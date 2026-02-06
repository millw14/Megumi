"""
Megumi Core - Her mind, heart, and soul.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The essence of who she is.
"""

# New cute names
from .memories import MegumiMemories, get_memories
from .eyes import MegumiEyes, get_eyes
from .senses import MegumiSenses, InputEvent, ActionFrame, get_senses
from .reading import MegumiReading, TextResult, get_reading
from .heart import MegumiHeart, Pattern, get_heart
from .echo import MegumiEcho, Action, ActionType, get_echo

# New enhanced learning modules
from .brain import MegumiBrain, get_brain
from .prediction import MegumiPrediction, get_prediction
from .feedback import MegumiFeedback, FeedbackType, IntentType, get_feedback

# Backward compatibility with old names
from .memories import MegumiDatabase, get_database
from .eyes import ScreenWatcher, get_watcher
from .reading import ScreenReader, get_reader
from .heart import MegumiLearner, get_learner
from .echo import MegumiMimic, get_mimic

__all__ = [
    # Cute names
    'MegumiMemories', 'get_memories',
    'MegumiEyes', 'get_eyes',
    'MegumiSenses', 'InputEvent', 'ActionFrame', 'get_senses',
    'MegumiReading', 'TextResult', 'get_reading',
    'MegumiHeart', 'Pattern', 'get_heart',
    'MegumiEcho', 'Action', 'ActionType', 'get_echo',
    
    # Enhanced learning
    'MegumiBrain', 'get_brain',
    'MegumiPrediction', 'get_prediction',
    'MegumiFeedback', 'FeedbackType', 'IntentType', 'get_feedback',
    
    # Backward compatibility
    'MegumiDatabase', 'get_database',
    'ScreenWatcher', 'get_watcher',
    'ScreenReader', 'get_reader',
    'MegumiLearner', 'get_learner',
    'MegumiMimic', 'get_mimic'
]

