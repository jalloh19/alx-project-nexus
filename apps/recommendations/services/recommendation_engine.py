"""
Recommendation engine service.

Generates personalized movie recommendations using a multi-signal
content-based approach:

  1. **Genre affinity** — weighted genre overlap between a candidate movie
     and the user's taste profile (built from favourites + high ratings).
  2. **Popularity signal** — log-scaled TMDb popularity so blockbusters
     get a gentle nudge but don't dominate.
  3. **Quality signal** — TMDb vote_average normalized to [0, 1].
  4. **Recency boost** — movies released in the last 2 years get a small
     bonus to keep the feed fresh.
  5. **Collaborative signal** — if other users with similar genre taste
     also liked a movie, it gets an extra boost.
  6. **Diversity pass** — after scoring, the final list is re-ranked to
     avoid genre monotony (no more than 3 consecutive same-top-genre).

All computation uses plain Python / Django ORM — no numpy or scikit-learn
required, so it works on the free Render tier without heavy deps.
"""
import logging
import math
from collections import Counter, defaultdict
from datetime import date

from django.db.models import Count, Q

from apps.favorites.models import Favorite, Rating
from apps.movies.models import Movie
from apps.recommendations.models import Recommendation, RecommendationFeedback

logger = logging.getLogger(__name__)

# ── Tunable weights ──────────────────────────────────────────────────
WEIGHT_GENRE = 0.45
WEIGHT_POPULARITY = 0.15
WEIGHT_QUALITY = 0.20
WEIGHT_RECENCY = 0.10
WEIGHT_COLLABORATIVE = 0.10

HIGH_RATING_THRESHOLD = 7  # on a 1-10 scale
RECENCY_WINDOW_DAYS = 730  # 2 years


class RecommendationEngine:
    """Service for generating movie recommendations."""

    def __init__(self, user):
        self.user = user
        # Lazily computed
        self._liked_movie_ids = None
        self._genre_profile = None  # {genre_id: weight}

    # ==================================================================
    # Public API
    # ==================================================================

    def generate_recommendations(self, limit=20):
        """Generate personalised recommendations and persist them."""
        liked_ids = self._get_liked_movie_ids()

        # Build the user's genre taste profile
        genre_profile = self._build_genre_profile(liked_ids)

        # Also collect IDs the user has dismissed / disliked
        dismissed_ids = self._get_dismissed_movie_ids()
        exclude_ids = liked_ids | dismissed_ids

        # Score every candidate movie
        candidates = (
            Movie.objects
            .exclude(id__in=exclude_ids)
            .prefetch_related('genres')
            .filter(vote_count__gte=10)  # skip very obscure entries
        )

        scored = []
        collab_boost = self._collaborative_boost_map(genre_profile)

        for movie in candidates.iterator(chunk_size=500):
            score, reason = self._score_movie(movie, genre_profile, collab_boost)
            if score > 0:
                scored.append({
                    'movie': movie,
                    'score': score,
                    'reason': reason,
                    'rec_type': 'content_based' if genre_profile else 'trending',
                })

        # Sort descending by score
        scored.sort(key=lambda x: x['score'], reverse=True)

        # Diversity re-ranking: limit genre repetition in the top N
        final = self._diversify(scored, limit)

        # If not enough personalised recs, pad with popular movies
        if len(final) < limit:
            filler = self._get_popular_filler(
                exclude_ids | {r['movie'].id for r in final},
                limit - len(final),
            )
            final.extend(filler)

        # Persist
        self._save_recommendations(final)

        return final[:limit]

    def get_similar_movies(self, movie_id, limit=10):
        """Content-based similarity to a single movie."""
        try:
            movie = Movie.objects.prefetch_related('genres').get(id=movie_id)
        except Movie.DoesNotExist:
            return Movie.objects.none()

        genre_ids = set(movie.genres.values_list('id', flat=True))
        if not genre_ids:
            return Movie.objects.none()

        similar = (
            Movie.objects
            .filter(genres__id__in=genre_ids)
            .exclude(id=movie_id)
            .prefetch_related('genres')
            .distinct()
            .annotate(
                genre_match=Count('genres', filter=Q(genres__id__in=genre_ids))
            )
            .order_by('-genre_match', '-vote_average', '-popularity')
        )[:limit]

        return similar

    # ==================================================================
    # Scoring
    # ==================================================================

    def _score_movie(self, movie, genre_profile, collab_boost):
        """Return (score, reason) for a single candidate movie."""
        reasons = []

        # 1. Genre affinity
        genre_score = 0.0
        if genre_profile:
            movie_genre_ids = set(movie.genres.values_list('id', flat=True))
            overlap = movie_genre_ids & set(genre_profile.keys())
            if overlap:
                genre_score = sum(genre_profile[gid] for gid in overlap) / sum(genre_profile.values())
                reasons.append('Matches your favourite genres')

        # 2. Popularity (log-scaled, capped at 1.0)
        pop_score = min(math.log1p(movie.popularity) / 10.0, 1.0) if movie.popularity else 0.0

        # 3. Quality
        quality_score = min(movie.vote_average / 10.0, 1.0) if movie.vote_average else 0.0

        # 4. Recency boost
        recency_score = 0.0
        if movie.release_date:
            days_old = (date.today() - movie.release_date).days
            if days_old <= RECENCY_WINDOW_DAYS:
                recency_score = 1.0 - (days_old / RECENCY_WINDOW_DAYS)
                if recency_score > 0.5:
                    reasons.append('Recently released')

        # 5. Collaborative boost
        collab_score = collab_boost.get(movie.id, 0.0)
        if collab_score > 0.3:
            reasons.append('Liked by users with similar taste')

        # Weighted sum
        total = (
            WEIGHT_GENRE * genre_score
            + WEIGHT_POPULARITY * pop_score
            + WEIGHT_QUALITY * quality_score
            + WEIGHT_RECENCY * recency_score
            + WEIGHT_COLLABORATIVE * collab_score
        )

        reason = '; '.join(reasons) if reasons else 'Popular movie you might enjoy'
        return round(total, 4), reason

    # ==================================================================
    # Profile builders
    # ==================================================================

    def _get_liked_movie_ids(self):
        """Movie IDs the user has favourited or rated highly."""
        if self._liked_movie_ids is not None:
            return self._liked_movie_ids

        fav_ids = set(
            Favorite.objects.filter(user=self.user).values_list('movie_id', flat=True)
        )
        rated_ids = set(
            Rating.objects.filter(
                user=self.user, rating__gte=HIGH_RATING_THRESHOLD
            ).values_list('movie_id', flat=True)
        )
        self._liked_movie_ids = fav_ids | rated_ids
        return self._liked_movie_ids

    def _build_genre_profile(self, liked_movie_ids):
        """
        Build a weighted genre vector from liked movies.

        Genres that appear more often in the user's favourites / high-rated
        movies get a higher weight. Weights are normalised to [0, 1].
        """
        if self._genre_profile is not None:
            return self._genre_profile

        if not liked_movie_ids:
            self._genre_profile = {}
            return self._genre_profile

        # Count genre occurrences across liked movies
        genre_counts = Counter()
        for genre_id in (
            Movie.objects
            .filter(id__in=liked_movie_ids)
            .values_list('genres__id', flat=True)
        ):
            if genre_id is not None:
                genre_counts[genre_id] += 1

        if not genre_counts:
            self._genre_profile = {}
            return self._genre_profile

        # Normalise so the heaviest genre = 1.0
        max_count = max(genre_counts.values())
        self._genre_profile = {
            gid: count / max_count for gid, count in genre_counts.items()
        }
        return self._genre_profile

    def _collaborative_boost_map(self, genre_profile):
        """
        Simple collaborative signal: find other users who share the
        current user's top genres, then find movies *they* liked that
        this user hasn't seen.  Return {movie_id: score}.
        """
        if not genre_profile:
            return {}

        top_genre_ids = [
            gid for gid, w in sorted(genre_profile.items(), key=lambda x: -x[1])
        ][:5]

        if not top_genre_ids:
            return {}

        # Users who have favourited movies in the same top genres
        similar_users = (
            Favorite.objects
            .filter(movie__genres__id__in=top_genre_ids)
            .exclude(user=self.user)
            .values_list('user_id', flat=True)
            .distinct()
        )[:50]  # cap for performance

        if not similar_users:
            return {}

        # Movies those users liked
        boost_qs = (
            Favorite.objects
            .filter(user_id__in=similar_users)
            .values('movie_id')
            .annotate(fan_count=Count('id'))
            .order_by('-fan_count')
        )[:200]

        max_fans = max((r['fan_count'] for r in boost_qs), default=1)
        return {
            r['movie_id']: min(r['fan_count'] / max_fans, 1.0)
            for r in boost_qs
        }

    def _get_dismissed_movie_ids(self):
        """Movies the user has explicitly dismissed / disliked."""
        dismissed = set(
            RecommendationFeedback.objects
            .filter(
                user=self.user,
                feedback_type__in=['dislike', 'not_interested'],
            )
            .values_list('recommendation__movie_id', flat=True)
        )
        # Also exclude low-rated movies
        low_rated = set(
            Rating.objects.filter(
                user=self.user, rating__lt=4,
            ).values_list('movie_id', flat=True)
        )
        return dismissed | low_rated

    # ==================================================================
    # Post-processing
    # ==================================================================

    @staticmethod
    def _diversify(scored, limit):
        """
        Re-rank to avoid genre monotony.
        Allow at most 3 consecutive movies with the same top genre.
        """
        if not scored:
            return []

        result = []
        recent_genre = None
        streak_count = 0

        for item in scored:
            movie = item['movie']
            top_genre = None
            genre_ids = list(movie.genres.values_list('id', flat=True))
            if genre_ids:
                top_genre = genre_ids[0]

            if top_genre == recent_genre:
                streak_count += 1
                if streak_count > 3:
                    continue  # skip to break the streak
            else:
                streak_count = 1
                recent_genre = top_genre

            result.append(item)
            if len(result) >= limit:
                break

        return result

    def _get_popular_filler(self, exclude_ids, limit):
        """Fill remaining slots with globally popular movies."""
        movies = (
            Movie.objects
            .exclude(id__in=exclude_ids)
            .filter(vote_count__gte=50)
            .order_by('-popularity', '-vote_average')
        )[:limit]

        return [
            {
                'movie': m,
                'score': round(min(math.log1p(m.popularity) / 10.0, 1.0), 4),
                'reason': 'Popular movie you might enjoy',
                'rec_type': 'trending',
            }
            for m in movies
        ]

    # ==================================================================
    # Persistence
    # ==================================================================

    def _save_recommendations(self, recommendations):
        """Replace old recommendations with the new batch."""
        Recommendation.objects.filter(user=self.user).delete()

        objs = [
            Recommendation(
                user=self.user,
                movie=rec['movie'],
                recommendation_type=rec.get('rec_type', 'personalized'),
                score=rec['score'],
                reason=rec['reason'],
            )
            for rec in recommendations
        ]

        Recommendation.objects.bulk_create(objs, ignore_conflicts=True)
        logger.info(
            "Saved %d recommendations for user %s",
            len(objs), self.user.email,
        )
