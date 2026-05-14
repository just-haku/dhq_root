from app.models.notification import Notification
import logging

logger = logging.getLogger(__name__)

async def send_notification(user_id: str, message: str, n_type: str = 'SYSTEM', link: str = None):
    """
    Send a notification to a specific user.
    """
    try:
        notif = Notification(
            user_id=user_id,
            message=message,
            type=n_type,
            link=link
        )
        notif.save()
        # Optionally trigger Socket.IO emit here in the future
        return True
    except Exception as e:
        logger.error(f"Failed to send notification to {user_id}: {e}")
        return False
