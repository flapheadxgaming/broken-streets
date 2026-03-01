# core/input_handler.py
# Touch & gesture input handler for the Mobile OS.
# Wraps Kivy's touch events and translates raw touch data into
# higher-level gestures (tap, long-press, swipe) that the rest of
# the system can subscribe to via the EventLoop.

from kivy.event import EventDispatcher
from kivy.clock import Clock


# Gesture thresholds (can be tuned at runtime)
LONG_PRESS_DURATION = 0.5   # seconds to trigger long-press
SWIPE_MIN_DISTANCE = 50     # pixels to be classified as a swipe


class InputHandler(EventDispatcher):
    """
    Translates raw Kivy touch events into OS-level gesture events.

    Gesture events emitted via the EventLoop
    -----------------------------------------
    ``gesture_tap``        – (x, y)
    ``gesture_long_press`` – (x, y)
    ``gesture_swipe``      – (direction, dx, dy)  direction in {left,right,up,down}
    ``gesture_drag``       – (x, y, dx, dy)
    """

    def __init__(self, event_loop, **kwargs):
        super().__init__(**kwargs)
        # Reference to the shared EventLoop for emitting named events
        self._event_loop = event_loop
        # Track ongoing touches: touch.uid -> metadata dict
        self._active_touches: dict = {}

    # ------------------------------------------------------------------
    # Kivy touch callbacks (called by the root widget or Window)
    # ------------------------------------------------------------------

    def on_touch_down(self, touch) -> None:
        """Record touch start; start long-press timer."""
        self._active_touches[touch.uid] = {
            "sx": touch.x,
            "sy": touch.y,
            "long_press_triggered": False,
            "timer": Clock.schedule_once(
                lambda dt, t=touch: self._trigger_long_press(t),
                LONG_PRESS_DURATION,
            ),
        }

    def on_touch_move(self, touch) -> None:
        """Cancel long-press on significant movement; emit drag event."""
        data = self._active_touches.get(touch.uid)
        if data is None:
            return
        dx = touch.x - data["sx"]
        dy = touch.y - data["sy"]
        # Cancel long-press if the finger has moved
        if abs(dx) > 10 or abs(dy) > 10:
            data["timer"].cancel()
        self._event_loop.emit("gesture_drag", touch.x, touch.y, dx, dy)

    def on_touch_up(self, touch) -> None:
        """Decide between tap and swipe on release; clean up."""
        data = self._active_touches.pop(touch.uid, None)
        if data is None:
            return
        # Cancel pending long-press timer
        data["timer"].cancel()
        if data["long_press_triggered"]:
            return  # already handled
        dx = touch.x - data["sx"]
        dy = touch.y - data["sy"]
        dist = (dx ** 2 + dy ** 2) ** 0.5
        if dist < SWIPE_MIN_DISTANCE:
            # Short movement → tap
            self._event_loop.emit("gesture_tap", touch.x, touch.y)
        else:
            # Classify swipe direction
            direction = self._classify_swipe(dx, dy)
            self._event_loop.emit("gesture_swipe", direction, dx, dy)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _trigger_long_press(self, touch) -> None:
        data = self._active_touches.get(touch.uid)
        if data:
            data["long_press_triggered"] = True
            self._event_loop.emit("gesture_long_press", touch.x, touch.y)

    @staticmethod
    def _classify_swipe(dx: float, dy: float) -> str:
        """Return the dominant swipe direction as a string."""
        if abs(dx) >= abs(dy):
            return "right" if dx > 0 else "left"
        return "down" if dy > 0 else "up"
