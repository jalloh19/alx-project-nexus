"""Movie serializers for API endpoints."""
from rest_framework import serializers
from .models import Movie, Genre


class GenreSerializer(serializers.ModelSerializer):
    """Serializer for movie genres."""

    class Meta:
        model = Genre
        fields = ['id', 'tmdb_id', 'name']
        read_only_fields = ['id']


class MovieListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for movie lists."""
    poster_url = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = [
            'id', 'tmdb_id', 'title', 'release_date',
            'vote_average', 'popularity', 'poster_url'
        ]

    def get_poster_url(self, obj):
        """Get full poster URL."""
        from .services.tmdb_service import TMDbService
        return TMDbService.get_poster_url(obj.poster_path)


class MovieDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single movie."""
    genres = GenreSerializer(many=True, read_only=True)
    poster_url = serializers.SerializerMethodField()
    backdrop_url = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = [
            'id', 'tmdb_id', 'imdb_id', 'title', 'original_title',
            'overview', 'tagline', 'release_date', 'runtime', 'budget',
            'revenue', 'popularity', 'vote_average', 'vote_count',
            'status', 'poster_url', 'backdrop_url', 'genres', 'created_at'
        ]

    def get_poster_url(self, obj):
        from .services.tmdb_service import TMDbService
        return TMDbService.get_poster_url(obj.poster_path)

    def get_backdrop_url(self, obj):
        from .services.tmdb_service import TMDbService
        return TMDbService.get_backdrop_url(obj.backdrop_path)


class TMDbMovieSerializer(serializers.Serializer):
    """Serializer for TMDb API responses."""
    id = serializers.IntegerField()
    title = serializers.CharField()
    overview = serializers.CharField(allow_blank=True)
    release_date = serializers.CharField(allow_blank=True)
    poster_path = serializers.CharField(allow_null=True)
    backdrop_path = serializers.CharField(allow_null=True)
    vote_average = serializers.FloatField()
    vote_count = serializers.IntegerField()
    popularity = serializers.FloatField()
    adult = serializers.BooleanField()

    poster_url = serializers.SerializerMethodField()

    def get_poster_url(self, obj):
        from .services.tmdb_service import TMDbService
        return TMDbService.get_poster_url(obj.get('poster_path'))
