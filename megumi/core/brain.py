"""
brain.py - Megumi's Brain
~~~~~~~~~~~~~~~~~~~~~~~~~

She understands meaning, not just words.
Semantic embedding system for intelligent pattern matching.

Uses sentence-transformers to convert text to meaning vectors.
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
import json
import os
from pathlib import Path

# Lazy load sentence-transformers (heavy import)
_model = None
_model_name = 'all-MiniLM-L6-v2'  # 80MB, good balance of size/quality


def _get_model():
    """Lazy load the embedding model."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            print(f"[Brain] Loading embedding model: {_model_name}")
            _model = SentenceTransformer(_model_name)
            print("[Brain] Model loaded successfully")
        except ImportError:
            print("[Brain] sentence-transformers not installed")
            print("[Brain] Install with: pip install sentence-transformers")
            return None
    return _model


class MegumiBrain:
    """
    Megumi's semantic understanding - she grasps meaning, not just words.
    
    Uses embeddings to find similar contexts and patterns even when
    the exact words are different.
    """
    
    def __init__(self, cache_dir: str = None):
        """
        Initialize Megumi's brain.
        
        Args:
            cache_dir: Directory to cache embeddings (defaults to data/embeddings)
        """
        if cache_dir is None:
            project_root = Path(__file__).parent.parent.parent
            cache_dir = project_root / "data" / "embeddings"
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory embedding cache
        self._embedding_cache: Dict[str, np.ndarray] = {}
        self._cache_file = self.cache_dir / "embedding_cache.json"
        
        # Load cached embeddings
        self._load_cache()
    
    def _load_cache(self):
        """Load cached embeddings from disk."""
        if self._cache_file.exists():
            try:
                with open(self._cache_file, 'r') as f:
                    data = json.load(f)
                    self._embedding_cache = {
                        k: np.array(v) for k, v in data.items()
                    }
                print(f"[Brain] Loaded {len(self._embedding_cache)} cached embeddings")
            except Exception as e:
                print(f"[Brain] Cache load error: {e}")
                self._embedding_cache = {}
    
    def _save_cache(self):
        """Save embedding cache to disk."""
        try:
            data = {k: v.tolist() for k, v in self._embedding_cache.items()}
            with open(self._cache_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"[Brain] Cache save error: {e}")
    
    def embed_text(self, text: str) -> Optional[np.ndarray]:
        """
        Convert text to an embedding vector.
        
        Args:
            text: Text to embed
            
        Returns:
            Numpy array of the embedding, or None if model unavailable
        """
        if not text or not text.strip():
            return None
        
        # Normalize text
        text = text.strip().lower()
        
        # Check cache first
        if text in self._embedding_cache:
            return self._embedding_cache[text]
        
        # Get model
        model = _get_model()
        if model is None:
            return None
        
        # Generate embedding
        try:
            embedding = model.encode(text, convert_to_numpy=True)
            
            # Cache it
            self._embedding_cache[text] = embedding
            
            # Periodically save cache
            if len(self._embedding_cache) % 100 == 0:
                self._save_cache()
            
            return embedding
        except Exception as e:
            print(f"[Brain] Embedding error: {e}")
            return None
    
    def embed_texts(self, texts: List[str]) -> List[Optional[np.ndarray]]:
        """
        Embed multiple texts efficiently (batched).
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings (None for failed ones)
        """
        if not texts:
            return []
        
        model = _get_model()
        if model is None:
            return [None] * len(texts)
        
        # Separate cached and uncached
        results = [None] * len(texts)
        uncached_indices = []
        uncached_texts = []
        
        for i, text in enumerate(texts):
            if not text or not text.strip():
                continue
            text = text.strip().lower()
            if text in self._embedding_cache:
                results[i] = self._embedding_cache[text]
            else:
                uncached_indices.append(i)
                uncached_texts.append(text)
        
        # Batch encode uncached texts
        if uncached_texts:
            try:
                embeddings = model.encode(uncached_texts, convert_to_numpy=True)
                for idx, text, emb in zip(uncached_indices, uncached_texts, embeddings):
                    self._embedding_cache[text] = emb
                    results[idx] = emb
                self._save_cache()
            except Exception as e:
                print(f"[Brain] Batch embedding error: {e}")
        
        return results
    
    def compute_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings.
        
        Args:
            emb1, emb2: Embedding vectors
            
        Returns:
            Similarity score between -1 and 1 (higher = more similar)
        """
        if emb1 is None or emb2 is None:
            return 0.0
        
        # Cosine similarity
        dot_product = np.dot(emb1, emb2)
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    def find_similar_texts(self, query: str, candidates: List[str], 
                          threshold: float = 0.5, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Find texts similar to the query.
        
        Args:
            query: The query text
            candidates: List of candidate texts to search
            threshold: Minimum similarity score (0-1)
            top_k: Maximum number of results
            
        Returns:
            List of (text, similarity) tuples, sorted by similarity
        """
        query_emb = self.embed_text(query)
        if query_emb is None:
            return []
        
        candidate_embs = self.embed_texts(candidates)
        
        results = []
        for text, emb in zip(candidates, candidate_embs):
            if emb is not None:
                sim = self.compute_similarity(query_emb, emb)
                if sim >= threshold:
                    results.append((text, sim))
        
        # Sort by similarity (descending)
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def create_context_embedding(self, window_title: str = None,
                                 process_name: str = None,
                                 visible_texts: List[str] = None) -> Optional[np.ndarray]:
        """
        Create a combined embedding for a context (window + visible text).
        
        Args:
            window_title: Active window title
            process_name: Process name
            visible_texts: Texts visible on screen
            
        Returns:
            Combined embedding representing the context
        """
        parts = []
        
        if window_title:
            parts.append(f"window: {window_title}")
        if process_name:
            parts.append(f"app: {process_name}")
        if visible_texts:
            # Take first few significant texts
            significant = [t for t in visible_texts if len(t) > 3][:5]
            if significant:
                parts.append(f"content: {' '.join(significant)}")
        
        if not parts:
            return None
        
        context_text = " | ".join(parts)
        return self.embed_text(context_text)
    
    def contexts_are_similar(self, context1: Dict, context2: Dict, 
                            threshold: float = 0.7) -> bool:
        """
        Check if two contexts are semantically similar.
        
        Args:
            context1, context2: Context dicts with window_title, process_name, texts
            threshold: Similarity threshold
            
        Returns:
            True if contexts are similar
        """
        emb1 = self.create_context_embedding(
            window_title=context1.get('window_title'),
            process_name=context1.get('process_name'),
            visible_texts=context1.get('texts', [])
        )
        
        emb2 = self.create_context_embedding(
            window_title=context2.get('window_title'),
            process_name=context2.get('process_name'),
            visible_texts=context2.get('texts', [])
        )
        
        if emb1 is None or emb2 is None:
            return False
        
        return self.compute_similarity(emb1, emb2) >= threshold
    
    def close(self):
        """Save cache and cleanup."""
        self._save_cache()
        print("[Brain] Closed and saved cache")


# Global instance
_brain_instance = None


def get_brain() -> MegumiBrain:
    """Get or create Megumi's brain."""
    global _brain_instance
    if _brain_instance is None:
        _brain_instance = MegumiBrain()
    return _brain_instance
