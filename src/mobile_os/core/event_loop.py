# core/event_loop.py
# Central event loop for the Mobile OS.
# Manages the Kivy application lifecycle, dispatches OS-level events,
# and coordinates all subsystems each frame.

from kivy.app import App
from kivy.clock import Clock


class EventLoop:
    """
    The heart of the OS runtime.

    Responsibilities
    ----------------
    - Start and stop the Kivy main loop.
    - Register/unregister per-frame listeners (tick callbacks).
    - Emit OS-level named events (e.g. 'app_open', 'theme_changed').
    - Provide a clean shutdown path for background tasks.
    """

    def __init__(self):
        # Mapping of event-name -> list of callables
        self._listeners: dict[str, list] = {}
        # Kivy Clock event handle for the main tick
        self._tick_event = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self, fps: int = 60) -> None:
        """Schedule the OS tick at *fps* frames per second."""
        self._tick_event = Clock.schedule_interval(self._tick, 1.0 / fps)

    def stop(self) -> None:
        """Cancel the OS tick and clean up listeners."""
        if self._tick_event:
            self._tick_event.cancel()
            self._tick_event = None
        self._listeners.clear()

    # ------------------------------------------------------------------
    # Per-frame callback
    # ------------------------------------------------------------------

    def _tick(self, dt: float) -> None:
        """Called every frame by Kivy Clock. *dt* is seconds since last tick."""
        self.emit("tick", dt)

    # ------------------------------------------------------------------
    # Event bus
    # ------------------------------------------------------------------

    def on(self, event_name: str, callback) -> None:
        """Register *callback* to be called when *event_name* is emitted."""
        self._listeners.setdefault(event_name, []).append(callback)

    def off(self, event_name: str, callback) -> None:
        """Unregister a previously registered *callback*."""
        listeners = self._listeners.get(event_name, [])
        if callback in listeners:
            listeners.remove(callback)

    def emit(self, event_name: str, *args, **kwargs) -> None:
        """Fire *event_name*, passing *args*/*kwargs* to every registered listener."""
        for cb in list(self._listeners.get(event_name, [])):
            cb(*args, **kwargs)
