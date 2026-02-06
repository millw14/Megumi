"""
senses.py - Megumi's Senses
~~~~~~~~~~~~~~~~~~~~~~~~~~~

She feels what you do.
Input capture for keyboard, mouse, and controller.
Each action is recorded to learn your patterns.

Privacy: Everything stays local. Always.
"""

import time
import threading
from datetime import datetime
from typing import Optional, Callable, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import deque

try:
    from pynput import keyboard, mouse
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    print("[Senses] pynput not installed - input capture disabled")
    print("[Senses] Install with: pip install pynput")


class InputType(Enum):
    """Types of input Megumi can sense."""
    KEY_PRESS = "key_press"
    KEY_RELEASE = "key_release"
    MOUSE_CLICK = "mouse_click"
    MOUSE_RELEASE = "mouse_release"
    MOUSE_MOVE = "mouse_move"
    MOUSE_SCROLL = "mouse_scroll"


@dataclass
class InputEvent:
    """A single input event - one moment of action."""
    input_type: InputType
    timestamp: str
    data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'type': self.input_type.value,
            'timestamp': self.timestamp,
            **self.data
        }


@dataclass 
class ActionFrame:
    """
    A frame of action - what happened in a moment.
    This pairs with a State (screen capture) for learning.
    """
    timestamp: str
    keys_pressed: List[str] = field(default_factory=list)
    mouse_position: Optional[tuple] = None
    mouse_clicks: List[Dict] = field(default_factory=list)
    scroll_delta: int = 0
    
    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp,
            'keys_pressed': self.keys_pressed,
            'mouse_position': self.mouse_position,
            'mouse_clicks': self.mouse_clicks,
            'scroll_delta': self.scroll_delta
        }


class MegumiSenses:
    """
    Megumi's input senses - she feels your keyboard and mouse.
    
    Privacy features:
    - Password mode detection (pauses on password fields)
    - Configurable key masking
    - All data stays local
    """
    
    def __init__(self):
        self.is_sensing = False
        self._keyboard_listener = None
        self._mouse_listener = None
        
        # Current state
        self._keys_held: set = set()
        self._mouse_position: tuple = (0, 0)
        self._last_click: Optional[Dict] = None
        
        # Event buffer (recent events for building ActionFrames)
        self._event_buffer: deque = deque(maxlen=1000)
        self._action_callbacks: List[Callable] = []
        
        # Privacy settings
        self.mask_passwords = True
        self.mask_keys = False  # If True, only record key events, not which keys
        self._password_mode = False
        
        # Sensitive key patterns to detect password fields
        self._password_indicators = ['password', 'passwd', 'secret', 'pin']
        
        # Movement tracking
        self._last_move_time = 0
        self._move_throttle = 0.05  # Only record mouse moves every 50ms
        
        if not PYNPUT_AVAILABLE:
            print("[Senses] Cannot initialize - pynput not available")
    
    # ==================== SENSING CONTROL ====================
    
    def start_sensing(self):
        """Start sensing input - she begins to feel."""
        if not PYNPUT_AVAILABLE:
            print("[Senses] Cannot start - pynput not installed")
            return False
        
        if self.is_sensing:
            print("[Senses] Already sensing")
            return True
        
        self.is_sensing = True
        self._keys_held.clear()
        
        # Start keyboard listener
        self._keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release
        )
        self._keyboard_listener.start()
        
        # Start mouse listener
        self._mouse_listener = mouse.Listener(
            on_click=self._on_mouse_click,
            on_move=self._on_mouse_move,
            on_scroll=self._on_mouse_scroll
        )
        self._mouse_listener.start()
        
        print("[Senses] Started sensing input")
        return True
    
    def stop_sensing(self):
        """Stop sensing input - she rests."""
        if not self.is_sensing:
            return
        
        self.is_sensing = False
        
        if self._keyboard_listener:
            self._keyboard_listener.stop()
            self._keyboard_listener = None
        
        if self._mouse_listener:
            self._mouse_listener.stop()
            self._mouse_listener = None
        
        self._keys_held.clear()
        print("[Senses] Stopped sensing")
    
    def add_action_callback(self, callback: Callable[[InputEvent], None]):
        """Add callback for when actions are sensed."""
        self._action_callbacks.append(callback)
    
    def remove_action_callback(self, callback: Callable):
        """Remove an action callback."""
        if callback in self._action_callbacks:
            self._action_callbacks.remove(callback)
    
    # ==================== KEYBOARD HANDLING ====================
    
    def _on_key_press(self, key):
        """Handle key press."""
        if not self.is_sensing:
            return
        
        try:
            # Get key name
            if hasattr(key, 'char') and key.char:
                key_name = key.char
            else:
                key_name = str(key).replace('Key.', '')
            
            # Skip if in password mode and masking is on
            if self._password_mode and self.mask_passwords:
                key_name = '*'
            
            # Mask all keys if configured
            if self.mask_keys:
                key_name = 'key'
            
            self._keys_held.add(key_name)
            
            event = InputEvent(
                input_type=InputType.KEY_PRESS,
                timestamp=datetime.now().isoformat(),
                data={
                    'key': key_name,
                    'modifiers': list(self._get_modifiers())
                }
            )
            
            self._record_event(event)
            
        except Exception as e:
            print(f"[Senses] Key press error: {e}")
    
    def _on_key_release(self, key):
        """Handle key release."""
        if not self.is_sensing:
            return
        
        try:
            if hasattr(key, 'char') and key.char:
                key_name = key.char
            else:
                key_name = str(key).replace('Key.', '')
            
            self._keys_held.discard(key_name)
            
            # Don't record releases in masked mode
            if self.mask_keys or (self._password_mode and self.mask_passwords):
                return
            
            event = InputEvent(
                input_type=InputType.KEY_RELEASE,
                timestamp=datetime.now().isoformat(),
                data={'key': key_name}
            )
            
            self._record_event(event)
            
        except Exception as e:
            print(f"[Senses] Key release error: {e}")
    
    def _get_modifiers(self) -> set:
        """Get currently held modifier keys."""
        modifiers = set()
        modifier_names = ['ctrl', 'alt', 'shift', 'cmd', 'ctrl_l', 'ctrl_r', 
                         'alt_l', 'alt_r', 'shift_l', 'shift_r']
        for key in self._keys_held:
            if key.lower() in modifier_names:
                modifiers.add(key.lower())
        return modifiers
    
    # ==================== MOUSE HANDLING ====================
    
    def _on_mouse_click(self, x, y, button, pressed):
        """Handle mouse click."""
        if not self.is_sensing:
            return
        
        try:
            button_name = str(button).replace('Button.', '')
            
            event = InputEvent(
                input_type=InputType.MOUSE_CLICK if pressed else InputType.MOUSE_RELEASE,
                timestamp=datetime.now().isoformat(),
                data={
                    'x': x,
                    'y': y,
                    'button': button_name,
                    'pressed': pressed
                }
            )
            
            if pressed:
                self._last_click = event.data.copy()
            
            self._record_event(event)
            
        except Exception as e:
            print(f"[Senses] Mouse click error: {e}")
    
    def _on_mouse_move(self, x, y):
        """Handle mouse movement (throttled)."""
        if not self.is_sensing:
            return
        
        # Throttle move events
        now = time.time()
        if now - self._last_move_time < self._move_throttle:
            self._mouse_position = (x, y)
            return
        
        self._last_move_time = now
        self._mouse_position = (x, y)
        
        # Only record significant moves (not every tiny movement)
        event = InputEvent(
            input_type=InputType.MOUSE_MOVE,
            timestamp=datetime.now().isoformat(),
            data={'x': x, 'y': y}
        )
        
        self._record_event(event)
    
    def _on_mouse_scroll(self, x, y, dx, dy):
        """Handle mouse scroll."""
        if not self.is_sensing:
            return
        
        try:
            event = InputEvent(
                input_type=InputType.MOUSE_SCROLL,
                timestamp=datetime.now().isoformat(),
                data={
                    'x': x,
                    'y': y,
                    'dx': dx,
                    'dy': dy
                }
            )
            
            self._record_event(event)
            
        except Exception as e:
            print(f"[Senses] Mouse scroll error: {e}")
    
    # ==================== EVENT RECORDING ====================
    
    def _record_event(self, event: InputEvent):
        """Record an event and notify callbacks."""
        self._event_buffer.append(event)
        
        for callback in self._action_callbacks:
            try:
                callback(event)
            except Exception as e:
                print(f"[Senses] Callback error: {e}")
    
    def get_current_action_frame(self) -> ActionFrame:
        """
        Get current action state as an ActionFrame.
        This can be paired with a screen capture for learning.
        """
        # Collect recent clicks (last 100ms)
        now = datetime.now()
        recent_clicks = []
        
        for event in reversed(self._event_buffer):
            if event.input_type == InputType.MOUSE_CLICK:
                recent_clicks.append(event.data)
                if len(recent_clicks) >= 5:  # Max 5 recent clicks
                    break
        
        return ActionFrame(
            timestamp=now.isoformat(),
            keys_pressed=list(self._keys_held),
            mouse_position=self._mouse_position,
            mouse_clicks=recent_clicks,
            scroll_delta=0  # Could track this too
        )
    
    def get_recent_events(self, count: int = 100) -> List[InputEvent]:
        """Get recent input events."""
        return list(self._event_buffer)[-count:]
    
    # ==================== PRIVACY ====================
    
    def set_password_mode(self, enabled: bool):
        """Enable/disable password masking mode."""
        if self._password_mode != enabled:
            self._password_mode = enabled
            if enabled:
                print("[Senses] Password mode ON - keys masked")
    
    def detect_password_field(self, window_title: str) -> bool:
        """Detect if current window might have a password field."""
        title_lower = window_title.lower()
        for indicator in self._password_indicators:
            if indicator in title_lower:
                return True
        return False
    
    # ==================== CLEANUP ====================
    
    def close(self):
        """Clean up resources."""
        self.stop_sensing()
        self._event_buffer.clear()
        self._action_callbacks.clear()


# Global instance
_senses_instance = None

def get_senses() -> MegumiSenses:
    """Get or create Megumi's senses."""
    global _senses_instance
    if _senses_instance is None:
        _senses_instance = MegumiSenses()
    return _senses_instance
