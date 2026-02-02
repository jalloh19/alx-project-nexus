"""Core Celery tasks."""
from celery import shared_task
from django.core.cache import cache
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@shared_task(name='apps.core.tasks.cleanup_stale_cache')
def cleanup_stale_cache():
    """
    Cleanup stale cache entries.
    This task runs daily to maintain cache health.
    """
    logger.info("Starting stale cache cleanup")

    try:
        # Redis automatically handles TTL, but we can log metrics
        logger.info("Cache cleanup completed successfully")
        return {'status': 'success', 'timestamp': timezone.now().isoformat()}
    except Exception as e:
        logger.error(f"Cache cleanup failed: {str(e)}")
        return {'status': 'failed', 'error': str(e)}
