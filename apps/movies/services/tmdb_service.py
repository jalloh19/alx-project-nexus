"""
TMDb API service for fetching movie data.
"""
import logging
import requests
from datetime import datetime
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class TMDbService:
    """Service class for TMDb API interactions."""

    BASE_URL = settings.TMDB_BASE_URL
    IMAGE_BASE_URL = settings.TMDB_IMAGE_BASE_URL
    API_KEY = settings.TMDB_API_KEY

    def __init__(self):
        self.session = requests.Session()

    def _make_request(self, endpoint, params=None):
        """Make request to TMDb API."""
        if params is None:
            params = {}
        params['api_key'] = self.API_KEY

        url = f"{self.BASE_URL}/{endpoint}"
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"TMDb API Error: {e}")
            return None

    def get_trending_movies(self, time_window='day', page=1):
        """Get trending movies."""
        cache_key = f'tmdb_trending_{time_window}_{page}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data

        data = self._make_request(f'trending/movie/{time_window}', {'page': page})
        if data:
            cache.set(cache_key, data, 3600)  # Cache for 1 hour
        return data

    def search_movies(self, query, page=1):
        """Search for movies."""
        return self._make_request('search/movie', {'query': query, 'page': page})

    def get_movie_details(self, movie_id):
        """Get detailed movie information."""
        cache_key = f'tmdb_movie_{movie_id}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data

        data = self._make_request(
            f'movie/{movie_id}',
            {'append_to_response': 'credits,videos,recommendations'}
        )
        if data:
            cache.set(cache_key, data, 86400)  # Cache for 24 hours
        return data

    def get_genres(self):
        """Get list of movie genres."""
        cache_key = 'tmdb_genres'
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data

        data = self._make_request('genre/movie/list')
        if data and 'genres' in data:
            cache.set(cache_key, data['genres'], 604800)  # Cache for 1 week
            return data['genres']
        return []

    def discover_movies(self, **filters):
        """Discover movies with filters."""
        return self._make_request('discover/movie', filters)

    def get_popular_movies(self, page=1):
        """Get popular movies."""
        return self._make_request('movie/popular', {'page': page})

    def get_top_rated_movies(self, page=1):
        """Get top rated movies."""
        return self._make_request('movie/top_rated', {'page': page})

    @staticmethod
    def get_poster_url(poster_path, size='w500'):
        """Get full poster URL."""
        if not poster_path:
            return None
        return f"{TMDbService.IMAGE_BASE_URL}/{size}{poster_path}"

    @staticmethod
    def get_backdrop_url(backdrop_path, size='w1280'):
        """Get full backdrop URL."""
        if not backdrop_path:
            return None
        return f"{TMDbService.IMAGE_BASE_URL}/{size}{backdrop_path}"

    # ------------------------------------------------------------------
    # Persistence helpers – save TMDb JSON results into local DB
    # ------------------------------------------------------------------

    @staticmethod
    def persist_tmdb_movies(results):
        """
        Upsert a list of TMDb movie dicts into the local Movie table.

        Accepts the 'results' array from any TMDb list endpoint
        (trending, popular, top_rated, search, discover).
        Returns the number of movies created or updated.
        """
        from apps.movies.models import Movie, Genre  # local import to avoid circular

        if not results:
            return 0

        saved = 0
        for item in results:
            tmdb_id = item.get('id')
            if not tmdb_id:
                continue

            # Parse release_date safely
            release_date = None
            raw_date = item.get('release_date', '')
            if raw_date:
                try:
                    release_date = datetime.strptime(raw_date, '%Y-%m-%d').date()
                except (ValueError, TypeError):
                    pass

            defaults = {
                'title': item.get('title', item.get('name', '')),
                'original_title': item.get('original_title', ''),
                'overview': item.get('overview', ''),
                'release_date': release_date,
                'vote_average': item.get('vote_average', 0.0),
                'vote_count': item.get('vote_count', 0),
                'popularity': item.get('popularity', 0.0),
                'poster_path': item.get('poster_path'),
                'backdrop_path': item.get('backdrop_path'),
                'original_language': item.get('original_language', 'en'),
                'adult': item.get('adult', False),
            }

            try:
                movie, _created = Movie.objects.update_or_create(
                    tmdb_id=tmdb_id,
                    defaults=defaults,
                )

                # Handle genre M2M via genre_ids from TMDb
                genre_ids = item.get('genre_ids', [])
                if genre_ids:
                    genres = Genre.objects.filter(tmdb_id__in=genre_ids)
                    if genres.exists():
                        movie.genres.set(genres)

                saved += 1
            except Exception as exc:
                logger.warning("Failed to persist tmdb_id=%s: %s", tmdb_id, exc)

        logger.info("Persisted %d/%d TMDb movies to DB", saved, len(results))
        return saved

    @staticmethod
    def persist_tmdb_movie_detail(data):
        """
        Upsert a single detailed TMDb movie dict (from /movie/{id}).

        Handles the richer payload that includes runtime, budget, revenue,
        tagline, status, imdb_id, homepage, and nested genre objects.
        """
        from apps.movies.models import Movie, Genre

        if not data or 'id' not in data:
            return None

        release_date = None
        raw_date = data.get('release_date', '')
        if raw_date:
            try:
                release_date = datetime.strptime(raw_date, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                pass

        defaults = {
            'title': data.get('title', ''),
            'original_title': data.get('original_title', ''),
            'overview': data.get('overview', ''),
            'tagline': data.get('tagline', ''),
            'release_date': release_date,
            'runtime': data.get('runtime'),
            'vote_average': data.get('vote_average', 0.0),
            'vote_count': data.get('vote_count', 0),
            'popularity': data.get('popularity', 0.0),
            'poster_path': data.get('poster_path'),
            'backdrop_path': data.get('backdrop_path'),
            'original_language': data.get('original_language', 'en'),
            'adult': data.get('adult', False),
            'status': data.get('status', ''),
            'budget': data.get('budget'),
            'revenue': data.get('revenue'),
            'homepage': data.get('homepage') or None,
            'imdb_id': data.get('imdb_id'),
        }

        try:
            movie, _created = Movie.objects.update_or_create(
                tmdb_id=data['id'],
                defaults=defaults,
            )

            # Detail endpoint returns full genre objects: [{"id": 28, "name": "Action"}, ...]
            genre_list = data.get('genres', [])
            if genre_list:
                genre_objs = []
                for g in genre_list:
                    obj, _ = Genre.objects.get_or_create(
                        tmdb_id=g['id'],
                        defaults={'name': g.get('name', '')}
                    )
                    genre_objs.append(obj)
                movie.genres.set(genre_objs)

            return movie
        except Exception as exc:
            logger.warning("Failed to persist movie detail tmdb_id=%s: %s", data['id'], exc)
            return None


# Singleton instance
tmdb_service = TMDbService()
