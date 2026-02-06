"""
feedback.py - Megumi's Feedback System
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

She learns from your guidance.
User feedback loop for pattern reinforcement.
"""

from typing import List, Dict, Optional, Callable
from datetime import datetime
from enum import Enum
import json

from .memories import get_memories


class FeedbackType(Enum):
    """Types of feedback Megumi can receive."""
    POSITIVE = "positive"      # User confirms pattern is correct
    NEGATIVE = "negative"      # User says pattern is wrong
    DISMISS = "dismiss"        # User dismisses without feedback
    NEVER_ASK = "never_ask"    # User says never ask about this again


class IntentType(Enum):
    """High-level intent categories for action classification."""
    NAVIGATE = "navigate"           # Opening apps, switching windows
    COMMUNICATE = "communicate"     # Email, chat, messaging
    CREATE = "create"               # Writing, coding, designing
    RESEARCH = "research"           # Browsing, searching, reading
    ORGANIZE = "organize"           # File management, tasks
    RELAX = "relax"                 # Entertainment, breaks
    UNKNOWN = "unknown"


# Intent patterns for classification
INTENT_PATTERNS = {
    IntentType.NAVIGATE: [
        'switch', 'open', 'close', 'alt+tab', 'window', 'launch'
    ],
    IntentType.COMMUNICATE: [
        'email', 'mail', 'chat', 'message', 'discord', 'slack', 'teams',
        'send', 'reply', 'compose', 'outlook', 'gmail'
    ],
    IntentType.CREATE: [
        'code', 'write', 'edit', 'create', 'design', 'develop',
        'visual studio', 'notepad', 'word', 'photoshop', 'figma'
    ],
    IntentType.RESEARCH: [
        'search', 'google', 'browse', 'read', 'wiki', 'stackoverflow',
        'chrome', 'firefox', 'documentation'
    ],
    IntentType.ORGANIZE: [
        'file', 'folder', 'copy', 'move', 'delete', 'rename', 'explorer',
        'todo', 'task', 'calendar', 'organize'
    ],
    IntentType.RELAX: [
        'youtube', 'spotify', 'netflix', 'game', 'music', 'video',
        'twitter', 'reddit', 'entertainment'
    ]
}


class PendingQuestion:
    """A question waiting for user feedback."""
    
    def __init__(self, pattern_id: int, pattern_type: str, 
                 description: str, confidence: float):
        self.pattern_id = pattern_id
        self.pattern_type = pattern_type
        self.description = description
        self.confidence = confidence
        self.created_at = datetime.now()
        self.answered = False
        self.answer: Optional[FeedbackType] = None


class MegumiFeedback:
    """
    Megumi's feedback system - she learns from your guidance.
    
    Features:
    - Asks confirmation for high-confidence patterns
    - Reinforces or weakens patterns based on feedback
    - Explains patterns in human-readable form
    """
    
    def __init__(self):
        self.memories = get_memories()
        
        # Pending questions for user
        self._pending_questions: List[PendingQuestion] = []
        
        # Callbacks for when questions are ready
        self._question_callbacks: List[Callable[[PendingQuestion], None]] = []
        
        # Settings
        self.ask_threshold = 0.7  # Only ask about patterns with confidence >= this
        self.min_frequency = 5    # Only ask after pattern seen N times
        self._asked_patterns = set()  # Track which patterns we've asked about
        
        # Feedback impact on confidence
        self.feedback_deltas = {
            FeedbackType.POSITIVE: 0.15,    # Increase confidence
            FeedbackType.NEGATIVE: -0.25,   # Decrease confidence
            FeedbackType.DISMISS: 0.0,      # No change
            FeedbackType.NEVER_ASK: -0.5    # Strong decrease
        }
    
    def classify_intent(self, action_context: Dict) -> IntentType:
        """
        Classify an action into a high-level intent category.
        
        Args:
            action_context: Dict with action details (window_title, action_type, etc.)
            
        Returns:
            IntentType enum value
        """
        # Build search text from context
        search_parts = []
        
        if action_context.get('window_title'):
            search_parts.append(action_context['window_title'].lower())
        if action_context.get('process_name'):
            search_parts.append(action_context['process_name'].lower())
        if action_context.get('action_type'):
            search_parts.append(action_context['action_type'].lower())
        if action_context.get('value'):
            search_parts.append(str(action_context['value']).lower())
        
        search_text = ' '.join(search_parts)
        
        # Match against intent patterns
        intent_scores = {}
        for intent, patterns in INTENT_PATTERNS.items():
            score = sum(1 for p in patterns if p in search_text)
            if score > 0:
                intent_scores[intent] = score
        
        if intent_scores:
            return max(intent_scores.keys(), key=lambda k: intent_scores[k])
        
        return IntentType.UNKNOWN
    
    def should_ask_about_pattern(self, pattern: Dict) -> bool:
        """
        Determine if Megumi should ask the user about a pattern.
        
        Args:
            pattern: Pattern dict from memories
            
        Returns:
            True if pattern is worth asking about
        """
        pattern_id = pattern.get('id')
        
        # Already asked about this one
        if pattern_id in self._asked_patterns:
            return False
        
        confidence = pattern.get('confidence', 0)
        frequency = pattern.get('frequency', 0)
        
        # Check thresholds
        if confidence < self.ask_threshold:
            return False
        if frequency < self.min_frequency:
            return False
        
        return True
    
    def create_question(self, pattern: Dict) -> Optional[PendingQuestion]:
        """
        Create a question about a pattern for user feedback.
        
        Args:
            pattern: Pattern dict from memories
            
        Returns:
            PendingQuestion or None
        """
        if not self.should_ask_about_pattern(pattern):
            return None
        
        pattern_id = pattern.get('id')
        pattern_type = pattern.get('pattern_type', 'unknown')
        
        # Generate human-readable description
        description = self.explain_pattern(pattern)
        
        question = PendingQuestion(
            pattern_id=pattern_id,
            pattern_type=pattern_type,
            description=description,
            confidence=pattern.get('confidence', 0)
        )
        
        self._pending_questions.append(question)
        self._asked_patterns.add(pattern_id)
        
        # Notify callbacks
        for callback in self._question_callbacks:
            try:
                callback(question)
            except Exception as e:
                print(f"[Feedback] Callback error: {e}")
        
        return question
    
    def explain_pattern(self, pattern: Dict) -> str:
        """
        Generate a human-readable explanation of a pattern.
        
        Args:
            pattern: Pattern dict from memories
            
        Returns:
            Human-readable string
        """
        pattern_type = pattern.get('pattern_type', 'unknown')
        
        try:
            triggers = json.loads(pattern.get('trigger_conditions', '{}'))
            actions = json.loads(pattern.get('action_sequence', '[]'))
        except json.JSONDecodeError:
            triggers = {}
            actions = []
        
        # Build explanation based on pattern type
        if 'window_sequence' in pattern_type:
            sequence = actions[0].get('sequence', []) if actions else []
            if len(sequence) >= 2:
                return f"After {' → '.join(sequence[:-1])}, you usually go to {sequence[-1]}"
            return f"You often switch to {actions[0].get('window', 'an app')}"
        
        elif pattern_type == 'time_habit':
            hour = triggers.get('hour', 0)
            window = actions[0].get('window', 'an app') if actions else 'an app'
            time_str = f"{hour}:00"
            return f"Around {time_str}, you usually use {window}"
        
        elif pattern_type == 'text_trigger':
            text = triggers.get('visible_text', 'something')
            action = actions[0] if actions else {}
            return f"When you see '{text}', you tend to {action.get('action', 'do something')}"
        
        else:
            return f"I noticed a pattern: {pattern_type}"
    
    def record_feedback(self, question: PendingQuestion, feedback: FeedbackType):
        """
        Record user feedback for a pattern.
        
        Args:
            question: The question being answered
            feedback: The user's feedback
        """
        question.answered = True
        question.answer = feedback
        
        # Apply feedback to pattern confidence
        delta = self.feedback_deltas.get(feedback, 0)
        if delta != 0:
            self.memories.update_pattern_confidence(question.pattern_id, delta)
            print(f"[Feedback] Pattern {question.pattern_id} confidence adjusted by {delta}")
        
        # Remove from pending
        self._pending_questions = [q for q in self._pending_questions if q != question]
    
    def get_pending_questions(self, max_count: int = 5) -> List[PendingQuestion]:
        """
        Get pending questions for the user.
        
        Args:
            max_count: Maximum questions to return
            
        Returns:
            List of unanswered questions
        """
        unanswered = [q for q in self._pending_questions if not q.answered]
        # Sort by confidence (ask about most confident first)
        unanswered.sort(key=lambda q: q.confidence, reverse=True)
        return unanswered[:max_count]
    
    def add_question_callback(self, callback: Callable[[PendingQuestion], None]):
        """Add callback for when new questions are created."""
        self._question_callbacks.append(callback)
    
    def remove_question_callback(self, callback: Callable):
        """Remove a question callback."""
        if callback in self._question_callbacks:
            self._question_callbacks.remove(callback)
    
    def check_patterns_for_questions(self):
        """
        Check recent patterns and create questions for notable ones.
        Should be called periodically.
        """
        patterns = self.memories.recall_patterns(min_confidence=self.ask_threshold)
        
        for pattern in patterns:
            if pattern.get('frequency', 0) >= self.min_frequency:
                self.create_question(pattern)


# Global instance
_feedback_instance = None


def get_feedback() -> MegumiFeedback:
    """Get or create Megumi's feedback system."""
    global _feedback_instance
    if _feedback_instance is None:
        _feedback_instance = MegumiFeedback()
    return _feedback_instance
