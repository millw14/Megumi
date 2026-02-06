"""
personality.py - Megumi's Personality
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Her personality settings.
How she looks, behaves, and interacts with you.
"""

from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path


@dataclass
class AppearanceSettings:
    """How Megumi appears on your desktop"""
    width: int = 300
    height: int = 420
    start_position: str = "bottom-right"  # top-left, top-right, bottom-left, bottom-right
    always_on_top: bool = True
    start_minimized: bool = False


@dataclass
class BodySettings:
    """Her VRM body settings"""
    model_path: str = "assets/models/megumi_chan.vrm"
    idle_animation: bool = True
    cursor_tracking: bool = True
    blink_interval: tuple[float, float] = (2.0, 6.0)  # min, max seconds


@dataclass
class EyesSettings:
    """How she watches (Phase 2)"""
    enabled: bool = False
    capture_interval: float = 1.0  # seconds
    reading_enabled: bool = False  # OCR
    regions: list = field(default_factory=list)


@dataclass
class HeartSettings:
    """How she learns (Phase 4)"""
    enabled: bool = False
    memories_path: str = "data/megumi_memories.db"
    min_pattern_frequency: int = 3
    max_pattern_age_days: int = 30


@dataclass
class EchoSettings:
    """How she echoes you (Phase 5)"""
    enabled: bool = False
    mode: str = "disabled"  # disabled, preview, confirm, autonomous
    safety_level: str = "cautious"  # paranoid, cautious, normal
    action_log_path: str = "data/actions.log"


@dataclass
class MegumiPersonality:
    """Megumi's complete personality configuration"""
    appearance: AppearanceSettings = field(default_factory=AppearanceSettings)
    body: BodySettings = field(default_factory=BodySettings)
    eyes: EyesSettings = field(default_factory=EyesSettings)
    heart: HeartSettings = field(default_factory=HeartSettings)
    echo: EchoSettings = field(default_factory=EchoSettings)
    
    # Server
    server_port: int = 9998
    
    # Debug
    debug_mode: bool = False
    show_fps: bool = False


# Default personality
personality = MegumiPersonality()


def load_personality(path: Optional[str] = None) -> MegumiPersonality:
    """Load personality from file"""
    # TODO: Implement YAML/JSON config loading
    return MegumiPersonality()


def save_personality(p: MegumiPersonality, path: str):
    """Save personality to file"""
    # TODO: Implement config saving
    pass


# Backward compatibility
WindowSettings = AppearanceSettings
AvatarSettings = BodySettings
WatcherSettings = EyesSettings
LearnerSettings = HeartSettings
MimicSettings = EchoSettings
MegumiConfig = MegumiPersonality
config = personality
load_config = load_personality
save_config = save_personality
