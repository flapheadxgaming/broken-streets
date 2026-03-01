# apps/browser.py
# Browser simulation mini-app for the Mobile OS.
# Simulates a minimal in-app browser with:
#   - Address bar (URL input)
#   - Back / Forward / Reload buttons
#   - A WebView-like content area (uses kivy.uix.label as placeholder;
#     replace with kivy-webview or CEF integration for a real browser).

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView


# Simulated page content – keyed by simplified URL
_SIMULATED_PAGES: dict[str, str] = {
    "home": "Welcome to Mobile OS Browser!\n\nType a URL above to navigate.",
    "news": "📰  Top Headlines\n\n• Story 1\n• Story 2\n• Story 3",
    "weather": "🌤  Weather Forecast\n\n Today: 22°C, Partly Cloudy",
    "error": "❌  Page not found.\n\nThe URL you entered could not be loaded.",
}


class BrowserApp(BoxLayout):
    """
    Simulated browser mini-app.

    The content area renders pre-defined static text pages keyed by the
    last path segment of the URL entered.  Replace ``_load_page()`` with
    a real HTTP fetch + HTML render for production use.
    """

    def __init__(self, theme=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self._theme      = theme
        self._history: list[str] = ["home"]
        self._history_index: int = 0

        self._build()
        self._render_current()

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def _build(self):
        # ── Navigation bar ───────────────────────────────────────────
        nav = BoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=48,
            spacing=4,
            padding=[4, 4],
        )

        self._btn_back = Button(
            text="◀",
            size_hint=(None, 1),
            width=44,
            on_release=lambda *_: self._go_back(),
        )
        nav.add_widget(self._btn_back)

        self._btn_forward = Button(
            text="▶",
            size_hint=(None, 1),
            width=44,
            on_release=lambda *_: self._go_forward(),
        )
        nav.add_widget(self._btn_forward)

        self._url_input = TextInput(
            text="home",
            multiline=False,
            size_hint=(1, 1),
            font_size="14sp",
        )
        self._url_input.bind(on_text_validate=lambda *_: self._navigate_to(
            self._url_input.text.strip()))
        nav.add_widget(self._url_input)

        self._btn_go = Button(
            text="Go",
            size_hint=(None, 1),
            width=52,
            on_release=lambda *_: self._navigate_to(
                self._url_input.text.strip()),
        )
        nav.add_widget(self._btn_go)

        self.add_widget(nav)

        # ── Content area ─────────────────────────────────────────────
        scroll = ScrollView(size_hint=(1, 1))
        self._content = Label(
            text="",
            size_hint_y=None,
            font_size="14sp",
            halign="left",
            valign="top",
            markup=False,
            padding=[12, 12],
        )
        self._content.bind(texture_size=self._content.setter("size"))
        scroll.add_widget(self._content)
        self.add_widget(scroll)

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def _navigate_to(self, url: str) -> None:
        # Trim everything after the last "/" as a simple page key
        key = url.rstrip("/").split("/")[-1].lower() or "home"
        # Truncate forward history when navigating to a new page
        self._history = self._history[: self._history_index + 1]
        self._history.append(key)
        self._history_index = len(self._history) - 1
        self._render_current()

    def _go_back(self) -> None:
        if self._history_index > 0:
            self._history_index -= 1
            self._render_current()

    def _go_forward(self) -> None:
        if self._history_index < len(self._history) - 1:
            self._history_index += 1
            self._render_current()

    def _render_current(self) -> None:
        key = self._history[self._history_index]
        self._url_input.text = key
        self._content.text = _SIMULATED_PAGES.get(key, _SIMULATED_PAGES["error"])
        self._btn_back.disabled    = self._history_index == 0
        self._btn_forward.disabled = self._history_index >= len(self._history) - 1
