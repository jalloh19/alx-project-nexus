"""
Core models - Abstract base models for other apps.
"""
from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base model with timestamp fields."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']


class SoftDeleteModel(models.Model):
    """Abstract base model with soft delete capability."""

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class BaseModel(TimeStampedModel):
    """Base model combining timestamp functionality."""

    class Meta:
        abstract = True
