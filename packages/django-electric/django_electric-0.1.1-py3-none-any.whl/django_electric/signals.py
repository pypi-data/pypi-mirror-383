"""Django signals for Electric SQL sync events."""

import logging
from django.dispatch import Signal, receiver
from django.db.models.signals import post_save, post_delete
from django.conf import settings

logger = logging.getLogger(__name__)

# Custom signals for Electric sync events
electric_sync_started = Signal()  # Fired when sync starts
electric_sync_completed = Signal()  # Fired when sync completes successfully
electric_sync_failed = Signal()  # Fired when sync fails
electric_data_received = Signal()  # Fired when data is received from Electric


def should_auto_sync(model_class) -> bool:
    """
    Check if a model should auto-sync.

    Args:
        model_class: Django model class

    Returns:
        True if auto-sync is enabled for this model
    """
    # Check global setting
    if not getattr(settings, "ELECTRIC_AUTO_SYNC", False):
        return False

    # Check model Meta
    return getattr(model_class._meta, "electric_sync", False)


@receiver(post_save)
def auto_sync_on_save(sender, instance, created, **kwargs):
    """
    Automatically sync model to Electric when saved.

    This signal handler is called after a model instance is saved.
    If auto-sync is enabled for the model, it will trigger a sync.
    """
    if not should_auto_sync(sender):
        return

    if not hasattr(sender, "electric_sync"):
        return

    try:
        logger.debug(f"Auto-syncing {sender.__name__} after save")
        # In a real implementation, this would push changes to Electric
        # For now, we just log the event
        electric_sync_started.send(sender=sender, instance=instance)

    except Exception as e:
        logger.error(f"Auto-sync failed for {sender.__name__}: {e}")
        electric_sync_failed.send(sender=sender, instance=instance, error=e)


@receiver(post_delete)
def auto_sync_on_delete(sender, instance, **kwargs):
    """
    Automatically sync model deletion to Electric.

    This signal handler is called after a model instance is deleted.
    """
    if not should_auto_sync(sender):
        return

    if not hasattr(sender, "electric_sync"):
        return

    try:
        logger.debug(f"Auto-syncing {sender.__name__} deletion")
        electric_sync_started.send(sender=sender, instance=instance, deleted=True)

    except Exception as e:
        logger.error(f"Auto-sync deletion failed for {sender.__name__}: {e}")
        electric_sync_failed.send(sender=sender, instance=instance, error=e)
