# ui/widgets/clock_widget.py
# Clock homescreen widget.
# Displays the current time (HH:MM) and date using Kivy Labels.
# Updates every second via Kivy Clock.

from datetime import datetime
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock


class ClockWidget(BoxLayout):
    """
    A compact digital clock widget for the homescreen.

    Layout (vertical)
    -----------------
    ┌──────────────┐
    │   14:35      │  ← large time label
    │ Monday 1 Mar │  ← small date label
    └──────────────┘
    """

    def __init__(self, theme=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint   = (1, None)
        self.height      = 120
        self._theme      = theme

        # Time label
        self._time_label = Label(
            text="--:--",
            font_size="48sp",
            bold=True,
            color=self._text_color(),
            size_hint=(1, 0.7),
        )
        self.add_widget(self._time_label)

        # Date label
        self._date_label = Label(
            text="",
            font_size="16sp",
            color=self._text_color(),
            size_hint=(1, 0.3),
        )
        self.add_widget(self._date_label)

        # Start the 1-second update loop
        self._update(0)
        Clock.schedule_interval(self._update, 1)

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def _update(self, dt) -> None:
        """Refresh time and date labels with the current local time."""
        now = datetime.now()
        self._time_label.text = now.strftime("%H:%M")
        self._date_label.text = now.strftime("%A, %d %B %Y")

    # ------------------------------------------------------------------
    # Theme
    # ------------------------------------------------------------------

    def update_theme(self, theme) -> None:
        """Re-apply colours when the global theme changes."""
        self._theme = theme
        col = self._text_color()
        self._time_label.color = col
        self._date_label.color = col

    def _text_color(self):
        if self._theme:
            return self._theme.color(self._theme.text_primary)
        return (1, 1, 1, 1)   # white fallback
