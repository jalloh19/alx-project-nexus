"""Recommendation serializers."""
from rest_framework import serializers
from .models import Recommendation, RecommendationFeedback
from apps.movies.serializers import MovieListSerializer


class RecommendationSerializer(serializers.ModelSerializer):
    """Serializer for recommendations."""
    movie_detail = MovieListSerializer(source='movie', read_only=True)

    class Meta:
        model = Recommendation
        fields = [
            'id', 'movie', 'movie_detail', 'recommendation_type',
            'score', 'reason', 'is_clicked', 'is_rated', 'created_at',
        ]
        read_only_fields = ['id', 'recommendation_type', 'score', 'reason', 'created_at']


class RecommendationFeedbackSerializer(serializers.ModelSerializer):
    """Serializer for recommendation feedback (like / dislike / not interested)."""

    class Meta:
        model = RecommendationFeedback
        fields = ['id', 'recommendation', 'feedback_type', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_recommendation(self, value):
        """Ensure the recommendation belongs to the requesting user."""
        request = self.context.get('request')
        if request and value.user != request.user:
            raise serializers.ValidationError("You can only give feedback on your own recommendations.")
        return value

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        feedback, _ = RecommendationFeedback.objects.update_or_create(
            user=validated_data['user'],
            recommendation=validated_data['recommendation'],
            defaults={
                'feedback_type': validated_data['feedback_type'],
                'comment': validated_data.get('comment', ''),
            },
        )
        return feedback
