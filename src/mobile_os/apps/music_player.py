# apps/music_player.py
# Music Player mini-app for the Mobile OS.
# Plays audio files from the device using Kivy's SoundLoader.
# Displays album art placeholder, track info, and transport controls
# (play/pause, previous, next, seek bar).

import os
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.core.audio import SoundLoader


class Track:
    """Metadata for a single audio track."""

    def __init__(self, title: str, artist: str,
                 file_path: str, cover_path: str = ""):
        self.title      = title
        self.artist     = artist
        self.file_path  = file_path
        self.cover_path = cover_path


class MusicPlayerApp(BoxLayout):
    """
    Music player mini-app.

    Parameters
    ----------
    tracks : list[Track]  – pre-loaded playlist.
    theme  : ThemeProfile – optional, for colour theming.
    """

    def __init__(self, tracks: list | None = None,
                 theme=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self._theme      = theme
        self._tracks     = tracks or []
        self._index      = 0
        self._sound      = None
        self._playing    = False
        self._seek_event = None

        self._build()
        if self._tracks:
            self._load_track(self._index)

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def _build(self):
        # Album art
        self._cover = Image(
            source="",
            size_hint=(1, 0.45),
            allow_stretch=True,
            keep_ratio=True,
        )
        self.add_widget(self._cover)

        # Track title
        self._title_label = Label(
            text="No track loaded",
            font_size="16sp",
            bold=True,
            size_hint=(1, None),
            height=32,
        )
        self.add_widget(self._title_label)

        # Artist name
        self._artist_label = Label(
            text="",
            font_size="13sp",
            size_hint=(1, None),
            height=24,
        )
        self.add_widget(self._artist_label)

        # Seek bar
        self._seek_bar = Slider(
            min=0,
            max=100,
            value=0,
            size_hint=(1, None),
            height=32,
        )
        self._seek_bar.bind(on_touch_up=self._on_seek)
        self.add_widget(self._seek_bar)

        # Transport controls
        controls = BoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=56,
            spacing=8,
            padding=[16, 4],
        )
        controls.add_widget(Button(
            text="⏮",  font_size="22sp",
            on_release=lambda *_: self._previous()))
        self._play_btn = Button(
            text="▶",  font_size="22sp",
            on_release=lambda *_: self._toggle_play())
        controls.add_widget(self._play_btn)
        controls.add_widget(Button(
            text="⏭",  font_size="22sp",
            on_release=lambda *_: self._next()))
        self.add_widget(controls)

    # ------------------------------------------------------------------
    # Playback
    # ------------------------------------------------------------------

    def _load_track(self, index: int) -> None:
        """Load the track at *index* without auto-playing."""
        if self._sound:
            self._sound.stop()
            self._sound = None
        if not self._tracks:
            return
        self._index = index % len(self._tracks)
        track = self._tracks[self._index]
        self._title_label.text  = track.title
        self._artist_label.text = track.artist
        self._cover.source      = track.cover_path if track.cover_path else ""
        self._seek_bar.value    = 0
        if os.path.isfile(track.file_path):
            self._sound = SoundLoader.load(track.file_path)
        self._update_play_button()

    def _toggle_play(self) -> None:
        if not self._sound:
            return
        if self._playing:
            self._sound.stop()
            self._playing = False
            if self._seek_event:
                self._seek_event.cancel()
        else:
            self._sound.play()
            self._playing = True
            self._seek_event = Clock.schedule_interval(self._update_seek, 0.5)
        self._update_play_button()

    def _previous(self) -> None:
        was_playing = self._playing
        self._stop()
        self._load_track(self._index - 1)
        if was_playing:
            self._toggle_play()

    def _next(self) -> None:
        was_playing = self._playing
        self._stop()
        self._load_track(self._index + 1)
        if was_playing:
            self._toggle_play()

    def _stop(self) -> None:
        if self._sound:
            self._sound.stop()
        self._playing = False
        if self._seek_event:
            self._seek_event.cancel()
        self._update_play_button()

    def _on_seek(self, slider, touch) -> None:
        if self._sound and self._sound.length:
            self._sound.seek(slider.value / 100.0 * self._sound.length)

    def _update_seek(self, dt) -> None:
        if self._sound and self._sound.length and self._playing:
            self._seek_bar.value = (
                self._sound.get_pos() / self._sound.length * 100
            )

    def _update_play_button(self) -> None:
        self._play_btn.text = "⏸" if self._playing else "▶"
