"""Recommendation engine service."""
from django.db.models import Avg, Count, Q
from apps.movies.models import Movie
from apps.favorites.models import Favorite, Rating
from apps.recommendations.models import Recommendation
import random


class RecommendationEngine:
    """Service for generating movie recommendations."""

    def __init__(self, user):
        self.user = user

    def generate_recommendations(self, limit=20):
        """Generate personalized recommendations for user."""
        recommendations = []

        # Get user's favorites and ratings
        user_favorites = Favorite.objects.filter(user=self.user).values_list('movie_id', flat=True)
        user_ratings = Rating.objects.filter(user=self.user, rating__gte=7).values_list('movie_id', flat=True)

        # Combine favorites and highly rated movies
        liked_movies = set(list(user_favorites) + list(user_ratings))

        if liked_movies:
            # Get genres from liked movies
            liked_genres = Movie.objects.filter(
                id__in=liked_movies
            ).values_list('genres__id', flat=True).distinct()

            # Genre-based recommendations
            genre_recommendations = self._get_genre_based_recommendations(
                liked_genres,
                exclude_movies=liked_movies,
                limit=limit
            )
            recommendations.extend(genre_recommendations)

        # If not enough recommendations, add popular movies
        if len(recommendations) < limit:
            popular_recommendations = self._get_popular_recommendations(
                exclude_movies=liked_movies,
                limit=limit - len(recommendations)
            )
            recommendations.extend(popular_recommendations)

        # Save recommendations to database
        self._save_recommendations(recommendations)

        return recommendations[:limit]

    def _get_genre_based_recommendations(self, genre_ids, exclude_movies, limit=20):
        """Get recommendations based on genres."""
        movies = Movie.objects.filter(
            genres__id__in=genre_ids
        ).exclude(
            id__in=exclude_movies
        ).annotate(
            genre_match_count=Count('genres', filter=Q(genres__id__in=genre_ids))
        ).order_by('-genre_match_count', '-vote_average', '-popularity')[:limit * 2]

        recommendations = []
        for movie in movies:
            recommendations.append({
                'movie': movie,
                'score': min(movie.vote_average / 10.0, 1.0),
                'reason': 'Based on your favorite genres'
            })

        return recommendations[:limit]

    def _get_popular_recommendations(self, exclude_movies, limit=10):
        """Get popular movie recommendations."""
        movies = Movie.objects.exclude(
            id__in=exclude_movies
        ).filter(
            vote_count__gte=100
        ).order_by('-popularity', '-vote_average')[:limit]

        recommendations = []
        for movie in movies:
            recommendations.append({
                'movie': movie,
                'score': min(movie.popularity / 1000.0, 1.0),
                'reason': 'Popular movies you might like'
            })

        return recommendations

    def _save_recommendations(self, recommendations):
        """Save recommendations to database."""
        # Clear old recommendations
        Recommendation.objects.filter(user=self.user).delete()

        # Save new recommendations
        recommendation_objects = [
            Recommendation(
                user=self.user,
                movie=rec['movie'],
                score=rec['score'],
                reason=rec['reason']
            )
            for rec in recommendations
        ]

        Recommendation.objects.bulk_create(recommendation_objects)

    def get_similar_movies(self, movie_id, limit=10):
        """Get movies similar to a given movie."""
        try:
            movie = Movie.objects.get(id=movie_id)
            genre_ids = movie.genres.values_list('id', flat=True)

            similar_movies = Movie.objects.filter(
                genres__id__in=genre_ids
            ).exclude(
                id=movie_id
            ).annotate(
                genre_match_count=Count('genres', filter=Q(genres__id__in=genre_ids))
            ).order_by('-genre_match_count', '-vote_average')[:limit]

            return similar_movies
        except Movie.DoesNotExist:
            return Movie.objects.none()
