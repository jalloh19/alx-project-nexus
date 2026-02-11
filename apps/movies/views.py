"""Movie views and viewsets."""
import threading
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core.cache import cache
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Movie, Genre
from .serializers import (
    MovieListSerializer,
    MovieDetailSerializer,
    GenreSerializer,
    TMDbMovieSerializer
)
from .services.tmdb_service import tmdb_service, TMDbService


def _persist_in_background(results, detail=False):
    """Fire-and-forget persistence so API response isn't slowed down."""
    if detail:
        thread = threading.Thread(
            target=TMDbService.persist_tmdb_movie_detail, args=(results,), daemon=True
        )
    else:
        thread = threading.Thread(
            target=TMDbService.persist_tmdb_movies, args=(results,), daemon=True
        )
    thread.start()


@extend_schema_view(
    list=extend_schema(tags=['Movies'], summary='List movies from database'),
    retrieve=extend_schema(tags=['Movies'], summary='Get movie details'),
)
class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for movies stored in database."""
    queryset = Movie.objects.prefetch_related('genres').all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MovieDetailSerializer
        return MovieListSerializer

    @extend_schema(
        tags=['Movies'],
        summary='Get trending movies from TMDb',
        responses={200: TMDbMovieSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def trending(self, request):
        """Get trending movies from TMDb."""
        time_window = request.query_params.get('time_window', 'day')
        page = request.query_params.get('page', 1)

        data = tmdb_service.get_trending_movies(time_window, page)
        if data and 'results' in data:
            # Persist to DB in background so recommendation engine has data
            _persist_in_background(data['results'])

            serializer = TMDbMovieSerializer(data['results'], many=True)
            return Response({
                'results': serializer.data,
                'page': data.get('page', 1),
                'total_pages': data.get('total_pages', 1),
                'total_results': data.get('total_results', 0)
            })
        return Response({'results': [], 'page': 1, 'total_pages': 0, 'total_results': 0})

    @extend_schema(
        tags=['Movies'],
        summary='Search movies on TMDb',
        responses={200: TMDbMovieSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search movies on TMDb."""
        query = request.query_params.get('q') or request.query_params.get('query', '')
        page = request.query_params.get('page', 1)

        if not query:
            return Response({'error': 'Query parameter "q" or "query" is required'},
                          status=status.HTTP_400_BAD_REQUEST)

        data = tmdb_service.search_movies(query, page)
        if data and 'results' in data:
            _persist_in_background(data['results'])

            serializer = TMDbMovieSerializer(data['results'], many=True)
            return Response({
                'results': serializer.data,
                'page': data.get('page', 1),
                'total_pages': data.get('total_pages', 1),
                'total_results': data.get('total_results', 0)
            })
        return Response({'results': [], 'page': 1, 'total_pages': 0, 'total_results': 0})

    @extend_schema(
        tags=['Movies'],
        summary='Get popular movies from TMDb',
        responses={200: TMDbMovieSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get popular movies."""
        page = request.query_params.get('page', 1)
        data = tmdb_service.get_popular_movies(page)

        if data and 'results' in data:
            _persist_in_background(data['results'])

            serializer = TMDbMovieSerializer(data['results'], many=True)
            return Response({
                'results': serializer.data,
                'page': data.get('page', 1),
                'total_pages': data.get('total_pages', 1),
                'total_results': data.get('total_results', 0)
            })
        return Response({'results': [], 'page': 1, 'total_pages': 0, 'total_results': 0})

    @extend_schema(
        tags=['Movies'],
        summary='Get top rated movies from TMDb',
        responses={200: TMDbMovieSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def top_rated(self, request):
        """Get top rated movies."""
        page = request.query_params.get('page', 1)
        data = tmdb_service.get_top_rated_movies(page)

        if data and 'results' in data:
            _persist_in_background(data['results'])

            serializer = TMDbMovieSerializer(data['results'], many=True)
            return Response({
                'results': serializer.data,
                'page': data.get('page', 1),
                'total_pages': data.get('total_pages', 1),
                'total_results': data.get('total_results', 0)
            })
        return Response({'results': [], 'page': 1, 'total_pages': 0, 'total_results': 0})

    @extend_schema(
        tags=['Movies'],
        summary='Get movie details from TMDb by ID',
        responses={200: TMDbMovieSerializer}
    )
    @action(detail=False, methods=['get'], url_path='tmdb/(?P<tmdb_id>[^/.]+)')
    def tmdb_detail(self, request, tmdb_id=None):
        """Get movie details from TMDb."""
        data = tmdb_service.get_movie_details(tmdb_id)
        if data:
            _persist_in_background(data, detail=True)
            return Response(data)
        return Response({'error': 'Movie not found'}, status=status.HTTP_404_NOT_FOUND)


@extend_schema_view(
    list=extend_schema(tags=['Genres'], summary='List all genres'),
)
class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for movie genres."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Genres'],
        summary='Sync genres from TMDb',
        responses={200: GenreSerializer(many=True)}
    )
    @action(detail=False, methods=['post'])
    def sync(self, request):
        """Sync genres from TMDb API."""
        genres_data = tmdb_service.get_genres()
        created_count = 0

        for genre_data in genres_data:
            genre, created = Genre.objects.update_or_create(
                tmdb_id=genre_data['id'],
                defaults={'name': genre_data['name']}
            )
            if created:
                created_count += 1

        return Response({
            'message': f'Synced {len(genres_data)} genres ({created_count} new)',
            'genres': GenreSerializer(Genre.objects.all(), many=True).data
        })

