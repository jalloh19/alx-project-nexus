"""Recommendation serializers."""
from rest_framework import serializers
from .models import Recommendation
from apps.movies.serializers import MovieListSerializer


class RecommendationSerializer(serializers.ModelSerializer):
    """Serializer for recommendations."""
    movie_detail = MovieListSerializer(source='movie', read_only=True)

    class Meta:
        model = Recommendation
        fields = ['id', 'movie', 'movie_detail', 'score', 'reason', 'created_at']
        read_only_fields = ['id', 'created_at']
