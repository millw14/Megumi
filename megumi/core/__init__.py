"""
Megumi Core - The brain and eyes.
"""

from .database import MegumiDatabase, get_database
from .watcher import ScreenWatcher, get_watcher
from .ocr import ScreenReader, TextResult, get_reader
from .learner import MegumiLearner, Pattern, get_learner
from .mimic import MegumiMimic, Action, ActionType, get_mimic

__all__ = [
    'MegumiDatabase', 'get_database',
    'ScreenWatcher', 'get_watcher',
    'ScreenReader', 'TextResult', 'get_reader',
    'MegumiLearner', 'Pattern', 'get_learner',
    'MegumiMimic', 'Action', 'ActionType', 'get_mimic'
]
