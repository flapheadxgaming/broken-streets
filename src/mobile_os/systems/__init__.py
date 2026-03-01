# systems/__init__.py
# Exports for the System Layer of the Mobile OS
from .app_registry import AppRegistry
from .notification_manager import NotificationManager
from .theme_engine import ThemeEngine

__all__ = ["AppRegistry", "NotificationManager", "ThemeEngine"]
