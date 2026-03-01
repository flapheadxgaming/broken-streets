# systems/app_registry.py
# App-Registry for the Mobile OS.
# Keeps a catalogue of all installed apps, manages their lifecycle
# (launch, minimize, resume, close) and supports multitasking by
# maintaining a stack of "running" app instances.

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AppDescriptor:
    """
    Static metadata for an installed app.

    Attributes
    ----------
    app_id      : Unique string identifier, e.g. ``"calculator"``.
    display_name: Human-readable name shown on the launcher.
    icon_path   : Relative path to the app icon (resolved by ResourceManager).
    entry_class : The Kivy Widget/Screen class that implements the app.
    """
    app_id: str
    display_name: str
    icon_path: str
    entry_class: type


@dataclass
class RunningApp:
    """
    Represents one live instance of an app.

    Attributes
    ----------
    descriptor  : Reference to the AppDescriptor.
    widget      : The instantiated Kivy widget for this app session.
    is_visible  : Whether the app is currently in the foreground.
    """
    descriptor: AppDescriptor
    widget: object                  # kivy.uix.widget.Widget
    is_visible: bool = True


class AppRegistry:
    """
    Central catalogue and lifecycle manager for all OS apps.

    Usage
    -----
    registry = AppRegistry()
    registry.install(AppDescriptor("calc", "Calculator", "icons/calc.png", CalculatorApp))
    widget = registry.launch("calc")
    registry.minimize("calc")
    registry.resume("calc")
    registry.close("calc")
    """

    def __init__(self, event_loop=None):
        # Installed apps: app_id -> AppDescriptor
        self._installed: dict[str, AppDescriptor] = {}
        # Currently running apps: app_id -> RunningApp
        self._running: dict[str, RunningApp] = {}
        # Optional event loop for emitting lifecycle events
        self._event_loop = event_loop

    # ------------------------------------------------------------------
    # Installation
    # ------------------------------------------------------------------

    def install(self, descriptor: AppDescriptor) -> None:
        """Register an app so it is available for launch."""
        self._installed[descriptor.app_id] = descriptor

    def uninstall(self, app_id: str) -> None:
        """Remove an app from the registry; closes it first if running."""
        if app_id in self._running:
            self.close(app_id)
        self._installed.pop(app_id, None)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def launch(self, app_id: str) -> Optional[object]:
        """
        Instantiate and start an app.

        If the app is already running it is simply brought to the foreground.
        Returns the app's root widget, or *None* if the app is not installed.
        """
        if app_id not in self._installed:
            return None
        if app_id in self._running:
            self.resume(app_id)
            return self._running[app_id].widget
        descriptor = self._installed[app_id]
        widget = descriptor.entry_class()
        running = RunningApp(descriptor=descriptor, widget=widget, is_visible=True)
        self._running[app_id] = running
        self._emit("app_launched", app_id, widget)
        return widget

    def minimize(self, app_id: str) -> None:
        """Send app to the background (keep it alive but hide it)."""
        running = self._running.get(app_id)
        if running:
            running.is_visible = False
            self._emit("app_minimized", app_id)

    def resume(self, app_id: str) -> None:
        """Bring a minimized app back to the foreground."""
        running = self._running.get(app_id)
        if running:
            running.is_visible = True
            self._emit("app_resumed", app_id, running.widget)

    def close(self, app_id: str) -> None:
        """Terminate an app and release its resources."""
        running = self._running.pop(app_id, None)
        if running:
            self._emit("app_closed", app_id)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_installed(self) -> list[AppDescriptor]:
        """Return a list of all installed AppDescriptors."""
        return list(self._installed.values())

    def get_running(self) -> list[RunningApp]:
        """Return a list of all currently running apps."""
        return list(self._running.values())

    def is_running(self, app_id: str) -> bool:
        return app_id in self._running

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _emit(self, event: str, *args) -> None:
        if self._event_loop:
            self._event_loop.emit(event, *args)
