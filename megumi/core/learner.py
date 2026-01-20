"""
learner.py - Megumi's Brain

Pattern recognition and learning system.
She learns from everything she observes.
"""

import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from collections import defaultdict
import json
import hashlib

from .database import get_database
from .watcher import ScreenWatcher
from .ocr import ScreenReader, TextResult


class Pattern:
    """Represents a learned behavioral pattern."""
    
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


class MegumiLearner:
    """
    Megumi's learning engine.
    Observes, learns, and builds patterns from user behavior.
    """
    
    def __init__(self, watcher: ScreenWatcher = None, reader: ScreenReader = None):
        self.db = get_database()
        self.watcher = watcher
        self.reader = reader
        
        self.is_learning = False
        self.current_session_id = None
        
        # In-memory caches
        self._recent_observations = []
        self._recent_actions = []
        self._window_time = defaultdict(float)  # Track time per window
        self._last_window = None
        self._last_window_time = None
        
        # Pattern detection settings
        self.min_pattern_frequency = 3  # Must see pattern N times to learn
        self.pattern_window = timedelta(hours=1)  # Look for patterns within this window
        
    # ==================== OBSERVATION ====================
    
    def observe(self, image: np.ndarray, metadata: Dict):
        """
        Process a new observation.
        
        Args:
            image: Screenshot array
            metadata: Dict with window_title, process_name, timestamp, etc.
        """
        if not self.is_learning:
            return
        
        window_title = metadata.get('window_title', 'Unknown')
        process_name = metadata.get('process_name', 'Unknown')
        
        # Track window time
        self._track_window_time(window_title)
        
        # Save basic observation to database
        obs_id = self.db.save_observation(
            obs_type='screen_capture',
            active_window=process_name,
            window_title=window_title,
            metadata=metadata
        )
        
        # Perform OCR if reader is available
        text_results = []
        if self.reader:
            try:
                text_results = self.reader.read_image(image, min_confidence=0.5)
                
                # Save text captures
                for result in text_results:
                    self.db.save_text_capture(
                        observation_id=obs_id,
                        text=result.text,
                        confidence=result.confidence,
                        bbox=result.bbox
                    )
            except Exception as e:
                print(f"[Learner] OCR error: {e}")
        
        # Build observation record
        observation = {
            'id': obs_id,
            'timestamp': metadata.get('timestamp', datetime.now().isoformat()),
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
        """Track how long user spends in each window."""
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
        Record a user action.
        
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
        
        # Save to database
        self.db.save_action(
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
        """Analyze recent activity to detect patterns."""
        if len(self._recent_observations) < 10:
            return
        
        # Pattern: Window sequences (user often opens A, then B)
        self._detect_window_sequences()
        
        # Pattern: Time-based habits (user does X at certain times)
        self._detect_time_patterns()
        
        # Pattern: Text triggers (when user sees X, they do Y)
        self._detect_text_triggers()
    
    def _detect_window_sequences(self):
        """Detect common window transition patterns."""
        if len(self._recent_observations) < 5:
            return
        
        # Build sequence of window transitions
        windows = [obs['window_title'] for obs in self._recent_observations[-20:]]
        
        # Count bigrams (window A -> window B)
        bigrams = defaultdict(int)
        for i in range(len(windows) - 1):
            if windows[i] != windows[i+1]:  # Only count transitions
                key = f"{windows[i]} -> {windows[i+1]}"
                bigrams[key] += 1
        
        # If a transition happens frequently, it might be a pattern
        for transition, count in bigrams.items():
            if count >= self.min_pattern_frequency:
                pattern_name = f"window_sequence_{self._hash(transition)[:8]}"
                from_window, to_window = transition.split(' -> ')
                
                self._save_pattern(
                    pattern_type='window_sequence',
                    pattern_name=pattern_name,
                    triggers={'from_window': from_window},
                    actions=[{'action': 'suggest_window', 'window': to_window}],
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
        """Save or update a pattern in the database."""
        # Check if pattern already exists
        existing = self.db.get_patterns(pattern_type=pattern_type)
        
        for p in existing:
            if p['pattern_name'] == pattern_name:
                # Update frequency
                self.db.update_pattern_frequency(p['id'])
                return
        
        # New pattern
        self.db.save_pattern(
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
        """Start a learning session."""
        self.is_learning = True
        self.current_session_id = self.db.start_session()
        print(f"[Learner] Started learning session {self.current_session_id}")
    
    def stop_learning(self):
        """Stop the learning session."""
        self.is_learning = False
        
        if self.current_session_id:
            # Generate session summary
            summary = self._generate_session_summary()
            self.db.end_session(self.current_session_id, summary)
            print(f"[Learner] Ended session {self.current_session_id}")
        
        self.current_session_id = None
    
    def _generate_session_summary(self) -> str:
        """Generate a summary of the learning session."""
        stats = self.db.get_stats()
        
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
            'db_stats': stats
        }
        
        return json.dumps(summary, indent=2)
    
    # ==================== QUERIES ====================
    
    def get_learned_patterns(self, pattern_type: str = None,
                            min_confidence: float = 0.5) -> List[Pattern]:
        """Get learned patterns from database."""
        raw_patterns = self.db.get_patterns(pattern_type, min_confidence)
        
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
        """Search through Megumi's memory."""
        return self.db.search_text(query)


# Global instance
_learner_instance = None

def get_learner() -> MegumiLearner:
    """Get or create the global learner instance."""
    global _learner_instance
    if _learner_instance is None:
        _learner_instance = MegumiLearner()
    return _learner_instance
