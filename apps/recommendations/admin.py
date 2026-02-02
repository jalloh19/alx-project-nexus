from django.contrib import admin
from .models import Recommendation, RecommendationFeedback


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ['movie', 'user', 'recommendation_type', 'score', 'is_clicked', 'is_rated', 'created_at']
    list_filter = ['recommendation_type', 'is_clicked', 'is_rated', 'created_at']
    search_fields = ['movie__title', 'user__email', 'reason']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-score', '-created_at']


@admin.register(RecommendationFeedback)
class RecommendationFeedbackAdmin(admin.ModelAdmin):
    list_display = ['user', 'recommendation', 'feedback_type', 'created_at']
    list_filter = ['feedback_type', 'created_at']
    search_fields = ['user__email', 'recommendation__movie__title', 'comment']
    readonly_fields = ['created_at', 'updated_at']
