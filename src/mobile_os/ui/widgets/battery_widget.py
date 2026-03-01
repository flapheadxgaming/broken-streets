# ui/widgets/battery_widget.py
# Battery status homescreen widget.
# Reads a simulated battery level (or a real platform value via psutil
# when available) and renders a labelled progress bar.

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock


def _read_battery_level() -> int:
    """
    Attempt to read the real battery level via psutil.
    Falls back to a static placeholder (80 %) when psutil is unavailable
    or the device has no battery sensor.
    """
    try:
        import psutil
        batt = psutil.sensors_battery()
        if batt is not None:
            return int(batt.percent)
    except Exception:
        pass
    return 80  # simulation fallback


class BatteryWidget(BoxLayout):
    """
    Compact battery indicator widget for the homescreen.

    Layout (horizontal)
    -------------------
    🔋  [████████░░]  80 %
    """

    def __init__(self, theme=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint   = (1, None)
        self.height      = 32
        self.spacing     = 8
        self.padding     = [8, 4]
        self._theme      = theme

        self._icon_label = Label(
            text="🔋",
            size_hint=(None, 1),
            width=32,
        )
        self.add_widget(self._icon_label)

        self._bar = ProgressBar(
            max=100,
            value=80,
            size_hint=(1, 1),
        )
        self.add_widget(self._bar)

        self._pct_label = Label(
            text="80 %",
            size_hint=(None, 1),
            width=52,
            color=self._text_color(),
        )
        self.add_widget(self._pct_label)

        # Poll every 30 seconds
        self._update(0)
        Clock.schedule_interval(self._update, 30)

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def _update(self, dt) -> None:
        level = _read_battery_level()
        self._bar.value       = level
        self._pct_label.text  = f"{level} %"

    # ------------------------------------------------------------------
    # Theme
    # ------------------------------------------------------------------

    def update_theme(self, theme) -> None:
        self._theme = theme
        self._pct_label.color = self._text_color()

    def _text_color(self):
        if self._theme:
            return self._theme.color(self._theme.text_primary)
        return (1, 1, 1, 1)
