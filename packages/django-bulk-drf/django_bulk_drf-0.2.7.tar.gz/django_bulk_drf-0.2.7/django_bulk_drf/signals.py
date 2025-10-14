"""
Signal dispatch for bulk operations.

Provides optional signal dispatch after bulk operations.
Disabled by default for performance.
"""

from django.dispatch import Signal
from django.db.models.signals import post_save
import logging


logger = logging.getLogger(__name__)


# Bulk operation signals
post_bulk_create = Signal()
post_bulk_update = Signal()
post_bulk_upsert = Signal()
post_bulk_delete = Signal()


class BulkSignalDispatcher:
    """
    Dispatches signals after bulk operations.
    Disabled by default for performance.
    """

    def __init__(self, enabled=False, dispatch_individual=False):
        """
        Initialize with enabled flag.

        Args:
            enabled: Whether to dispatch bulk signals
            dispatch_individual: Whether to dispatch individual post_save/post_delete signals
        """
        self.enabled = enabled
        self.dispatch_individual = dispatch_individual

    def send_post_bulk_create(self, sender, instances, **kwargs):
        """
        Send post_bulk_create signal.

        Args:
            sender: Model class
            instances: List of created instances
            **kwargs: Additional signal arguments
        """
        if not self.enabled:
            return

        logger.debug(f"Dispatching post_bulk_create for {len(instances)} {sender.__name__} instances")

        post_bulk_create.send(sender=sender, instances=instances, **kwargs)

        # Optionally dispatch individual signals
        if self.dispatch_individual:
            self.dispatch_individual_signals(post_save, sender, instances, created=True)

    def send_post_bulk_update(self, sender, instances, **kwargs):
        """
        Send post_bulk_update signal.

        Args:
            sender: Model class
            instances: List of updated instances
            **kwargs: Additional signal arguments
        """
        if not self.enabled:
            return

        logger.debug(f"Dispatching post_bulk_update for {len(instances)} {sender.__name__} instances")

        post_bulk_update.send(sender=sender, instances=instances, **kwargs)

        # Optionally dispatch individual signals
        if self.dispatch_individual:
            self.dispatch_individual_signals(post_save, sender, instances, created=False)

    def send_post_bulk_upsert(self, sender, created_instances, updated_instances, **kwargs):
        """
        Send post_bulk_upsert signal.

        Args:
            sender: Model class
            created_instances: List of created instances
            updated_instances: List of updated instances
            **kwargs: Additional signal arguments
        """
        if not self.enabled:
            return

        total = len(created_instances) + len(updated_instances)
        logger.debug(
            f"Dispatching post_bulk_upsert for {total} {sender.__name__} instances "
            f"({len(created_instances)} created, {len(updated_instances)} updated)"
        )

        post_bulk_upsert.send(sender=sender, created_instances=created_instances, updated_instances=updated_instances, **kwargs)

        # Optionally dispatch individual signals
        if self.dispatch_individual:
            if created_instances:
                self.dispatch_individual_signals(post_save, sender, created_instances, created=True)
            if updated_instances:
                self.dispatch_individual_signals(post_save, sender, updated_instances, created=False)

    def send_post_bulk_delete(self, sender, count, filters=None, **kwargs):
        """
        Send post_bulk_delete signal.

        Args:
            sender: Model class
            count: Number of deleted records
            filters: Dict of filters used for deletion
            **kwargs: Additional signal arguments
        """
        if not self.enabled:
            return

        logger.debug(f"Dispatching post_bulk_delete for {count} {sender.__name__} instances")

        post_bulk_delete.send(sender=sender, count=count, filters=filters or {}, **kwargs)

    def dispatch_individual_signals(self, signal, sender, instances, **signal_kwargs):
        """
        Optionally dispatch individual post_save/post_delete signals.
        Very slow - only enable if required by existing code.

        Args:
            signal: Signal to dispatch (post_save or post_delete)
            sender: Model class
            instances: List of instances
            **signal_kwargs: Additional signal arguments
        """
        if not self.dispatch_individual:
            return

        logger.warning(
            f"Dispatching individual {signal} signals for {len(instances)} instances - "
            f"this is slow and should only be used if absolutely necessary"
        )

        for instance in instances:
            signal.send(sender=sender, instance=instance, **signal_kwargs)


# Global dispatcher instance
_global_dispatcher = None


def get_dispatcher(enabled=None, dispatch_individual=False):
    """
    Get global signal dispatcher instance.

    Args:
        enabled: Override enabled state (uses settings if None)
        dispatch_individual: Whether to dispatch individual signals

    Returns:
        BulkSignalDispatcher instance
    """
    global _global_dispatcher

    if _global_dispatcher is None:
        if enabled is None:
            from .settings import bulk_settings

            enabled = bulk_settings.signal_dispatch

        _global_dispatcher = BulkSignalDispatcher(enabled=enabled, dispatch_individual=dispatch_individual)

    return _global_dispatcher


def reset_dispatcher():
    """Reset global dispatcher instance."""
    global _global_dispatcher
    _global_dispatcher = None
