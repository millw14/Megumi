"""
reading.py - Megumi's Reading Ability
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

She reads what she sees.
Text recognition from screen captures.
Every word on your screen, she can understand.
"""

import numpy as np
from PIL import Image
from typing import List, Tuple, Optional
import threading


class TextResult:
    """Represents a piece of text Megumi read."""
    
    def __init__(self, text: str, bbox: Tuple[int, int, int, int], 
                 confidence: float = 1.0):
        self.text = text
        self.bbox = bbox  # (x1, y1, x2, y2)
        self.confidence = confidence
    
    @property
    def x(self) -> int:
        return self.bbox[0]
    
    @property
    def y(self) -> int:
        return self.bbox[1]
    
    @property
    def width(self) -> int:
        return self.bbox[2] - self.bbox[0]
    
    @property
    def height(self) -> int:
        return self.bbox[3] - self.bbox[1]
    
    @property
    def center(self) -> Tuple[int, int]:
        return (
            (self.bbox[0] + self.bbox[2]) // 2,
            (self.bbox[1] + self.bbox[3]) // 2
        )
    
    def __repr__(self):
        return f"TextResult('{self.text[:30]}...', conf={self.confidence:.2f})"


class MegumiReading:
    """Megumi's ability to read - she understands text on screen."""
    
    def __init__(self, languages: List[str] = ['en'], use_gpu: bool = False):
        """
        Initialize her reading ability.
        
        Args:
            languages: List of language codes (e.g., ['en', 'ja'])
            use_gpu: Whether to use GPU acceleration
        """
        self.languages = languages
        self.use_gpu = use_gpu
        self._reader = None
        self._lock = threading.Lock()
        self._initialized = False
        
    def _ensure_initialized(self):
        """Lazy initialization of reading engine."""
        if self._initialized:
            return
        
        with self._lock:
            if self._initialized:
                return
            
            try:
                import easyocr
                print(f"[Reading] Initializing (languages: {self.languages}, GPU: {self.use_gpu})")
                self._reader = easyocr.Reader(
                    self.languages, 
                    gpu=self.use_gpu,
                    verbose=False
                )
                self._initialized = True
                print("[Reading] Ready to read")
            except ImportError:
                print("[Reading] EasyOCR not installed. Install with: pip install easyocr")
                raise
            except Exception as e:
                print(f"[Reading] Failed to initialize: {e}")
                raise
    
    def read_image(self, image: np.ndarray, 
                   detail: int = 1,
                   paragraph: bool = False,
                   min_confidence: float = 0.3) -> List[TextResult]:
        """
        Read text from an image.
        
        Args:
            image: numpy array (BGR or RGB)
            detail: 0 for simple output, 1 for detailed output
            paragraph: Whether to merge text into paragraphs
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of TextResult objects
        """
        self._ensure_initialized()
        
        # Convert BGRA to RGB if needed
        if len(image.shape) == 3:
            if image.shape[2] == 4:
                image = image[:, :, :3]
            # Assume BGR, convert to RGB
            image = image[:, :, ::-1]
        
        results = []
        
        try:
            raw_results = self._reader.readtext(
                image,
                detail=detail,
                paragraph=paragraph
            )
            
            for item in raw_results:
                if detail == 1:
                    bbox_points, text, confidence = item
                    
                    if confidence < min_confidence:
                        continue
                    
                    # Convert polygon points to bounding box
                    xs = [p[0] for p in bbox_points]
                    ys = [p[1] for p in bbox_points]
                    bbox = (int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys)))
                    
                    results.append(TextResult(text, bbox, confidence))
                else:
                    # detail=0 returns just text
                    results.append(TextResult(item, (0, 0, 0, 0), 1.0))
            
        except Exception as e:
            print(f"[Reading] Error reading image: {e}")
        
        return results
    
    def read_pil_image(self, image: Image.Image, **kwargs) -> List[TextResult]:
        """Read text from a PIL Image."""
        img_array = np.array(image)
        return self.read_image(img_array, **kwargs)
    
    def read_file(self, filepath: str, **kwargs) -> List[TextResult]:
        """Read text from an image file."""
        self._ensure_initialized()
        
        try:
            raw_results = self._reader.readtext(filepath, **kwargs)
            results = []
            
            for bbox_points, text, confidence in raw_results:
                xs = [p[0] for p in bbox_points]
                ys = [p[1] for p in bbox_points]
                bbox = (int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys)))
                results.append(TextResult(text, bbox, confidence))
            
            return results
        except Exception as e:
            print(f"[Reading] Error reading file: {e}")
            return []
    
    def read_all_text(self, image: np.ndarray, separator: str = ' ') -> str:
        """Get all text from image as a single string."""
        results = self.read_image(image, detail=0)
        return separator.join([r.text for r in results])
    
    def find_text(self, image: np.ndarray, search_text: str, 
                  case_sensitive: bool = False) -> List[TextResult]:
        """
        Find specific text in an image.
        
        Args:
            image: Image to search
            search_text: Text to find
            case_sensitive: Whether search is case-sensitive
            
        Returns:
            List of matching TextResult objects
        """
        results = self.read_image(image)
        matches = []
        
        for result in results:
            text = result.text if case_sensitive else result.text.lower()
            target = search_text if case_sensitive else search_text.lower()
            
            if target in text:
                matches.append(result)
        
        return matches


# Global instance
_reading_instance = None

def get_reading(languages: List[str] = ['en']) -> MegumiReading:
    """Get or create Megumi's reading ability."""
    global _reading_instance
    if _reading_instance is None:
        _reading_instance = MegumiReading(languages=languages)
    return _reading_instance


# Backward compatibility
ScreenReader = MegumiReading
get_reader = get_reading
