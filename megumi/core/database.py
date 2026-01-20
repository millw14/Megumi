"""
database.py - Megumi's Memory Bank

SQLite database for storing everything Megumi observes.
She remembers everything. Forever.
"""

import sqlite3
import os
import json
from datetime import datetime
from pathlib import Path


class MegumiDatabase:
    """Megumi's persistent memory storage."""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Default to data folder in project root
            project_root = Path(__file__).parent.parent.parent
            data_dir = project_root / "data"
            data_dir.mkdir(exist_ok=True)
            db_path = str(data_dir / "megumi.db")
        
        self.db_path = db_path
        self.conn = None
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables."""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        
        cursor = self.conn.cursor()
        
        # Screenshots and screen captures
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS observations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                observation_type TEXT NOT NULL,
                active_window TEXT,
                window_title TEXT,
                screen_region TEXT,
                data TEXT,
                metadata TEXT
            )
        """)
        
        # OCR text captures
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS text_captures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                observation_id INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                text_content TEXT,
                confidence REAL,
                bounding_box TEXT,
                FOREIGN KEY (observation_id) REFERENCES observations(id)
            )
        """)
        
        # Detected UI elements
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ui_elements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                observation_id INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                element_type TEXT,
                label TEXT,
                position TEXT,
                size TEXT,
                confidence REAL,
                FOREIGN KEY (observation_id) REFERENCES observations(id)
            )
        """)
        
        # User actions (clicks, typing, etc.)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                action_type TEXT NOT NULL,
                target_element TEXT,
                position TEXT,
                value TEXT,
                context TEXT
            )
        """)
        
        # Learned patterns
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                pattern_type TEXT NOT NULL,
                pattern_name TEXT,
                trigger_conditions TEXT,
                action_sequence TEXT,
                frequency INTEGER DEFAULT 1,
                confidence REAL DEFAULT 0.5
            )
        """)
        
        # Session tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                ended_at DATETIME,
                total_observations INTEGER DEFAULT 0,
                total_actions INTEGER DEFAULT 0,
                summary TEXT
            )
        """)
        
        self.conn.commit()
        print(f"[Database] Initialized at {self.db_path}")
    
    # ==================== OBSERVATIONS ====================
    
    def save_observation(self, obs_type: str, active_window: str = None,
                        window_title: str = None, data: dict = None,
                        metadata: dict = None) -> int:
        """Save a screen observation."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO observations (observation_type, active_window, window_title, data, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (
            obs_type,
            active_window,
            window_title,
            json.dumps(data) if data else None,
            json.dumps(metadata) if metadata else None
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_recent_observations(self, limit: int = 100) -> list:
        """Get recent observations."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM observations 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]
    
    # ==================== TEXT CAPTURES ====================
    
    def save_text_capture(self, observation_id: int, text: str,
                         confidence: float = 1.0, bbox: tuple = None) -> int:
        """Save OCR text capture."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO text_captures (observation_id, text_content, confidence, bounding_box)
            VALUES (?, ?, ?, ?)
        """, (
            observation_id,
            text,
            confidence,
            json.dumps(bbox) if bbox else None
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def search_text(self, query: str, limit: int = 50) -> list:
        """Search through captured text."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT tc.*, o.active_window, o.window_title, o.timestamp as obs_time
            FROM text_captures tc
            JOIN observations o ON tc.observation_id = o.id
            WHERE tc.text_content LIKE ?
            ORDER BY tc.timestamp DESC
            LIMIT ?
        """, (f"%{query}%", limit))
        return [dict(row) for row in cursor.fetchall()]
    
    # ==================== UI ELEMENTS ====================
    
    def save_ui_element(self, observation_id: int, element_type: str,
                       label: str = None, position: tuple = None,
                       size: tuple = None, confidence: float = 1.0) -> int:
        """Save detected UI element."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO ui_elements (observation_id, element_type, label, position, size, confidence)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            observation_id,
            element_type,
            label,
            json.dumps(position) if position else None,
            json.dumps(size) if size else None,
            confidence
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    # ==================== ACTIONS ====================
    
    def save_action(self, action_type: str, target: str = None,
                   position: tuple = None, value: str = None,
                   context: dict = None) -> int:
        """Save a user action."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO actions (action_type, target_element, position, value, context)
            VALUES (?, ?, ?, ?, ?)
        """, (
            action_type,
            target,
            json.dumps(position) if position else None,
            value,
            json.dumps(context) if context else None
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_recent_actions(self, limit: int = 100) -> list:
        """Get recent user actions."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM actions
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]
    
    # ==================== PATTERNS ====================
    
    def save_pattern(self, pattern_type: str, pattern_name: str,
                    trigger_conditions: dict, action_sequence: list,
                    confidence: float = 0.5) -> int:
        """Save a learned pattern."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO patterns (pattern_type, pattern_name, trigger_conditions, action_sequence, confidence)
            VALUES (?, ?, ?, ?, ?)
        """, (
            pattern_type,
            pattern_name,
            json.dumps(trigger_conditions),
            json.dumps(action_sequence),
            confidence
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def update_pattern_frequency(self, pattern_id: int):
        """Increment pattern frequency when observed again."""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE patterns 
            SET frequency = frequency + 1, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (pattern_id,))
        self.conn.commit()
    
    def get_patterns(self, pattern_type: str = None, min_confidence: float = 0) -> list:
        """Get learned patterns."""
        cursor = self.conn.cursor()
        if pattern_type:
            cursor.execute("""
                SELECT * FROM patterns
                WHERE pattern_type = ? AND confidence >= ?
                ORDER BY frequency DESC, confidence DESC
            """, (pattern_type, min_confidence))
        else:
            cursor.execute("""
                SELECT * FROM patterns
                WHERE confidence >= ?
                ORDER BY frequency DESC, confidence DESC
            """, (min_confidence,))
        return [dict(row) for row in cursor.fetchall()]
    
    # ==================== SESSIONS ====================
    
    def start_session(self) -> int:
        """Start a new observation session."""
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO sessions DEFAULT VALUES")
        self.conn.commit()
        return cursor.lastrowid
    
    def end_session(self, session_id: int, summary: str = None):
        """End an observation session."""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE sessions 
            SET ended_at = CURRENT_TIMESTAMP, summary = ?
            WHERE id = ?
        """, (summary, session_id))
        self.conn.commit()
    
    # ==================== STATS ====================
    
    def get_stats(self) -> dict:
        """Get database statistics."""
        cursor = self.conn.cursor()
        
        stats = {}
        
        cursor.execute("SELECT COUNT(*) FROM observations")
        stats['total_observations'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM text_captures")
        stats['total_text_captures'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM ui_elements")
        stats['total_ui_elements'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM actions")
        stats['total_actions'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM patterns")
        stats['total_patterns'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM sessions")
        stats['total_sessions'] = cursor.fetchone()[0]
        
        return stats
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            print("[Database] Connection closed")


# Global instance
_db_instance = None

def get_database() -> MegumiDatabase:
    """Get or create the global database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = MegumiDatabase()
    return _db_instance
