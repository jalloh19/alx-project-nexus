"""Favorites and ratings views."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Favorite, Rating
from .serializers import FavoriteSerializer, RatingSerializer


@extend_schema_view(
    list=extend_schema(tags=['Favorites'], summary='List user favorites'),
    create=extend_schema(tags=['Favorites'], summary='Add movie to favorites'),
    destroy=extend_schema(tags=['Favorites'], summary='Remove from favorites'),
)
class FavoriteViewSet(viewsets.ModelViewSet):
    """ViewSet for user favorites."""
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related('movie')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Check if already favorited
        if Favorite.objects.filter(
            user=request.user,
            movie=serializer.validated_data['movie']
        ).exists():
            return Response(
                {'message': 'Movie already in favorites'},
                status=status.HTTP_400_BAD_REQUEST
            )

        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        tags=['Favorites'],
        summary='Check if movie is favorited',
        responses={200: {'type': 'object', 'properties': {'is_favorited': {'type': 'boolean'}}}}
    )
    @action(detail=False, methods=['get'], url_path='check/(?P<movie_id>[^/.]+)')
    def check(self, request, movie_id=None):
        """Check if a movie is in user's favorites."""
        is_favorited = Favorite.objects.filter(
            user=request.user,
            movie_id=movie_id
        ).exists()
        return Response({'is_favorited': is_favorited})


@extend_schema_view(
    list=extend_schema(tags=['Ratings'], summary='List user ratings'),
    create=extend_schema(tags=['Ratings'], summary='Rate a movie'),
    update=extend_schema(tags=['Ratings'], summary='Update rating'),
    destroy=extend_schema(tags=['Ratings'], summary='Delete rating'),
)
class RatingViewSet(viewsets.ModelViewSet):
    """ViewSet for movie ratings."""
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def get_queryset(self):
        return Rating.objects.filter(user=self.request.user).select_related('movie')

    @extend_schema(
        tags=['Ratings'],
        summary='Get user rating for a movie',
        responses={200: RatingSerializer}
    )
    @action(detail=False, methods=['get'], url_path='movie/(?P<movie_id>[^/.]+)')
    def get_movie_rating(self, request, movie_id=None):
        """Get user's rating for a specific movie."""
        try:
            rating = Rating.objects.get(user=request.user, movie_id=movie_id)
            serializer = self.get_serializer(rating)
            return Response(serializer.data)
        except Rating.DoesNotExist:
            return Response(
                {'message': 'No rating found for this movie'},
                status=status.HTTP_404_NOT_FOUND
            )

