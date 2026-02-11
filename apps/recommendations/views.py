"""Recommendation views."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Recommendation
from .serializers import RecommendationSerializer
from .services.recommendation_engine import RecommendationEngine
from apps.movies.serializers import MovieListSerializer


@extend_schema_view(
    list=extend_schema(tags=['Recommendations'], summary='Get user recommendations'),
)
class RecommendationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for movie recommendations."""
    serializer_class = RecommendationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Recommendation.objects.filter(
            user=self.request.user
        ).select_related('movie').order_by('-score', '-created_at')

    def list(self, request, *args, **kwargs):
        """Get recommendations for user."""
        # Check if we have recent recommendations
        existing_recs = self.get_queryset()

        if not existing_recs.exists():
            # Generate new recommendations
            engine = RecommendationEngine(request.user)
            engine.generate_recommendations(limit=20)
            existing_recs = self.get_queryset()

        serializer = self.get_serializer(existing_recs, many=True)
        return Response(serializer.data)

    @extend_schema(
        tags=['Recommendations'],
        summary='Refresh recommendations',
        responses={200: RecommendationSerializer(many=True)}
    )
    @action(detail=False, methods=['post'])
    def refresh(self, request):
        """Force refresh recommendations."""
        engine = RecommendationEngine(request.user)
        engine.generate_recommendations(limit=20)

        recommendations = self.get_queryset()
        serializer = self.get_serializer(recommendations, many=True)

        return Response({
            'message': f'Generated {recommendations.count()} recommendations',
            'recommendations': serializer.data
        })

    @extend_schema(
        tags=['Recommendations'],
        summary='Get similar movies',
        responses={200: MovieListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], url_path='similar/(?P<movie_id>[^/.]+)')
    def similar(self, request, movie_id=None):
        """Get movies similar to a specific movie."""
        engine = RecommendationEngine(request.user)
        similar_movies = engine.get_similar_movies(movie_id, limit=10)

        serializer = MovieListSerializer(similar_movies, many=True)
        return Response(serializer.data)

