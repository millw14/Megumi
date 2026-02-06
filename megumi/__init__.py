"""
Megumi - Your AI Desktop Companion
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

She's always watching. She's always learning.
She grows with you.

Basic usage:
    >>> from megumi import MegumiPresence
    >>> megumi = MegumiPresence()
    >>> megumi.show()

Or simply run:
    python summon.py

:copyright: (c) 2024-2026 Megumi Project
:license: MIT
"""

__version__ = "0.2.0"
__author__ = "Megumi Project"
__title__ = "megumi"

# Main presence
from megumi.ui.presence import MegumiPresence

# Core components (cute names)
from megumi.core import (
    MegumiMemories, get_memories,
    MegumiEyes, get_eyes,
    MegumiReading, get_reading,
    MegumiHeart, get_heart,
    MegumiEcho, get_echo
)

# Backward compatibility
from megumi.ui.presence import MegumiWidget

__all__ = [
    # Main
    "MegumiPresence",
    "__version__",
    
    # Core
    "MegumiMemories", "get_memories",
    "MegumiEyes", "get_eyes", 
    "MegumiReading", "get_reading",
    "MegumiHeart", "get_heart",
    "MegumiEcho", "get_echo",
    
    # Backward compatibility
    "MegumiWidget"
]
