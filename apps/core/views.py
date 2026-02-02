"""Core views - Health checks and utility endpoints."""
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.core.cache import cache
from django.db import connection


@require_GET
def health_check(request):
    """
    Health check endpoint for Kubernetes probes.
    Returns HTTP 200 if all systems are operational.
    """
    health_status = {
        'status': 'healthy',
        'database': False,
        'cache': False,
    }

    # Check database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        health_status['database'] = True
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['database_error'] = str(e)

    # Check Redis cache
    try:
        cache.set('health_check', 'ok', 10)
        cache_value = cache.get('health_check')
        health_status['cache'] = cache_value == 'ok'
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['cache_error'] = str(e)

    status_code = 200 if health_status['status'] == 'healthy' else 503
    return JsonResponse(health_status, status=status_code)


@require_GET
def readiness_check(request):
    """
    Readiness check for Kubernetes.
    Returns HTTP 200 when application is ready to serve traffic.
    """
    return JsonResponse({'status': 'ready'})


@require_GET
def liveness_check(request):
    """
    Liveness check for Kubernetes.
    Returns HTTP 200 if application is running.
    """
    return JsonResponse({'status': 'alive'})
