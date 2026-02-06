"""
Megumi Configuration
~~~~~~~~~~~~~~~~~~~~

Her personality and settings.
"""

from .personality import (
    MegumiPersonality,
    AppearanceSettings,
    BodySettings,
    EyesSettings,
    HeartSettings,
    EchoSettings,
    personality,
    load_personality,
    save_personality,
    
    # Backward compatibility
    MegumiConfig,
    WindowSettings,
    AvatarSettings,
    WatcherSettings,
    LearnerSettings,
    MimicSettings,
    config,
    load_config,
    save_config
)

__all__ = [
    'MegumiPersonality',
    'AppearanceSettings',
    'BodySettings',
    'EyesSettings',
    'HeartSettings',
    'EchoSettings',
    'personality',
    'load_personality',
    'save_personality',
    
    # Backward compatibility
    'MegumiConfig',
    'config',
    'load_config',
    'save_config'
]
