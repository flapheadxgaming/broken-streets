# apps/__init__.py
# Exports for the bundled mini-apps
from .calculator import CalculatorApp
from .browser import BrowserApp
from .music_player import MusicPlayerApp

__all__ = ["CalculatorApp", "BrowserApp", "MusicPlayerApp"]
