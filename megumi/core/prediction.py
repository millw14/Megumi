"""
prediction.py - Megumi's Prediction Engine
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

She knows what you'll do next.
Combines patterns, semantics, and habits to predict actions.
"""

from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
from collections import defaultdict
import json

from .memories import get_memories
from .brain import get_brain


class MegumiPrediction:
    """
    Megumi's prediction engine - she anticipates your needs.
    
    Combines:
    - N-gram sequence patterns
    - Time-based habits
    - Semantic context similarity
    """
    
    def __init__(self):
        self.memories = get_memories()
        self.brain = get_brain()
        
        # Prediction weights
        self.weights = {
            'sequence_pattern': 0.4,   # Weight for n-gram patterns
            'time_habit': 0.3,         # Weight for time-of-day habits
            'semantic_similarity': 0.3  # Weight for semantic matching
        }
    
    def predict_next_window(self, current_context: Dict) -> Optional[Dict]:
        """
        Predict the next window/application the user will open.
        
        Args:
            current_context: Dict with current window_title, process_name, etc.
            
        Returns:
            Dict with predicted window and confidence, or None
        """
        predictions = []
        
        # 1. Check n-gram sequence patterns
        sequence_pred = self._predict_from_sequences(current_context)
        if sequence_pred:
            predictions.append(sequence_pred)
        
        # 2. Check time-based habits
        time_pred = self._predict_from_time()
        if time_pred:
            predictions.append(time_pred)
        
        # 3. Semantic pattern matching
        semantic_pred = self._predict_from_semantics(current_context)
        if semantic_pred:
            predictions.append(semantic_pred)
        
        if not predictions:
            return None
        
        # Combine predictions
        return self._combine_predictions(predictions)
    
    def _predict_from_sequences(self, context: Dict) -> Optional[Dict]:
        """Predict based on window sequence patterns."""
        current_window = context.get('window_title', '')
        
        # Get sequence patterns
        patterns = self.memories.recall_patterns(
            pattern_type=None,  # Get all pattern types
            min_confidence=0.3
        )
        
        # Find patterns that match current window
        matching = []
        for p in patterns:
            if 'window_sequence' not in p.get('pattern_type', ''):
                continue
            
            try:
                triggers = json.loads(p['trigger_conditions']) if p['trigger_conditions'] else {}
                sequence_start = triggers.get('sequence_start', [])
                
                # Check if current window matches end of sequence start
                if sequence_start and isinstance(sequence_start, list):
                    # Simple match: current window contains or equals last item
                    if current_window and sequence_start[-1].lower() in current_window.lower():
                        actions = json.loads(p['action_sequence']) if p['action_sequence'] else []
                        if actions:
                            matching.append({
                                'window': actions[0].get('window'),
                                'confidence': p['confidence'],
                                'source': 'sequence',
                                'pattern_id': p['id']
                            })
            except (json.JSONDecodeError, KeyError):
                continue
        
        if matching:
            # Return highest confidence match
            best = max(matching, key=lambda x: x['confidence'])
            return {
                'window': best['window'],
                'confidence': best['confidence'] * self.weights['sequence_pattern'],
                'source': 'sequence_pattern'
            }
        
        return None
    
    def _predict_from_time(self) -> Optional[Dict]:
        """Predict based on time-of-day habits."""
        current_hour = datetime.now().hour
        
        # Get time habit patterns
        patterns = self.memories.recall_patterns(
            pattern_type='time_habit',
            min_confidence=0.3
        )
        
        for p in patterns:
            try:
                triggers = json.loads(p['trigger_conditions']) if p['trigger_conditions'] else {}
                if triggers.get('hour') == current_hour:
                    actions = json.loads(p['action_sequence']) if p['action_sequence'] else []
                    if actions:
                        return {
                            'window': actions[0].get('window'),
                            'confidence': p['confidence'] * self.weights['time_habit'],
                            'source': 'time_habit'
                        }
            except (json.JSONDecodeError, KeyError):
                continue
        
        return None
    
    def _predict_from_semantics(self, context: Dict) -> Optional[Dict]:
        """Predict based on semantic similarity to past contexts."""
        # This requires historical context embeddings
        # For now, return None as this needs integration with observation storage
        return None
    
    def _combine_predictions(self, predictions: List[Dict]) -> Dict:
        """Combine multiple predictions into a single result."""
        if not predictions:
            return None
        
        if len(predictions) == 1:
            return predictions[0]
        
        # Aggregate by window
        window_scores = defaultdict(float)
        window_sources = defaultdict(list)
        
        for pred in predictions:
            window = pred.get('window')
            if window:
                window_scores[window] += pred['confidence']
                window_sources[window].append(pred['source'])
        
        if not window_scores:
            return None
        
        # Find best window
        best_window = max(window_scores.keys(), key=lambda w: window_scores[w])
        
        return {
            'window': best_window,
            'confidence': window_scores[best_window],
            'sources': window_sources[best_window]
        }
    
    def predict_next_action(self, context: Dict) -> Optional[Dict]:
        """
        Predict the next action (beyond just window switching).
        
        Args:
            context: Current context with window, visible text, etc.
            
        Returns:
            Predicted action dict or None
        """
        # Get text trigger patterns
        patterns = self.memories.recall_patterns(
            pattern_type='text_trigger',
            min_confidence=0.5
        )
        
        visible_texts = context.get('texts', []) or context.get('visible_text', [])
        if not visible_texts:
            return None
        
        for p in patterns:
            try:
                triggers = json.loads(p['trigger_conditions']) if p['trigger_conditions'] else {}
                trigger_text = triggers.get('visible_text', '')
                
                # Check if trigger text is visible
                for text in visible_texts:
                    if trigger_text and trigger_text.lower() in text.lower():
                        actions = json.loads(p['action_sequence']) if p['action_sequence'] else []
                        if actions:
                            return {
                                'action': actions[0],
                                'confidence': p['confidence'],
                                'trigger': trigger_text,
                                'source': 'text_trigger'
                            }
            except (json.JSONDecodeError, KeyError):
                continue
        
        return None
    
    def get_recommendations(self, context: Dict, max_count: int = 3) -> List[Dict]:
        """
        Get multiple recommendations based on current context.
        
        Args:
            context: Current context
            max_count: Maximum recommendations to return
            
        Returns:
            List of recommendation dicts
        """
        recommendations = []
        
        # Window prediction
        window_pred = self.predict_next_window(context)
        if window_pred:
            recommendations.append({
                'type': 'window',
                'suggestion': f"Open {window_pred['window']}",
                'confidence': window_pred['confidence'],
                'sources': window_pred.get('sources', [window_pred.get('source')])
            })
        
        # Action prediction
        action_pred = self.predict_next_action(context)
        if action_pred:
            action = action_pred['action']
            recommendations.append({
                'type': 'action',
                'suggestion': f"{action.get('action', 'Do')} {action.get('value', '')}".strip(),
                'confidence': action_pred['confidence'],
                'trigger': action_pred.get('trigger')
            })
        
        # Sort by confidence
        recommendations.sort(key=lambda x: x['confidence'], reverse=True)
        return recommendations[:max_count]


# Global instance
_prediction_instance = None


def get_prediction() -> MegumiPrediction:
    """Get or create Megumi's prediction engine."""
    global _prediction_instance
    if _prediction_instance is None:
        _prediction_instance = MegumiPrediction()
    return _prediction_instance
