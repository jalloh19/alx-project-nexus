"""Favorites and ratings serializers."""
from rest_framework import serializers
from .models import Favorite, Rating
from apps.movies.serializers import MovieListSerializer


class FavoriteSerializer(serializers.ModelSerializer):
    """Serializer for favorites."""
    movie_detail = MovieListSerializer(source='movie', read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'movie', 'movie_detail', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class RatingSerializer(serializers.ModelSerializer):
    """Serializer for ratings."""
    movie_detail = MovieListSerializer(source='movie', read_only=True)

    class Meta:
        model = Rating
        fields = ['id', 'movie', 'movie_detail', 'rating', 'review', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_rating(self, value):
        if not (1 <= value <= 10):
            raise serializers.ValidationError("Rating must be between 1 and 10.")
        return value

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        # Update or create rating
        rating, created = Rating.objects.update_or_create(
            user=validated_data['user'],
            movie=validated_data['movie'],
            defaults={
                'rating': validated_data['rating'],
                'review': validated_data.get('review', '')
            }
        )
        return rating
