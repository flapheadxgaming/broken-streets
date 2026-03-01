# ui/widgets/notes_widget.py
# Notes homescreen widget.
# Shows a simple sticky-note area where the user can type a short memo
# that persists across sessions (saved to a plain-text file).

import os
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, RoundedRectangle
from kivy.clock import Clock


# Default save location (relative to the asset root – resolved by the
# ResourceManager when the OS boots; here we use a /tmp fallback for
# standalone testing).
_DEFAULT_NOTES_FILE = os.path.join(
    os.path.expanduser("~"), ".mobile_os_notes.txt"
)


class NotesWidget(BoxLayout):
    """
    Sticky-note widget for the homescreen.

    The user can type a brief memo; it is auto-saved on every keystroke
    to ``notes_file`` so it survives app restarts.
    """

    def __init__(self, theme=None, notes_file: str = _DEFAULT_NOTES_FILE,
                 **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint   = (1, None)
        self.height      = 150
        self.padding     = 8
        self.spacing     = 4
        self._theme      = theme
        self._notes_file = notes_file

        self._draw_background()

        # Header label
        self._header = Label(
            text="📝  Notes",
            size_hint=(1, None),
            height=28,
            font_size="13sp",
            bold=True,
            color=self._text_color(),
            halign="left",
        )
        self.add_widget(self._header)

        # Text input area
        self._input = TextInput(
            text=self._load(),
            multiline=True,
            size_hint=(1, 1),
            font_size="13sp",
            foreground_color=self._text_color(),
            background_color=(0, 0, 0, 0),  # transparent – bg drawn manually
        )
        self._input.bind(text=self._on_text_change)
        self.add_widget(self._input)
        # Pending save event handle (debounce)
        self._save_event = None

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _on_text_change(self, instance, value) -> None:
        """Debounce saves: write to disk 500 ms after the last keystroke."""
        if self._save_event:
            self._save_event.cancel()
        self._save_event = Clock.schedule_once(
            lambda dt: self._write(value), 0.5
        )

    def _write(self, text: str) -> None:
        """Persist *text* to disk."""
        try:
            with open(self._notes_file, "w", encoding="utf-8") as fh:
                fh.write(text)
        except OSError:
            pass  # silently ignore write errors (e.g. read-only FS)

    def _load(self) -> str:
        """Read saved notes from disk; return empty string if not found."""
        try:
            with open(self._notes_file, "r", encoding="utf-8") as fh:
                return fh.read()
        except OSError:
            return ""

    # ------------------------------------------------------------------
    # Visual background
    # ------------------------------------------------------------------

    def _draw_background(self):
        with self.canvas.before:
            col = (1, 0.98, 0.8, 0.9)  # warm yellow note colour
            Color(*col)
            self._bg = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[8]
            )
        self.bind(pos=self._update_bg, size=self._update_bg)

    def _update_bg(self, *_):
        self._bg.pos  = self.pos
        self._bg.size = self.size

    # ------------------------------------------------------------------
    # Theme
    # ------------------------------------------------------------------

    def update_theme(self, theme) -> None:
        self._theme = theme
        col = self._text_color()
        self._header.color = col
        self._input.foreground_color = col

    def _text_color(self):
        # Notes widget uses dark text regardless of OS theme for readability
        return (0.15, 0.15, 0.15, 1)
