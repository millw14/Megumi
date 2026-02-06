"""
heart.py - Megumi's Heart
~~~~~~~~~~~~~~~~~~~~~~~~~

She learns and remembers.
Pattern recognition and learning system.
Her heart grows with every moment shared.

The heart receives (State, Action) pairs:
- State: What she sees (screen capture, window info, text)
- Action: What you do (keyboard, mouse, inputs)

From these pairs, she learns your patterns.
"""

import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from collections import defaultdict
from dataclasses import dataclass, field
import json
import hashlib

from .memories import get_memories
from .eyes import MegumiEyes
from .reading import MegumiReading, TextResult


@dataclass
class StateActionPair:
    """
    A moment of observation - State paired with Action.
    This is the fundamental unit of learning.
    """
    timestamp: str
    
    # State: What she sees
    window_title: str = ""
    process_name: str = ""
    screen_texts: List[str] = field(default_factory=list)
    
    # Action: What you do
    keys_pressed: List[str] = field(default_factory=list)
    mouse_position: Optional[tuple] = None
    mouse_clicks: List[Dict] = field(default_factory=list)
    
    # Context
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp,
            'state': {
                'window_title': self.window_title,
                'process_name': self.process_name,
                'screen_texts': self.screen_texts
            },
            'action': {
                'keys_pressed': self.keys_pressed,
                'mouse_position': self.mouse_position,
                'mouse_clicks': self.mouse_clicks
            },
            'metadata': self.metadata
        }


class Pattern:
    """Represents a learned behavioral pattern - a piece of her heart."""
    
    def __init__(self, pattern_type: str, name: str,
                 triggers: Dict[str, Any], actions: List[Dict],
                 confidence: float = 0.5, frequency: int = 1):
        self.pattern_type = pattern_type
        self.name = name
        self.triggers = triggers
        self.actions = actions
        self.confidence = confidence
        self.frequency = frequency
        self.last_seen = datetime.now()
    
    def matches(self, context: Dict) -> bool:
        """Check if current context matches this pattern's triggers."""
        for key, value in self.triggers.items():
            if key not in context:
                return False
            if isinstance(value, str) and isinstance(context[key], str):
                if value.lower() not in context[key].lower():
                    return False
            elif context[key] != value:
                return False
        return True
    
    def to_dict(self) -> Dict:
        return {
            'pattern_type': self.pattern_type,
            'name': self.name,
            'triggers': self.triggers,
            'actions': self.actions,
            'confidence': self.confidence,
            'frequency': self.frequency
        }


class MegumiHeart:
    """
    Megumi's learning engine - her heart that grows with experience.
    Observes, learns, and builds patterns from shared moments.
    
    Receives (State, Action) pairs and learns from them.
    """
    
    def __init__(self, eyes: MegumiEyes = None, reading: 'MegumiReading' = None):
        self.memories = get_memories()
        self.eyes = eyes
        self.reading = reading
        self.senses = None  # Set externally to avoid circular import
        
        self.is_learning = False
        self.current_session_id = None
        
        # In-memory caches
        self._recent_observations = []
        self._recent_actions = []
        self._state_action_pairs: List[StateActionPair] = []
        self._window_time = defaultdict(float)  # Track time per window
        self._last_window = None
        self._last_window_time = None
        
        # Pattern detection settings
        self.min_pattern_frequency = 3  # Must see pattern N times to learn
        self.pattern_window = timedelta(hours=1)  # Look for patterns within this window
        
        # N-gram settings for sequence detection
        self.ngram_sizes = [2, 3, 4]  # Bigrams, trigrams, quadgrams
        
        # Application context grouping patterns
        # Maps window title patterns to normalized app names
        self._app_patterns = {
            'Visual Studio Code': ['Visual Studio Code', 'Code - ', 'code.exe'],
            'Chrome': ['Google Chrome', 'Chrome', 'chrome.exe'],
            'Firefox': ['Mozilla Firefox', 'Firefox', 'firefox.exe'],
            'Microsoft Word': ['Word', 'Document', 'WINWORD'],
            'Microsoft Excel': ['Excel', 'xlsx', 'EXCEL'],
            'Discord': ['Discord', 'discord.exe'],
            'Spotify': ['Spotify', 'spotify.exe'],
            'Terminal': ['Terminal', 'PowerShell', 'cmd.exe', 'WindowsTerminal'],
            'File Explorer': ['File Explorer', 'explorer.exe'],
            'Notepad': ['Notepad', 'notepad.exe'],
        }
        
        # Learning stats
        self.total_pairs_collected = 0
        
        # Apply confidence decay on startup
        self._apply_startup_decay()
    
    def _apply_startup_decay(self):
        """Apply confidence decay to old patterns on startup."""
        try:
            decayed = self.memories.decay_old_patterns(decay_rate=0.95, min_confidence=0.1)
            if decayed > 0:
                print(f"[Heart] Applied decay to {decayed} old patterns")
        except Exception as e:
            print(f"[Heart] Decay error (ok for first run): {e}")
    
    def _normalize_app_name(self, window_title: str) -> str:
        """
        Normalize window title to app name for better pattern grouping.
        E.g., "Document1 - Microsoft Word" -> "Microsoft Word"
        """
        if not window_title:
            return "Unknown"
        
        for app_name, patterns in self._app_patterns.items():
            for pattern in patterns:
                if pattern.lower() in window_title.lower():
                    return app_name
        
        # If no match, try to extract app name from common title formats
        # "Title - AppName" or "AppName: Title"
        if ' - ' in window_title:
            parts = window_title.split(' - ')
            return parts[-1].strip()  # Usually app name is at the end
        elif ': ' in window_title:
            parts = window_title.split(': ')
            return parts[0].strip()  # Or at the beginning with colon
        
        return window_title
        
    # ==================== OBSERVATION ====================
    
    def observe(self, image: np.ndarray, metadata: Dict):
        """
        Process a new observation - a moment shared together.
        Creates a (State, Action) pair for learning.
        
        Args:
            image: Screenshot array
            metadata: Dict with window_title, process_name, timestamp, etc.
        """
        if not self.is_learning:
            return
        
        window_title = metadata.get('window_title', 'Unknown')
        process_name = metadata.get('process_name', 'Unknown')
        timestamp = metadata.get('timestamp', datetime.now().isoformat())
        
        # Track window time
        self._track_window_time(window_title)
        
        # Check for password fields (privacy)
        if self.senses and self.senses.detect_password_field(window_title):
            self.senses.set_password_mode(True)
        elif self.senses:
            self.senses.set_password_mode(False)
        
        # Save to memories
        obs_id = self.memories.remember_observation(
            obs_type='screen_capture',
            active_window=process_name,
            window_title=window_title,
            metadata=metadata
        )
        
        # Read text if reading ability available
        text_results = []
        if self.reading:
            try:
                text_results = self.reading.read_image(image, min_confidence=0.5)
                
                # Save text to memories
                for result in text_results:
                    self.memories.remember_text(
                        observation_id=obs_id,
                        text=result.text,
                        confidence=result.confidence,
                        bbox=result.bbox
                    )
            except Exception as e:
                print(f"[Heart] Reading error: {e}")
        
        # Get current action from senses
        action_frame = None
        if self.senses:
            action_frame = self.senses.get_current_action_frame()
        
        # Create State-Action pair
        pair = StateActionPair(
            timestamp=timestamp,
            window_title=window_title,
            process_name=process_name,
            screen_texts=[r.text for r in text_results],
            keys_pressed=action_frame.keys_pressed if action_frame else [],
            mouse_position=action_frame.mouse_position if action_frame else None,
            mouse_clicks=action_frame.mouse_clicks if action_frame else [],
            metadata=metadata
        )
        
        self._state_action_pairs.append(pair)
        self.total_pairs_collected += 1
        
        # Save pair to memories
        self.memories.remember_action(
            action_type='state_action_pair',
            target=window_title,
            position=pair.mouse_position,
            value=json.dumps(pair.keys_pressed) if pair.keys_pressed else None,
            context=pair.to_dict()
        )
        
        # Keep only recent pairs in memory
        if len(self._state_action_pairs) > 500:
            self._state_action_pairs = self._state_action_pairs[-250:]
        
        # Build observation record (for backward compatibility)
        observation = {
            'id': obs_id,
            'timestamp': timestamp,
            'window_title': window_title,
            'process_name': process_name,
            'texts': [r.text for r in text_results],
            'metadata': metadata
        }
        
        self._recent_observations.append(observation)
        
        # Keep only recent observations in memory
        if len(self._recent_observations) > 1000:
            self._recent_observations = self._recent_observations[-500:]
        
        # Try to detect patterns
        self._detect_patterns()
    
    def _track_window_time(self, window_title: str):
        """Track how long human spends in each window."""
        now = datetime.now()
        
        if self._last_window and self._last_window_time:
            elapsed = (now - self._last_window_time).total_seconds()
            self._window_time[self._last_window] += elapsed
        
        self._last_window = window_title
        self._last_window_time = now
    
    # ==================== ACTION RECORDING ====================
    
    def record_action(self, action_type: str, target: str = None,
                     position: tuple = None, value: str = None):
        """
        Record a human action.
        
        Args:
            action_type: click, type, scroll, hotkey, etc.
            target: Target element or window
            position: (x, y) coordinates
            value: Action value (typed text, key combo, etc.)
        """
        if not self.is_learning:
            return
        
        # Get current context
        context = {}
        if self._recent_observations:
            last_obs = self._recent_observations[-1]
            context = {
                'window_title': last_obs.get('window_title'),
                'process_name': last_obs.get('process_name'),
                'visible_text': last_obs.get('texts', [])
            }
        
        # Save to memories
        self.memories.remember_action(
            action_type=action_type,
            target=target,
            position=position,
            value=value,
            context=context
        )
        
        # Track in memory
        action_record = {
            'type': action_type,
            'target': target,
            'position': position,
            'value': value,
            'timestamp': datetime.now().isoformat(),
            'context': context
        }
        self._recent_actions.append(action_record)
        
        # Keep only recent actions
        if len(self._recent_actions) > 500:
            self._recent_actions = self._recent_actions[-250:]
    
    # ==================== PATTERN DETECTION ====================
    
    def _detect_patterns(self):
        """Analyze recent activity to detect patterns - learning from you."""
        if len(self._recent_observations) < 10:
            return
        
        # Pattern: Window sequences (human often opens A, then B)
        self._detect_window_sequences()
        
        # Pattern: Time-based habits (human does X at certain times)
        self._detect_time_patterns()
        
        # Pattern: Text triggers (when human sees X, they do Y)
        self._detect_text_triggers()
    
    def _detect_window_sequences(self):
        """Detect common window transition patterns using n-grams."""
        if len(self._recent_observations) < 5:
            return
        
        # Get normalized app names from recent windows
        windows = [
            self._normalize_app_name(obs['window_title']) 
            for obs in self._recent_observations[-30:]
        ]
        
        # Detect patterns for each n-gram size
        for n in self.ngram_sizes:
            if len(windows) < n:
                continue
            
            # Count n-grams
            ngrams = defaultdict(int)
            for i in range(len(windows) - n + 1):
                sequence = windows[i:i+n]
                
                # Only count if there are actual transitions (not all same window)
                if len(set(sequence)) > 1:
                    key = ' -> '.join(sequence)
                    ngrams[key] += 1
            
            # Save frequent n-grams as patterns
            for sequence_str, count in ngrams.items():
                if count >= self.min_pattern_frequency:
                    windows_in_seq = sequence_str.split(' -> ')
                    pattern_name = f"window_{n}gram_{self._hash(sequence_str)[:8]}"
                    
                    self._save_pattern(
                        pattern_type=f'window_sequence_{n}gram',
                        pattern_name=pattern_name,
                        triggers={
                            'sequence_start': windows_in_seq[:-1],  # All but last
                            'sequence_length': n
                        },
                        actions=[{
                            'action': 'suggest_window', 
                            'window': windows_in_seq[-1],  # Last window is the prediction
                            'sequence': windows_in_seq
                        }],
                        confidence=min(count / 10, 1.0)
                    )
    
    def _detect_time_patterns(self):
        """Detect time-based patterns."""
        if len(self._recent_observations) < 10:
            return
        
        # Group observations by hour of day
        hour_windows = defaultdict(lambda: defaultdict(int))
        
        for obs in self._recent_observations:
            try:
                ts = datetime.fromisoformat(obs['timestamp'])
                hour = ts.hour
                window = obs['window_title']
                hour_windows[hour][window] += 1
            except:
                continue
        
        # Find dominant windows per hour
        for hour, windows in hour_windows.items():
            if windows:
                top_window = max(windows.items(), key=lambda x: x[1])
                if top_window[1] >= self.min_pattern_frequency:
                    self._save_pattern(
                        pattern_type='time_habit',
                        pattern_name=f"hour_{hour}_habit",
                        triggers={'hour': hour},
                        actions=[{'action': 'suggest_app', 'window': top_window[0]}],
                        confidence=min(top_window[1] / 10, 1.0)
                    )
    
    def _detect_text_triggers(self):
        """Detect patterns where specific text leads to actions."""
        if len(self._recent_actions) < 5:
            return
        
        # Look for text -> action correlations
        for action in self._recent_actions[-20:]:
            context = action.get('context', {})
            visible_text = context.get('visible_text', [])
            
            # If there's text context and an action, that's a potential trigger
            for text in visible_text:
                if len(text) > 3 and len(text) < 50:  # Reasonable text length
                    pattern_name = f"text_trigger_{self._hash(text)[:8]}"
                    self._save_pattern(
                        pattern_type='text_trigger',
                        pattern_name=pattern_name,
                        triggers={'visible_text': text},
                        actions=[{
                            'action': action['type'],
                            'target': action.get('target'),
                            'value': action.get('value')
                        }],
                        confidence=0.3  # Low initial confidence
                    )
    
    def _save_pattern(self, pattern_type: str, pattern_name: str,
                     triggers: Dict, actions: List, confidence: float):
        """Save or update a pattern in memories."""
        # Check if pattern already exists
        existing = self.memories.recall_patterns(pattern_type=pattern_type)
        
        for p in existing:
            if p['pattern_name'] == pattern_name:
                # Strengthen existing pattern
                self.memories.strengthen_pattern(p['id'])
                return
        
        # New pattern
        self.memories.remember_pattern(
            pattern_type=pattern_type,
            pattern_name=pattern_name,
            trigger_conditions=triggers,
            action_sequence=actions,
            confidence=confidence
        )
    
    def _hash(self, text: str) -> str:
        """Create a short hash of text."""
        return hashlib.md5(text.encode()).hexdigest()
    
    # ==================== LEARNING CONTROL ====================
    
    def start_learning(self):
        """Start a learning session - open her heart."""
        self.is_learning = True
        self.current_session_id = self.memories.start_session()
        print(f"[Heart] Started learning session {self.current_session_id}")
    
    def stop_learning(self):
        """Stop the learning session - rest her heart."""
        self.is_learning = False
        
        if self.current_session_id:
            # Generate session summary
            summary = self._generate_session_summary()
            self.memories.end_session(self.current_session_id, summary)
            print(f"[Heart] Ended session {self.current_session_id}")
        
        self.current_session_id = None
    
    def _generate_session_summary(self) -> str:
        """Generate a summary of the learning session."""
        stats = self.memories.get_stats()
        
        # Top windows by time
        top_windows = sorted(
            self._window_time.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        summary = {
            'observations': len(self._recent_observations),
            'actions': len(self._recent_actions),
            'top_windows': [(w, f"{t:.1f}s") for w, t in top_windows],
            'memory_stats': stats
        }
        
        return json.dumps(summary, indent=2)
    
    # ==================== QUERIES ====================
    
    def get_learned_patterns(self, pattern_type: str = None,
                            min_confidence: float = 0.5) -> List[Pattern]:
        """Get learned patterns from memories."""
        raw_patterns = self.memories.recall_patterns(pattern_type, min_confidence)
        
        return [
            Pattern(
                pattern_type=p['pattern_type'],
                name=p['pattern_name'],
                triggers=json.loads(p['trigger_conditions']) if p['trigger_conditions'] else {},
                actions=json.loads(p['action_sequence']) if p['action_sequence'] else [],
                confidence=p['confidence'],
                frequency=p['frequency']
            )
            for p in raw_patterns
        ]
    
    def get_window_stats(self) -> Dict[str, float]:
        """Get time spent in each window."""
        return dict(self._window_time)
    
    def search_memory(self, query: str) -> List[Dict]:
        """Search through Megumi's memories."""
        return self.memories.search_memories(query)


# Global instance
_heart_instance = None

def get_heart() -> MegumiHeart:
    """Get or create Megumi's heart."""
    global _heart_instance
    if _heart_instance is None:
        _heart_instance = MegumiHeart()
    return _heart_instance


# Backward compatibility
MegumiLearner = MegumiHeart
get_learner = get_heart
