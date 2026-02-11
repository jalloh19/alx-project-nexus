"""
TMDb API service for fetching movie data.
"""
import requests
from django.conf import settings
from django.core.cache import cache


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


# Singleton instance
tmdb_service = TMDbService()
