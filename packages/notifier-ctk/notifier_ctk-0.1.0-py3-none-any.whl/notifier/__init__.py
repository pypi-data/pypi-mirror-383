
from .core import Notifier

__all__ = ["Notifier"]

def show_notification(**kwargs):
    """Convenience function to quickly show a notification."""
    Notifier(**kwargs).show()
