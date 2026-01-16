"""
Megumi Screen Watcher
~~~~~~~~~~~~~~~~~~~~~

Monitors the screen to see what the user is doing.
This is the "eyes" of Megumi.

Status: Phase 2 (Coming Soon)
"""

from dataclasses import dataclass
from typing import Optional, Tuple
import threading
import time


@dataclass
class ScreenRegion:
    """Defines a region of the screen to watch"""
    x: int
    y: int
    width: int
    height: int
    name: str = "unnamed"


class ScreenWatcher:
    """
    Watches the screen and captures what Megumi sees.
    
    Features (planned):
    - Full screen capture
    - Region-specific monitoring
    - Change detection
    - OCR text extraction
    - UI element recognition
    """
    
    def __init__(self):
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._capture_interval = 1.0  # seconds
        self._regions: list[ScreenRegion] = []
    
    def add_watch_region(self, region: ScreenRegion):
        """Add a specific region to monitor"""
        self._regions.append(region)
    
    def start(self):
        """Start watching the screen"""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._thread.start()
    
    def stop(self):
        """Stop watching"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
    
    def _watch_loop(self):
        """Main watching loop"""
        while self._running:
            # TODO: Implement actual screen capture
            # - Use mss for fast capture
            # - Process with OpenCV
            # - Extract text with EasyOCR
            # - Detect UI elements
            time.sleep(self._capture_interval)
    
    def capture_full_screen(self) -> Optional[bytes]:
        """Capture the entire screen"""
        # TODO: Implement with mss
        pass
    
    def capture_region(self, region: ScreenRegion) -> Optional[bytes]:
        """Capture a specific region"""
        # TODO: Implement with mss
        pass
    
    def detect_changes(self, previous: bytes, current: bytes) -> bool:
        """Detect if significant changes occurred"""
        # TODO: Implement with OpenCV
        pass
    
    def extract_text(self, image: bytes) -> list[str]:
        """Extract text from captured image"""
        # TODO: Implement with EasyOCR
        pass
