from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Post
from .tasks import send_bulk_post_notifications
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Post)
def notify_subscribers(sender, instance, created, **kwargs):
    if created:
        try:
            category = instance.category
            subscribers_dict = {}
            for subscriber in category.subscribers.all():
                if subscriber.email not in subscribers_dict:
                    subscribers_dict[subscriber.email] = {
                        'email': subscriber.email,
                        'username': subscriber.username,
                        'post_title': instance.title,
                        'post_text': instance.text,
                        'post_url': instance.get_absolute_url_with_domain()
                    }
            notifications_data = list(subscribers_dict.values())
            if notifications_data:
                try:
                    send_bulk_post_notifications.delay(notifications_data)
                except Exception as e:
                    logger.error(f"Celery task failed: {e}")
                    send_bulk_post_notifications(notifications_data)
        except Exception as e:
            logger.error(f"Error in notify_subscribers: {e}")
