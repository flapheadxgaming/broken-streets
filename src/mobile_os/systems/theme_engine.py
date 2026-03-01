# systems/theme_engine.py
# Theme Engine for the Mobile OS.
# Manages Light/Dark mode, accent colours, font choices and wallpapers.
# All UI components should read colours from the active ThemeProfile
# instead of hard-coding them, so a single call to ThemeEngine.apply()
# re-skins the entire OS.

from dataclasses import dataclass, field
from kivy.utils import get_color_from_hex


@dataclass
class ThemeProfile:
    """
    A complete visual theme.

    Colours are expressed as hex strings (e.g. ``"#1E1E2E"``) and
    converted to Kivy RGBA tuples on demand.
    """
    name: str
    # Background colours
    bg_primary: str   = "#FFFFFF"
    bg_secondary: str = "#F2F2F7"
    # Text colours
    text_primary: str   = "#000000"
    text_secondary: str = "#6C6C70"
    # Accent / interactive colour
    accent: str = "#007AFF"
    # Dock bar colour (RGBA hex with alpha)
    dock_color: str = "#FFFFFFCC"
    # Wallpaper asset path (relative, resolved by ResourceManager)
    wallpaper: str = "wallpapers/default_light.jpg"
    # Font family name (must be registered via Kivy LabelBase)
    font_family: str = "Roboto"

    def color(self, hex_value: str):
        """Convert a hex colour string to a Kivy RGBA tuple [0..1]."""
        return get_color_from_hex(hex_value)


# -----------------------------------------------------------------------
# Built-in themes
# -----------------------------------------------------------------------

THEME_LIGHT = ThemeProfile(
    name="Light",
    bg_primary="#FFFFFF",
    bg_secondary="#F2F2F7",
    text_primary="#000000",
    text_secondary="#6C6C70",
    accent="#007AFF",
    dock_color="#FFFFFFCC",
    wallpaper="wallpapers/default_light.jpg",
)

THEME_DARK = ThemeProfile(
    name="Dark",
    bg_primary="#1C1C1E",
    bg_secondary="#2C2C2E",
    text_primary="#FFFFFF",
    text_secondary="#AEAEB2",
    accent="#0A84FF",
    dock_color="#1C1C1ECC",
    wallpaper="wallpapers/default_dark.jpg",
)


class ThemeEngine:
    """
    Runtime theme manager.

    Usage
    -----
    engine = ThemeEngine(event_loop)
    engine.register(my_custom_theme)
    engine.apply("Dark")          # switch to built-in Dark theme
    engine.apply("MyTheme")       # switch to custom theme
    engine.set_wallpaper("wallpapers/city.jpg")
    current = engine.current      # active ThemeProfile
    """

    def __init__(self, event_loop=None):
        self._event_loop = event_loop
        # name -> ThemeProfile
        self._themes: dict[str, ThemeProfile] = {
            THEME_LIGHT.name: THEME_LIGHT,
            THEME_DARK.name: THEME_DARK,
        }
        self.current: ThemeProfile = THEME_LIGHT

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, profile: ThemeProfile) -> None:
        """Add a custom theme to the catalogue."""
        self._themes[profile.name] = profile

    # ------------------------------------------------------------------
    # Applying a theme
    # ------------------------------------------------------------------

    def apply(self, name: str) -> None:
        """
        Switch the active theme to *name*.

        Emits ``"theme_changed"`` with the new ThemeProfile so every UI
        widget can redraw itself.
        """
        profile = self._themes.get(name)
        if profile is None:
            raise ValueError(f"Unknown theme: {name!r}. "
                             f"Registered themes: {list(self._themes)}")
        self.current = profile
        self._emit("theme_changed", profile)

    def toggle_dark_light(self) -> None:
        """Convenience: flip between Dark and Light."""
        target = "Dark" if self.current.name == "Light" else "Light"
        self.apply(target)

    def set_wallpaper(self, relative_path: str) -> None:
        """
        Update only the wallpaper of the current theme and emit an event
        so the homescreen can refresh the background texture.
        """
        self.current.wallpaper = relative_path
        self._emit("wallpaper_changed", relative_path)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _emit(self, event: str, *args) -> None:
        if self._event_loop:
            self._event_loop.emit(event, *args)
