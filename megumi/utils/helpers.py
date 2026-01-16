"""
Megumi Helper Utilities
~~~~~~~~~~~~~~~~~~~~~~~

Common utility functions used across the project.
"""

import os
from pathlib import Path
from typing import Union


def get_resource_path(relative_path: str) -> Path:
    """
    Get absolute path to a resource file.
    Works both in development and when packaged.
    
    Args:
        relative_path: Path relative to megumi package root
        
    Returns:
        Absolute path to the resource
    """
    base_path = Path(__file__).parent.parent.parent
    return base_path / relative_path


def ensure_dir(path: Union[str, Path]) -> Path:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path
        
    Returns:
        Path object to the directory
    """
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_screen_size() -> tuple[int, int]:
    """Get the primary screen dimensions"""
    try:
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            screen = app.primaryScreen().geometry()
            return screen.width(), screen.height()
    except ImportError:
        pass
    
    # Fallback to common resolution
    return 1920, 1080


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp a value between min and max"""
    return max(min_val, min(max_val, value))


def lerp(start: float, end: float, t: float) -> float:
    """Linear interpolation between two values"""
    return start + (end - start) * t
