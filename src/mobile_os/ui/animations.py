# ui/animations.py
# Animation Manager for the Mobile OS.
# Provides reusable, named animations (app-open, app-close, page-swipe,
# fade-in, bounce) that every UI component can request by name instead
# of building raw Kivy animations inline.

from kivy.animation import Animation


# Default durations (seconds) – easy to override per-call
_DURATION_FAST   = 0.20
_DURATION_NORMAL = 0.35
_DURATION_SLOW   = 0.50


class AnimationManager:
    """
    Factory for common OS UI animations.

    Each method returns a configured ``kivy.animation.Animation`` object.
    Callers are responsible for calling ``.start(widget)`` on it.

    Usage
    -----
    anim = AnimationManager()
    anim.app_open(my_widget).start(my_widget)
    """

    # ------------------------------------------------------------------
    # App transitions
    # ------------------------------------------------------------------

    def app_open(self, widget, duration: float = _DURATION_NORMAL) -> Animation:
        """
        Scale-up + fade-in effect used when launching an app from the
        homescreen.  The widget starts at 0.85× size and full transparency.
        """
        widget.opacity = 0
        widget.scale = 0.85        # requires a ScatterLayout or similar
        return (
            Animation(opacity=1, scale=1, duration=duration, t="out_cubic")
        )

    def app_close(self, widget, duration: float = _DURATION_FAST) -> Animation:
        """
        Scale-down + fade-out when an app is dismissed.
        """
        return (
            Animation(opacity=0, scale=0.85, duration=duration, t="in_cubic")
        )

    # ------------------------------------------------------------------
    # Homescreen page transitions
    # ------------------------------------------------------------------

    def slide_left(self, widget, distance: float = 360,
                   duration: float = _DURATION_NORMAL) -> Animation:
        """Slide the current page to the left (navigate forward)."""
        return Animation(x=widget.x - distance, duration=duration, t="out_quad")

    def slide_right(self, widget, distance: float = 360,
                    duration: float = _DURATION_NORMAL) -> Animation:
        """Slide the current page to the right (navigate back)."""
        return Animation(x=widget.x + distance, duration=duration, t="out_quad")

    # ------------------------------------------------------------------
    # Generic utilities
    # ------------------------------------------------------------------

    def fade_in(self, widget, duration: float = _DURATION_FAST) -> Animation:
        """Simple opacity 0 → 1 animation."""
        widget.opacity = 0
        return Animation(opacity=1, duration=duration)

    def fade_out(self, widget, duration: float = _DURATION_FAST) -> Animation:
        """Simple opacity 1 → 0 animation."""
        return Animation(opacity=0, duration=duration)

    def bounce(self, widget, scale_peak: float = 1.1,
               duration: float = _DURATION_FAST) -> Animation:
        """
        Quick scale-up then scale-back-to-normal pulse.
        Useful for icon press feedback.
        """
        up   = Animation(scale=scale_peak, duration=duration / 2, t="out_quad")
        down = Animation(scale=1.0,        duration=duration / 2, t="in_quad")
        return up + down

    def banner_slide_in(self, widget, duration: float = _DURATION_NORMAL) -> Animation:
        """Slide a notification banner down from off-screen top."""
        return Animation(top=widget.parent.height, duration=duration, t="out_quad")

    def banner_slide_out(self, widget, duration: float = _DURATION_FAST) -> Animation:
        """Slide a notification banner back up off-screen."""
        return Animation(top=widget.parent.height + widget.height,
                         duration=duration, t="in_quad")
