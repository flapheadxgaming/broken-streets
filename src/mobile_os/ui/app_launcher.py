# ui/app_launcher.py
# App Launcher / App Drawer for the Mobile OS.
# Displays all installed apps in a scrollable grid.
# Opened via an upward swipe on the homescreen or a dedicated button.

from kivy.uix.modalview import ModalView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle

from .animations import AnimationManager


class AppLauncherItem(Button):
    """Single app entry in the launcher grid."""

    def __init__(self, descriptor, on_launch, **kwargs):
        super().__init__(**kwargs)
        self.descriptor = descriptor
        self._on_launch = on_launch
        self.text = descriptor.display_name
        self.font_size = "12sp"
        self.size_hint_y = None
        self.height = 96
        self.bind(on_release=lambda *_: self._on_launch(descriptor.app_id))


class AppLauncher(ModalView):
    """
    Full-screen app drawer that slides in from the bottom.

    Parameters
    ----------
    app_registry : systems.AppRegistry
    theme        : ThemeProfile currently active
    event_loop   : core.EventLoop
    """

    def __init__(self, app_registry, theme, event_loop, **kwargs):
        super().__init__(**kwargs)
        self._registry   = app_registry
        self._theme      = theme
        self._event_loop = event_loop
        self._anim_mgr   = AnimationManager()

        self.size_hint   = (1, 0.85)
        self.pos_hint    = {"center_x": 0.5, "y": 0}
        self.background_color = theme.color(theme.bg_primary)

        self._build()

        # Keep in sync with theme changes
        self._event_loop.on("theme_changed", self._on_theme_changed)
        self._event_loop.on("app_launched",  lambda *_: self.dismiss())

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def _build(self):
        root = BoxLayout(orientation="vertical")

        # Drag handle visual hint
        handle = Label(
            text="━━━",
            size_hint=(1, None),
            height=24,
            color=self._theme.color(self._theme.text_secondary),
        )
        root.add_widget(handle)

        # Search bar placeholder
        search = Label(
            text="🔍  Search apps…",
            size_hint=(1, None),
            height=40,
            color=self._theme.color(self._theme.text_secondary),
        )
        root.add_widget(search)

        # Scrollable grid of apps
        self._grid = GridLayout(
            cols=4,
            spacing=8,
            padding=16,
            size_hint_y=None,
        )
        self._grid.bind(minimum_height=self._grid.setter("height"))
        self._populate_grid()

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self._grid)
        root.add_widget(scroll)

        self.add_widget(root)

    def _populate_grid(self):
        self._grid.clear_widgets()
        for descriptor in self._registry.get_installed():
            item = AppLauncherItem(
                descriptor,
                on_launch=self._launch_app,
            )
            self._grid.add_widget(item)

    # ------------------------------------------------------------------
    # Overrides
    # ------------------------------------------------------------------

    def open(self, *args, **kwargs):
        """Refresh app list every time the drawer is opened."""
        self._populate_grid()
        super().open(*args, **kwargs)

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _launch_app(self, app_id: str):
        widget = self._registry.launch(app_id)
        if widget:
            self._event_loop.emit("app_launched", app_id, widget)

    def _on_theme_changed(self, profile):
        self._theme = profile
        self.background_color = profile.color(profile.bg_primary)
        self._populate_grid()
