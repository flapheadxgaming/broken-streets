# core/__init__.py
# Exports for the Core Layer of the Mobile OS
from .event_loop import EventLoop
from .input_handler import InputHandler
from .resource_manager import ResourceManager

__all__ = ["EventLoop", "InputHandler", "ResourceManager"]
