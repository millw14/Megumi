"""
Megumi UI Module
~~~~~~~~~~~~~~~~

Her physical presence in your world.

Contains:
- MegumiPresence: The main desktop companion window (her body)
- soul.html: Three.js VRM renderer (her visual soul)
"""

from .presence import MegumiPresence

# Backward compatibility
from .presence import MegumiWidget

__all__ = ["MegumiPresence", "MegumiWidget"]
