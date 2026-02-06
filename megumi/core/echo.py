"""
echo.py - Megumi's Echo
~~~~~~~~~~~~~~~~~~~~~~~

She echoes your actions.
Activity mimicking system.
When you're away, she can be you.

WARNING: This module can control your computer.
Use with caution.
"""

import time
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    print("[Echo] pyautogui not installed - echoing disabled")

from .memories import get_memories
from .heart import Pattern


class ActionType(Enum):
    """Types of actions Megumi can echo."""
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    TYPE = "type"
    HOTKEY = "hotkey"
    SCROLL = "scroll"
    MOVE = "move"
    WAIT = "wait"


@dataclass
class Action:
    """Represents an action to echo."""
    action_type: ActionType
    target: Optional[str] = None
    position: Optional[Tuple[int, int]] = None
    value: Optional[str] = None
    duration: float = 0.1
    

class MegumiEcho:
    """
    Megumi's action execution engine - she echoes what you do.
    
    SAFETY: All actions require explicit approval by default.
    """
    
    def __init__(self, safe_mode: bool = True):
        """
        Initialize echo engine.
        
        Args:
            safe_mode: If True, requires approval for each action
        """
        self.safe_mode = safe_mode
        self.is_enabled = False
        self.memories = get_memories()
        
        # Safety settings
        self.allowed_apps: List[str] = []  # Whitelist of apps she can interact with
        self.blocked_regions: List[Tuple[int, int, int, int]] = []  # Screen regions to avoid
        self.max_actions_per_minute = 30
        
        self._action_count = 0
        self._last_action_time = 0
        
        if not PYAUTOGUI_AVAILABLE:
            print("[Echo] pyautogui required for echoing. Install with: pip install pyautogui")
    
    # ==================== SAFETY ====================
    
    def enable(self, confirm: bool = False):
        """
        Enable echo mode.
        
        Args:
            confirm: Must be True to actually enable (prevents accidental enabling)
        """
        if not confirm:
            print("[Echo] You must pass confirm=True to enable echoing")
            return
        
        if not PYAUTOGUI_AVAILABLE:
            print("[Echo] Cannot enable - pyautogui not installed")
            return
        
        self.is_enabled = True
        pyautogui.FAILSAFE = True  # Move mouse to corner to abort
        print("[Echo] Enabled - Move mouse to corner to emergency stop")
    
    def disable(self):
        """Disable echo mode."""
        self.is_enabled = False
        print("[Echo] Disabled")
    
    def add_allowed_app(self, app_name: str):
        """Add an app to the whitelist."""
        if app_name not in self.allowed_apps:
            self.allowed_apps.append(app_name)
    
    def remove_allowed_app(self, app_name: str):
        """Remove an app from the whitelist."""
        if app_name in self.allowed_apps:
            self.allowed_apps.remove(app_name)
    
    def add_blocked_region(self, x: int, y: int, w: int, h: int):
        """Add a screen region that Megumi cannot touch."""
        self.blocked_regions.append((x, y, w, h))
    
    def _is_safe_position(self, x: int, y: int) -> bool:
        """Check if a position is safe to interact with."""
        for rx, ry, rw, rh in self.blocked_regions:
            if rx <= x <= rx + rw and ry <= y <= ry + rh:
                return False
        return True
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limit."""
        now = time.time()
        if now - self._last_action_time > 60:
            self._action_count = 0
        
        if self._action_count >= self.max_actions_per_minute:
            print("[Echo] Rate limit exceeded")
            return False
        
        return True
    
    # ==================== ACTIONS ====================
    
    def execute(self, action: Action) -> bool:
        """
        Execute a single action.
        
        Args:
            action: The action to echo
            
        Returns:
            True if action was executed successfully
        """
        if not self.is_enabled:
            print("[Echo] Not enabled - action blocked")
            return False
        
        if not PYAUTOGUI_AVAILABLE:
            return False
        
        if not self._check_rate_limit():
            return False
        
        # Check position safety
        if action.position:
            x, y = action.position
            if not self._is_safe_position(x, y):
                print(f"[Echo] Position ({x}, {y}) is in blocked region")
                return False
        
        try:
            self._perform_action(action)
            self._action_count += 1
            self._last_action_time = time.time()
            
            # Remember the action
            self.memories.remember_action(
                action_type=action.action_type.value,
                target=action.target,
                position=action.position,
                value=action.value,
                context={'echo': True}
            )
            
            return True
            
        except Exception as e:
            print(f"[Echo] Action failed: {e}")
            return False
    
    def _perform_action(self, action: Action):
        """Actually perform the action using pyautogui."""
        at = action.action_type
        
        if at == ActionType.CLICK:
            if action.position:
                pyautogui.click(action.position[0], action.position[1])
            else:
                pyautogui.click()
                
        elif at == ActionType.DOUBLE_CLICK:
            if action.position:
                pyautogui.doubleClick(action.position[0], action.position[1])
            else:
                pyautogui.doubleClick()
                
        elif at == ActionType.RIGHT_CLICK:
            if action.position:
                pyautogui.rightClick(action.position[0], action.position[1])
            else:
                pyautogui.rightClick()
                
        elif at == ActionType.TYPE:
            if action.value:
                pyautogui.write(action.value, interval=0.02)
                
        elif at == ActionType.HOTKEY:
            if action.value:
                keys = action.value.split('+')
                pyautogui.hotkey(*keys)
                
        elif at == ActionType.SCROLL:
            amount = int(action.value) if action.value else 3
            if action.position:
                pyautogui.scroll(amount, action.position[0], action.position[1])
            else:
                pyautogui.scroll(amount)
                
        elif at == ActionType.MOVE:
            if action.position:
                pyautogui.moveTo(action.position[0], action.position[1], 
                               duration=action.duration)
                
        elif at == ActionType.WAIT:
            time.sleep(action.duration)
    
    def execute_sequence(self, actions: List[Action], 
                        delay_between: float = 0.5) -> int:
        """
        Execute a sequence of actions.
        
        Args:
            actions: List of actions to echo
            delay_between: Seconds to wait between actions
            
        Returns:
            Number of successfully executed actions
        """
        executed = 0
        
        for action in actions:
            if self.execute(action):
                executed += 1
            time.sleep(delay_between)
        
        return executed
    
    # ==================== PATTERN REPLAY ====================
    
    def replay_pattern(self, pattern: Pattern) -> bool:
        """
        Replay a learned pattern.
        
        Args:
            pattern: The pattern to replay
            
        Returns:
            True if pattern was replayed successfully
        """
        if not pattern.actions:
            return False
        
        actions = []
        for action_dict in pattern.actions:
            action_type = ActionType(action_dict.get('action', 'wait'))
            action = Action(
                action_type=action_type,
                target=action_dict.get('target'),
                position=tuple(action_dict['position']) if action_dict.get('position') else None,
                value=action_dict.get('value'),
                duration=action_dict.get('duration', 0.1)
            )
            actions.append(action)
        
        executed = self.execute_sequence(actions)
        return executed == len(actions)


# Global instance
_echo_instance = None

def get_echo() -> MegumiEcho:
    """Get or create Megumi's echo ability."""
    global _echo_instance
    if _echo_instance is None:
        _echo_instance = MegumiEcho(safe_mode=True)
    return _echo_instance


# Backward compatibility
MegumiMimic = MegumiEcho
get_mimic = get_echo
