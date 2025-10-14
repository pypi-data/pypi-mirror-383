
from .core import Notifier

__all__ = ["Notifier"]

def notify(title, message, **kwargs):
    """Quick shorthand to display a notification."""
    Notifier(title=title, message=message, **kwargs).show()

