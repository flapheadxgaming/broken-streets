# ui/homescreen.py
# Homescreen UI for the Mobile OS.
# Renders:
#   - Multiple swipeable pages of app icons / folders
#   - A persistent Dock at the bottom
#   - Home-screen widgets (clock, battery, etc.)
#   - A notification banner area at the top
# Responds to theme changes and gesture events from the InputHandler.

from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock

from .animations import AnimationManager


# Number of icon columns on each homescreen page
ICON_COLUMNS = 4
# Max icons per page (4 × 5 grid)
ICONS_PER_PAGE = 20
# Dock capacity
DOCK_SLOTS = 4


class AppIconButton(Button):
    """A single tappable app icon with label beneath it."""

    def __init__(self, descriptor, on_launch, **kwargs):
        super().__init__(**kwargs)
        self.descriptor = descriptor
        self._on_launch = on_launch
        self.text = descriptor.display_name
        self.font_size = "11sp"
        self.size_hint = (None, None)
        self.size = (72, 88)
        self.bind(on_release=self._launch)

    def _launch(self, *_):
        self._on_launch(self.descriptor.app_id)


class HomescreenPage(GridLayout):
    """One page of app icons (ICONS_PER_PAGE icons max)."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = ICON_COLUMNS
        self.spacing = [8, 8]
        self.padding = [16, 16]
        self.size_hint = (1, 1)


class Dock(BoxLayout):
    """
    The persistent bottom dock showing up to DOCK_SLOTS pinned app icons.
    """

    def __init__(self, theme, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint = (1, None)
        self.height = 80
        self.padding = [16, 8]
        self.spacing = 16
        self._theme = theme
        self._draw_background()

    def _draw_background(self):
        with self.canvas.before:
            col = self._theme.color(self._theme.dock_color)
            Color(*col)
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

    def _update_bg(self, *_):
        self._bg_rect.pos  = self.pos
        self._bg_rect.size = self.size

    def update_theme(self, theme):
        self._theme = theme
        self.canvas.before.clear()
        self._draw_background()


class Homescreen(RelativeLayout):
    """
    Root homescreen widget.

    Parameters
    ----------
    app_registry        : systems.AppRegistry instance.
    theme               : The active ThemeProfile (from ThemeEngine).
    notification_manager: systems.NotificationManager instance.
    event_loop          : core.EventLoop instance.
    widgets             : List of Kivy widget instances to display on screen.
    """

    def __init__(self, app_registry, theme, notification_manager,
                 event_loop, widgets=None, **kwargs):
        super().__init__(**kwargs)
        self._registry   = app_registry
        self._theme      = theme
        self._notif_mgr  = notification_manager
        self._event_loop = event_loop
        self._anim_mgr   = AnimationManager()
        self._widgets    = widgets or []

        # Build the layout
        self._build()

        # Subscribe to OS events
        self._event_loop.on("theme_changed",       self._on_theme_changed)
        self._event_loop.on("wallpaper_changed",   self._on_wallpaper_changed)
        self._event_loop.on("banner_show",         self._on_banner_show)
        self._event_loop.on("gesture_swipe",       self._on_swipe)

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def _build(self):
        # Background / wallpaper
        self._bg = Image(
            source=self._resolve_wallpaper(),
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1, 1),
        )
        self.add_widget(self._bg)

        # Homescreen widgets row (clock, etc.)
        self._widget_area = BoxLayout(
            orientation="vertical",
            size_hint=(1, None),
            height=160,
            pos_hint={"top": 1},
        )
        for w in self._widgets:
            self._widget_area.add_widget(w)
        self.add_widget(self._widget_area)

        # Icon pages (horizontal scroll)
        self._page_scroll = ScrollView(
            do_scroll_x=True,
            do_scroll_y=False,
            size_hint=(1, 1),
        )
        self._pages_container = BoxLayout(
            orientation="horizontal",
            size_hint=(None, 1),
        )
        self._page_scroll.add_widget(self._pages_container)
        self.add_widget(self._page_scroll)

        # Populate pages from the app registry
        self._build_pages()

        # Dock
        self._dock = Dock(theme=self._theme, pos_hint={"y": 0})
        self.add_widget(self._dock)

        # Notification banner (initially off-screen above top edge)
        self._banner = Label(
            text="",
            size_hint=(1, None),
            height=48,
            opacity=0,
            pos_hint={"top": 1},
        )
        self.add_widget(self._banner)

    def _build_pages(self):
        """Distribute installed apps across pages of ICONS_PER_PAGE icons."""
        self._pages_container.clear_widgets()
        apps = self._registry.get_installed()
        # Ensure at least one empty page when no apps are installed
        if not apps:
            self._pages_container.add_widget(HomescreenPage())
        else:
            for i in range(0, len(apps), ICONS_PER_PAGE):
                page = HomescreenPage()
                for descriptor in apps[i:i + ICONS_PER_PAGE]:
                    icon = AppIconButton(descriptor, on_launch=self._launch_app)
                    page.add_widget(icon)
                self._pages_container.add_widget(page)
        # Ensure container width matches total page count
        page_count = len(self._pages_container.children) or 1
        self._pages_container.width = self.width * page_count

    # ------------------------------------------------------------------
    # App launching
    # ------------------------------------------------------------------

    def _launch_app(self, app_id: str):
        widget = self._registry.launch(app_id)
        if widget:
            widget.size_hint = (1, 1)
            self.add_widget(widget)
            self._anim_mgr.app_open(widget).start(widget)

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _on_theme_changed(self, profile):
        self._theme = profile
        self._bg.source = self._resolve_wallpaper()
        self._dock.update_theme(profile)

    def _on_wallpaper_changed(self, path):
        self._bg.source = path

    def _on_banner_show(self, notification):
        self._banner.text = f"{notification.title}: {notification.body}"
        self._banner.opacity = 1
        self._anim_mgr.fade_in(self._banner).start(self._banner)
        Clock.schedule_once(
            lambda dt: self._anim_mgr.fade_out(self._banner).start(self._banner),
            3,
        )

    def _on_swipe(self, direction, dx, dy):
        # Left/right swipes scroll between homescreen pages
        if direction == "left":
            self._anim_mgr.slide_left(self._pages_container).start(
                self._pages_container
            )
        elif direction == "right":
            self._anim_mgr.slide_right(self._pages_container).start(
                self._pages_container
            )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _resolve_wallpaper(self) -> str:
        """Return the wallpaper path from the current theme."""
        return self._theme.wallpaper
