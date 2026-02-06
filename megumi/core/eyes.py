"""
eyes.py - Megumi's Eyes
~~~~~~~~~~~~~~~~~~~~~~~

She watches over you.
Screen capture and monitoring system.
Always watching. Always seeing.
"""

import mss
import mss.tools
import numpy as np
from PIL import Image
import io
import time
import threading
from datetime import datetime
from typing import Optional, Callable, Tuple
import ctypes
from ctypes import wintypes


class MegumiEyes:
    """Megumi's vision - captures and monitors screen content."""
    
    def __init__(self):
        self._sct = None  # Created per-thread
        self.is_watching = False
        self._watch_thread = None
        self._callbacks = []
        self._last_capture = None
        self._capture_interval = 1.0  # seconds
    
    @property
    def sct(self):
        """Get or create mss instance for current thread."""
        if self._sct is None:
            self._sct = mss.mss()
        return self._sct
        
    @property
    def monitors(self) -> list:
        """Get list of available monitors."""
        return self.sct.monitors
    
    @property
    def primary_monitor(self) -> dict:
        """Get primary monitor info."""
        # monitors[0] is the virtual screen (all monitors combined)
        # monitors[1] is usually the primary monitor
        return self.sct.monitors[1] if len(self.sct.monitors) > 1 else self.sct.monitors[0]
    
    def see(self, monitor: int = 1) -> np.ndarray:
        """
        See the entire screen or a specific monitor.
        
        Args:
            monitor: Monitor index (0 = all, 1 = primary, 2+ = secondary)
            
        Returns:
            numpy array of the screenshot (BGRA format)
        """
        mon = self.sct.monitors[monitor]
        screenshot = self.sct.grab(mon)
        
        # Convert to numpy array
        img = np.array(screenshot)
        self._last_capture = img
        
        return img
    
    def see_region(self, x: int, y: int, width: int, height: int) -> np.ndarray:
        """
        See a specific region of the screen.
        
        Args:
            x, y: Top-left corner coordinates
            width, height: Region dimensions
            
        Returns:
            numpy array of the screenshot
        """
        region = {"left": x, "top": y, "width": width, "height": height}
        screenshot = self.sct.grab(region)
        return np.array(screenshot)
    
    def see_as_pil(self, monitor: int = 1) -> Image.Image:
        """See screen and return as PIL Image."""
        img_array = self.see(monitor)
        # Convert BGRA to RGB
        img_rgb = img_array[:, :, :3][:, :, ::-1]
        return Image.fromarray(img_rgb)
    
    def see_as_bytes(self, monitor: int = 1, format: str = 'PNG') -> bytes:
        """See screen and return as bytes."""
        img = self.see_as_pil(monitor)
        buffer = io.BytesIO()
        img.save(buffer, format=format)
        return buffer.getvalue()
    
    def save_vision(self, filepath: str, monitor: int = 1):
        """Save what she sees to file."""
        img = self.see_as_pil(monitor)
        img.save(filepath)
        print(f"[Eyes] Saved vision to {filepath}")
    
    # ==================== ACTIVE WINDOW ====================
    
    def get_focus(self) -> Tuple[str, str]:
        """
        Get what the human is focusing on (active window).
        
        Returns:
            Tuple of (window_title, process_name)
        """
        try:
            # Windows API
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            
            # Get window title
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            buf = ctypes.create_unicode_buffer(length + 1)
            ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
            title = buf.value
            
            # Get process name
            pid = wintypes.DWORD()
            ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            
            process_name = self._get_process_name(pid.value)
            
            return (title, process_name)
        except Exception as e:
            print(f"[Eyes] Error getting focus: {e}")
            return ("Unknown", "Unknown")
    
    def _get_process_name(self, pid: int) -> str:
        """Get process name from PID."""
        try:
            import psutil
            process = psutil.Process(pid)
            return process.name()
        except:
            return "Unknown"
    
    # ==================== CONTINUOUS WATCHING ====================
    
    def add_callback(self, callback: Callable[[np.ndarray, dict], None]):
        """
        Add a callback for when new captures are made.
        
        Callback receives: (image_array, metadata_dict)
        """
        self._callbacks.append(callback)
    
    def remove_callback(self, callback: Callable):
        """Remove a callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def start_watching(self, interval: float = 1.0, monitor: int = 1):
        """
        Start watching over you.
        
        Args:
            interval: Seconds between captures
            monitor: Which monitor to watch
        """
        if self.is_watching:
            print("[Eyes] Already watching")
            return
        
        self._capture_interval = interval
        self.is_watching = True
        
        def watch_loop():
            # Create mss instance in this thread (required by mss)
            with mss.mss() as thread_sct:
                print(f"[Eyes] Started watching (interval: {interval}s)")
                while self.is_watching:
                    try:
                        # Capture screen using thread-local mss
                        mon = thread_sct.monitors[monitor]
                        screenshot = thread_sct.grab(mon)
                        img = np.array(screenshot)
                        self._last_capture = img
                        
                        # Get what human is focused on
                        title, process = self.get_focus()
                        
                        metadata = {
                            'timestamp': datetime.now().isoformat(),
                            'window_title': title,
                            'process_name': process,
                            'monitor': monitor,
                            'resolution': (img.shape[1], img.shape[0])
                        }
                        
                        # Notify callbacks
                        for callback in self._callbacks:
                            try:
                                callback(img, metadata)
                            except Exception as e:
                                print(f"[Eyes] Callback error: {e}")
                        
                        time.sleep(interval)
                        
                    except Exception as e:
                        print(f"[Eyes] Watch loop error: {e}")
                        time.sleep(interval)
                
                print("[Eyes] Stopped watching")
        
        self._watch_thread = threading.Thread(target=watch_loop, daemon=True)
        self._watch_thread.start()
    
    def stop_watching(self):
        """Stop watching."""
        self.is_watching = False
        if self._watch_thread:
            self._watch_thread.join(timeout=2)
            self._watch_thread = None
    
    def set_interval(self, interval: float):
        """Change capture interval while watching."""
        self._capture_interval = interval
    
    # ==================== CHANGE DETECTION ====================
    
    def detect_change(self, img1: np.ndarray, img2: np.ndarray, 
                      threshold: float = 0.1) -> Tuple[bool, float]:
        """
        Detect if significant change occurred between two captures.
        
        Args:
            img1, img2: Screenshot arrays to compare
            threshold: Percentage of pixels that must differ (0.0 to 1.0)
            
        Returns:
            Tuple of (has_changed, change_percentage)
        """
        if img1.shape != img2.shape:
            return (True, 1.0)
        
        # Calculate difference
        diff = np.abs(img1.astype(float) - img2.astype(float))
        
        # Consider a pixel changed if any channel differs by more than 10
        changed_pixels = np.any(diff > 10, axis=2)
        change_ratio = np.mean(changed_pixels)
        
        return (change_ratio > threshold, change_ratio)
    
    def close(self):
        """Close her eyes."""
        self.stop_watching()
        self.sct.close()


# Global instance
_eyes_instance = None

def get_eyes() -> MegumiEyes:
    """Get or create Megumi's eyes."""
    global _eyes_instance
    if _eyes_instance is None:
        _eyes_instance = MegumiEyes()
    return _eyes_instance


# Backward compatibility
ScreenWatcher = MegumiEyes
get_watcher = get_eyes
