# systems/notification_manager.py
# Notification system for the Mobile OS.
# Supports three display styles:
#   - Banner  : a slim bar that slides in from the top for ~3 seconds.
#   - Popup   : a modal card that requires user dismissal.
#   - Silent  : stored only in the notification tray, no UI interruption.
#
# Integrates with the EventLoop so other subsystems can react to
# notification events (e.g. play a sound on "notification_shown").

from dataclasses import dataclass, field
from enum import Enum, auto
from kivy.clock import Clock


class NotificationStyle(Enum):
    BANNER = auto()
    POPUP  = auto()
    SILENT = auto()


@dataclass
class Notification:
    """Represents a single notification."""
    notif_id: str
    title: str
    body: str
    style: NotificationStyle = NotificationStyle.BANNER
    # Icon relative path (resolved by ResourceManager)
    icon_path: str = "icons/notification_default.png"
    # Auto-dismiss delay in seconds (None = manual dismiss)
    auto_dismiss: float | None = 3.0


class NotificationManager:
    """
    Creates, displays and dismisses OS notifications.

    Usage
    -----
    nm = NotificationManager(event_loop, ui_root)
    nm.show(Notification("n1", "Battery Low", "Charge your device soon!",
                         NotificationStyle.BANNER))
    nm.dismiss("n1")
    """

    def __init__(self, event_loop=None, ui_root=None):
        self._event_loop = event_loop
        # The Kivy widget that notifications are added to
        self._ui_root = ui_root
        # All active (undismissed) notifications: notif_id -> Notification
        self._active: dict[str, Notification] = {}
        # All notifications ever shown (tray history)
        self._history: list[Notification] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def show(self, notification: Notification) -> None:
        """Display a notification according to its style."""
        self._active[notification.notif_id] = notification
        self._history.append(notification)
        if notification.style == NotificationStyle.BANNER:
            self._show_banner(notification)
        elif notification.style == NotificationStyle.POPUP:
            self._show_popup(notification)
        # SILENT notifications are stored but not rendered
        self._emit("notification_shown", notification)

    def dismiss(self, notif_id: str) -> None:
        """Dismiss a notification by ID."""
        notif = self._active.pop(notif_id, None)
        if notif:
            self._emit("notification_dismissed", notif)

    def get_history(self) -> list[Notification]:
        """Return all past notifications (tray contents)."""
        return list(self._history)

    def clear_history(self) -> None:
        """Clear the notification tray history."""
        self._history.clear()

    # ------------------------------------------------------------------
    # Rendering helpers (placeholders – wired up to real widgets in UI layer)
    # ------------------------------------------------------------------

    def _show_banner(self, notification: Notification) -> None:
        """
        Slide a banner widget in from the top of the screen.
        The actual Kivy widget is built in ui/homescreen.py;
        here we emit an event so the UI layer can react.
        """
        self._emit("banner_show", notification)
        if notification.auto_dismiss is not None:
            Clock.schedule_once(
                lambda dt, nid=notification.notif_id: self.dismiss(nid),
                notification.auto_dismiss,
            )

    def _show_popup(self, notification: Notification) -> None:
        """Emit an event so the UI layer can build a modal popup."""
        self._emit("popup_show", notification)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _emit(self, event: str, *args) -> None:
        if self._event_loop:
            self._event_loop.emit(event, *args)
