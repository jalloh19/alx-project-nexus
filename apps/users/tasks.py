"""User-related Celery tasks."""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task(name='apps.users.tasks.send_verification_email')
def send_verification_email(user_id: int, verification_token: str):
    """Send email verification link to user."""
    from .models import User

    try:
        user = User.objects.get(id=user_id)
        subject = 'Verify your email address'
        message = f'Click the link to verify your email: {verification_token}'

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info(f"Verification email sent to {user.email}")
        return {'status': 'success', 'email': user.email}
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        return {'status': 'failed', 'error': 'User not found'}
    except Exception as e:
        logger.error(f"Failed to send verification email: {str(e)}")
        return {'status': 'failed', 'error': str(e)}


@shared_task(name='apps.users.tasks.send_password_reset_email')
def send_password_reset_email(user_id: int, reset_token: str):
    """Send password reset link to user."""
    from .models import User

    try:
        user = User.objects.get(id=user_id)
        subject = 'Reset your password'
        message = f'Click the link to reset your password: {reset_token}'

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info(f"Password reset email sent to {user.email}")
        return {'status': 'success', 'email': user.email}
    except Exception as e:
        logger.error(f"Failed to send password reset email: {str(e)}")
        return {'status': 'failed', 'error': str(e)}
