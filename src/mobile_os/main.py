# main.py
# Entry point for the Mobile OS.
#
# Architecture overview
# ─────────────────────
# ┌──────────────────────────────────────────────────────────┐
# │  MobileOSApp  (kivy.app.App subclass)                    │
# │                                                          │
# │  Core Layer                                              │
# │    EventLoop     – frame-tick & named-event bus          │
# │    InputHandler  – raw touch → tap / swipe / long-press  │
# │    ResourceManager – centralised asset cache             │
# │                                                          │
# │  System Layer                                            │
# │    AppRegistry         – install / launch / lifecycle    │
# │    NotificationManager – banner / popup / silent         │
# │    ThemeEngine         – light / dark / custom themes    │
# │                                                          │
# │  UI Layer                                                │
# │    Homescreen   – wallpaper, icon pages, dock, widgets   │
# │    AppLauncher  – full-screen app drawer (modal)         │
# │    AnimationManager – named reusable animations          │
# │                                                          │
# │  Widgets                                                 │
# │    ClockWidget · BatteryWidget · NotesWidget             │
# │                                                          │
# │  Built-in Apps                                           │
# │    CalculatorApp · BrowserApp · MusicPlayerApp           │
# └──────────────────────────────────────────────────────────┘

from kivy.app import App
from kivy.uix.relativelayout import RelativeLayout

# Core Layer
from core.event_loop      import EventLoop
from core.input_handler   import InputHandler
from core.resource_manager import ResourceManager

# System Layer
from systems.app_registry         import AppRegistry, AppDescriptor
from systems.notification_manager import NotificationManager, Notification, NotificationStyle
from systems.theme_engine         import ThemeEngine

# UI Layer
from ui.homescreen   import Homescreen
from ui.app_launcher import AppLauncher
from ui.animations   import AnimationManager

# Widgets
from ui.widgets.clock_widget   import ClockWidget
from ui.widgets.battery_widget import BatteryWidget
from ui.widgets.notes_widget   import NotesWidget

# Built-in apps
from apps.calculator   import CalculatorApp
from apps.browser      import BrowserApp
from apps.music_player import MusicPlayerApp


class MobileOSApp(App):
    """
    Top-level Kivy application class for the Mobile OS.

    Wires together all subsystems and builds the initial UI.
    """

    title = "Mobile OS"

    def build(self):
        # ── 1. Core Layer ────────────────────────────────────────────
        self.event_loop       = EventLoop()
        self.resource_manager = ResourceManager()
        self.input_handler    = InputHandler(self.event_loop)

        # ── 2. System Layer ──────────────────────────────────────────
        self.app_registry  = AppRegistry(event_loop=self.event_loop)
        self.notif_manager = NotificationManager(event_loop=self.event_loop)
        self.theme_engine  = ThemeEngine(event_loop=self.event_loop)

        # ── 3. Register built-in apps ────────────────────────────────
        self.app_registry.install(AppDescriptor(
            app_id="calculator",
            display_name="Calculator",
            icon_path="icons/calculator.png",
            entry_class=CalculatorApp,
        ))
        self.app_registry.install(AppDescriptor(
            app_id="browser",
            display_name="Browser",
            icon_path="icons/browser.png",
            entry_class=BrowserApp,
        ))
        self.app_registry.install(AppDescriptor(
            app_id="music",
            display_name="Music",
            icon_path="icons/music.png",
            entry_class=MusicPlayerApp,
        ))

        # ── 4. Homescreen widgets ────────────────────────────────────
        theme = self.theme_engine.current
        widgets = [
            ClockWidget(theme=theme),
            BatteryWidget(theme=theme),
            NotesWidget(theme=theme),
        ]

        # ── 5. UI Layer ──────────────────────────────────────────────
        root = RelativeLayout()

        self.homescreen = Homescreen(
            app_registry=self.app_registry,
            theme=theme,
            notification_manager=self.notif_manager,
            event_loop=self.event_loop,
            widgets=widgets,
        )
        root.add_widget(self.homescreen)

        self.app_launcher = AppLauncher(
            app_registry=self.app_registry,
            theme=theme,
            event_loop=self.event_loop,
        )

        # ── 6. Forward touch events to InputHandler ──────────────────
        root.bind(
            on_touch_down=lambda w, t: self.input_handler.on_touch_down(t),
            on_touch_move=lambda w, t: self.input_handler.on_touch_move(t),
            on_touch_up=lambda w, t: self.input_handler.on_touch_up(t),
        )

        # ── 7. Start the event loop ───────────────────────────────────
        self.event_loop.start()

        # ── 8. Example: show a welcome notification after 2 seconds ──
        from kivy.clock import Clock
        Clock.schedule_once(self._show_welcome_notification, 2)

        return root

    # ------------------------------------------------------------------
    # Demo / example callbacks
    # ------------------------------------------------------------------

    def _show_welcome_notification(self, dt) -> None:
        """Fire a welcome banner notification when the OS boots."""
        self.notif_manager.show(Notification(
            notif_id="welcome",
            title="Welcome to Mobile OS",
            body="Tap icons to launch apps. Swipe up for the app drawer.",
            style=NotificationStyle.BANNER,
        ))

    def on_stop(self):
        """Clean up the event loop on app exit."""
        self.event_loop.stop()


if __name__ == "__main__":
    MobileOSApp().run()
