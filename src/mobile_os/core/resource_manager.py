# core/resource_manager.py
# Asset / resource management for the Mobile OS.
# Centralises loading of images, sounds, fonts and animation data so
# that every subsystem uses the same cache and avoids duplicate loads.

import os
from kivy.cache import Cache
from kivy.core.image import Image as CoreImage
from kivy.core.audio import SoundLoader


# Register a named Kivy cache bucket for OS assets (limit = 200 entries)
Cache.register("mobile_os.assets", limit=200)

# Default asset root – resolved relative to this file so the package is
# portable.  Override by calling ResourceManager.set_asset_root().
_DEFAULT_ASSET_ROOT = os.path.join(
    os.path.dirname(__file__), "..", "assets"
)


class ResourceManager:
    """
    Centralised loader and cache for OS assets.

    Usage
    -----
    rm = ResourceManager()
    texture = rm.load_image("icons/calculator.png")
    sound   = rm.load_sound("sfx/tap.wav")
    """

    def __init__(self, asset_root: str | None = None):
        self._root = os.path.abspath(asset_root or _DEFAULT_ASSET_ROOT)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_asset_root(self, path: str) -> None:
        """Override the base directory for all asset lookups."""
        self._root = os.path.abspath(path)

    def load_image(self, relative_path: str):
        """
        Return a Kivy *Texture* for *relative_path* (relative to asset root).
        Subsequent calls with the same path return the cached texture.
        """
        cache_key = f"image:{relative_path}"
        cached = Cache.get("mobile_os.assets", cache_key)
        if cached:
            return cached
        full_path = self._resolve(relative_path)
        texture = CoreImage(full_path).texture if os.path.isfile(full_path) else None
        Cache.append("mobile_os.assets", cache_key, texture)
        return texture

    def load_sound(self, relative_path: str):
        """
        Return a Kivy *Sound* object for *relative_path*.
        Returns *None* when the file does not exist or no audio backend
        is available.
        """
        cache_key = f"sound:{relative_path}"
        cached = Cache.get("mobile_os.assets", cache_key)
        if cached:
            return cached
        full_path = self._resolve(relative_path)
        sound = SoundLoader.load(full_path) if os.path.isfile(full_path) else None
        Cache.append("mobile_os.assets", cache_key, sound)
        return sound

    def asset_path(self, relative_path: str) -> str:
        """Return the absolute path for *relative_path* inside the asset root."""
        return self._resolve(relative_path)

    def clear_cache(self) -> None:
        """Evict all entries from the OS asset cache."""
        Cache.remove("mobile_os.assets")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _resolve(self, relative_path: str) -> str:
        return os.path.join(self._root, relative_path)
