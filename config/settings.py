"""
Megumi Configuration
~~~~~~~~~~~~~~~~~~~~

Central configuration for all Megumi settings.
"""

from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path


@dataclass
class WindowSettings:
    """Desktop widget window settings"""
    width: int = 300
    height: int = 420
    start_position: str = "bottom-right"  # top-left, top-right, bottom-left, bottom-right
    always_on_top: bool = True
    start_minimized: bool = False


@dataclass
class AvatarSettings:
    """VRM avatar settings"""
    model_path: str = "assets/models/megumi.vrm"
    idle_animation: bool = True
    cursor_tracking: bool = True
    blink_interval: tuple[float, float] = (2.0, 6.0)  # min, max seconds


@dataclass
class WatcherSettings:
    """Screen watcher settings (Phase 2)"""
    enabled: bool = False
    capture_interval: float = 1.0  # seconds
    ocr_enabled: bool = False
    regions: list = field(default_factory=list)


@dataclass
class LearnerSettings:
    """Pattern learner settings (Phase 4)"""
    enabled: bool = False
    storage_path: str = "data/patterns.db"
    min_pattern_frequency: int = 3
    max_pattern_age_days: int = 30


@dataclass
class MimicSettings:
    """Mimic engine settings (Phase 5)"""
    enabled: bool = False
    mode: str = "disabled"  # disabled, preview, confirm, autonomous
    safety_level: str = "cautious"  # paranoid, cautious, normal
    action_log_path: str = "data/actions.log"


@dataclass
class MegumiConfig:
    """Main configuration class"""
    window: WindowSettings = field(default_factory=WindowSettings)
    avatar: AvatarSettings = field(default_factory=AvatarSettings)
    watcher: WatcherSettings = field(default_factory=WatcherSettings)
    learner: LearnerSettings = field(default_factory=LearnerSettings)
    mimic: MimicSettings = field(default_factory=MimicSettings)
    
    # Server
    server_port: int = 9998
    
    # Debug
    debug_mode: bool = False
    show_fps: bool = False


# Default configuration instance
config = MegumiConfig()


def load_config(path: Optional[str] = None) -> MegumiConfig:
    """Load configuration from file"""
    # TODO: Implement YAML/JSON config loading
    return MegumiConfig()


def save_config(cfg: MegumiConfig, path: str):
    """Save configuration to file"""
    # TODO: Implement config saving
    pass
