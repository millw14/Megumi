"""
Megumi Mimic Engine
~~~~~~~~~~~~~~~~~~~

Replays learned patterns to mimic user activity.
This is the "hands" of Megumi.

Status: Phase 5 (Planned)

WARNING: This module can control your computer.
Safety features are critical!
"""

from dataclasses import dataclass
from typing import Optional, Callable
from enum import Enum
import time


class MimicMode(Enum):
    """Operating modes for the mimic engine"""
    DISABLED = "disabled"      # No actions allowed
    PREVIEW = "preview"        # Show what would happen, don't execute
    CONFIRM = "confirm"        # Ask before each action
    AUTONOMOUS = "autonomous"  # Full auto (dangerous!)


class SafetyLevel(Enum):
    """Safety restriction levels"""
    PARANOID = "paranoid"   # Only whitelisted apps, no typing
    CAUTIOUS = "cautious"   # No sensitive apps, limited typing
    NORMAL = "normal"       # Blacklist only
    UNRESTRICTED = "unrestricted"  # Full access (dangerous!)


@dataclass
class MimicAction:
    """A single action to perform"""
    action_type: str
    target: dict
    delay_before: float = 0.0
    
    
class MimicEngine:
    """
    Executes learned patterns to mimic user behavior.
    
    Safety Features:
    - Kill switch (Ctrl+Shift+Escape)
    - Action whitelist/blacklist
    - Sensitive area blocking
    - Action logging
    - Preview mode
    - Confirmation dialogs
    """
    
    # Apps that should NEVER be automated
    BLACKLIST_APPS = [
        "banking", "bank", "paypal", "venmo", "cashapp",
        "password", "1password", "lastpass", "bitwarden",
        "authenticator", "2fa",
    ]
    
    def __init__(self):
        self._mode = MimicMode.DISABLED
        self._safety_level = SafetyLevel.CAUTIOUS
        self._kill_switch_pressed = False
        self._action_log: list[dict] = []
        self._whitelist: set[str] = set()
        self._on_action_callback: Optional[Callable] = None
    
    @property
    def mode(self) -> MimicMode:
        return self._mode
    
    @mode.setter  
    def mode(self, value: MimicMode):
        if value == MimicMode.AUTONOMOUS:
            print("WARNING: Autonomous mode enabled. Megumi can now control your PC!")
        self._mode = value
    
    def register_kill_switch(self):
        """Register global hotkey for emergency stop"""
        # TODO: Implement with pynput or keyboard library
        # Hotkey: Ctrl+Shift+Escape
        pass
    
    def kill(self):
        """Emergency stop - immediately halt all actions"""
        self._kill_switch_pressed = True
        self._mode = MimicMode.DISABLED
        print("KILL SWITCH ACTIVATED - All actions stopped")
    
    def is_safe_target(self, target: str) -> bool:
        """Check if target app/window is safe to interact with"""
        target_lower = target.lower()
        
        # Check blacklist
        for blocked in self.BLACKLIST_APPS:
            if blocked in target_lower:
                return False
        
        # Check whitelist if in paranoid mode
        if self._safety_level == SafetyLevel.PARANOID:
            return target in self._whitelist
        
        return True
    
    def execute_action(self, action: MimicAction) -> bool:
        """Execute a single mimic action"""
        if self._kill_switch_pressed:
            return False
        
        if self._mode == MimicMode.DISABLED:
            return False
        
        # Safety check
        target_name = action.target.get("window", "")
        if not self.is_safe_target(target_name):
            self._log_action(action, "BLOCKED", "Unsafe target")
            return False
        
        # Preview mode - just log
        if self._mode == MimicMode.PREVIEW:
            self._log_action(action, "PREVIEW", "Would execute")
            if self._on_action_callback:
                self._on_action_callback(action, "preview")
            return True
        
        # Confirm mode - ask user
        if self._mode == MimicMode.CONFIRM:
            # TODO: Show confirmation dialog
            pass
        
        # Execute the action
        time.sleep(action.delay_before)
        success = self._do_action(action)
        self._log_action(action, "EXECUTED" if success else "FAILED")
        
        return success
    
    def _do_action(self, action: MimicAction) -> bool:
        """Actually perform the action"""
        # TODO: Implement with pyautogui
        # - click: pyautogui.click(x, y)
        # - type: pyautogui.typewrite(text)
        # - scroll: pyautogui.scroll(amount)
        # - hotkey: pyautogui.hotkey(*keys)
        return False
    
    def _log_action(self, action: MimicAction, status: str, note: str = ""):
        """Log an action for audit trail"""
        import datetime
        self._action_log.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "action": action.action_type,
            "target": action.target,
            "status": status,
            "note": note
        })
    
    def get_action_log(self) -> list[dict]:
        """Get the action audit log"""
        return self._action_log.copy()
