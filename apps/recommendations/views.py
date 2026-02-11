"""Recommendation views."""
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Recommendation, RecommendationFeedback
from .serializers import RecommendationSerializer, RecommendationFeedbackSerializer
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

    # ── Feedback actions ────────────────────────────────────────────
    @extend_schema(
        tags=['Recommendations'],
        summary='Submit feedback on a recommendation',
        request=RecommendationFeedbackSerializer,
        responses={201: RecommendationFeedbackSerializer},
    )
    @action(detail=False, methods=['post'])
    def feedback(self, request):
        """Submit like / dislike / not_interested feedback."""
        serializer = RecommendationFeedbackSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        tags=['Recommendations'],
        summary='Get all feedback from current user',
        responses={200: RecommendationFeedbackSerializer(many=True)},
    )
    @action(detail=False, methods=['get'], url_path='feedback/list')
    def feedback_list(self, request):
        """List all feedback entries for the current user."""
        feedbacks = RecommendationFeedback.objects.filter(
            user=request.user
        ).select_related('recommendation__movie').order_by('-created_at')

        serializer = RecommendationFeedbackSerializer(feedbacks, many=True)
        return Response(serializer.data)

