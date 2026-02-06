"""
presence.py - Megumi's Presence
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Her presence on your desktop.
The floating, transparent, always-on-top window
that lets Megumi exist in your world.

She watches. She learns. She grows.
"""

import sys
import os
import threading
import http.server
import socketserver
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import QApplication, QWidget, QMenu
from PySide6.QtCore import Qt, QPoint, QUrl, QTimer
from PySide6.QtGui import QAction, QCursor
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings

# Core imports (cute names!)
from ..core.memories import get_memories
from ..core.eyes import get_eyes
from ..core.senses import get_senses
from ..core.heart import get_heart
from ..core.feedback import get_feedback, FeedbackType
from ..core.prediction import get_prediction


class SilentHTTPHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler that serves files without logging"""
    
    def log_message(self, format, *args):
        pass  # Silence is golden
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()


class MegumiPresence(QWidget):
    """
    Megumi's presence on your desktop.
    
    Features:
    - Frameless transparent window
    - Always stays on top
    - Draggable anywhere
    - VRM character with cursor tracking
    - Right-click context menu
    - Screen watching and learning
    """
    
    def __init__(
        self,
        width: int = 250,
        height: int = 350,
        port: int = 9998
    ):
        super().__init__()
        
        self._drag_pos = QPoint()
        self._server_port = port
        self._server_thread: Optional[threading.Thread] = None
        
        # Get paths
        self._megumi_root = Path(__file__).parent.parent.parent.resolve()
        self._assets_path = self._megumi_root / "assets"
        self._vrm_path = self._assets_path / "models" / "megumi_chan.vrm"
        
        # Initialize her mind
        self._is_watching = False
        self._memories = get_memories()
        self._eyes = get_eyes()
        self._senses = get_senses()
        self._heart = get_heart()
        
        # Connect everything to heart
        self._heart.eyes = self._eyes
        self._heart.senses = self._senses
        
        # Initialize feedback and prediction
        self._feedback = get_feedback()
        self._prediction = get_prediction()
        
        # Set up watching callback
        self._eyes.add_callback(self._on_see)
        
        # Window setup
        self.setWindowTitle("Megumi")
        self.setFixedSize(width, height)
        
        # Frameless, transparent, always-on-top, hidden from taskbar
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Start file server
        self._start_server()
        
        # Create web view for VRM
        self._web = QWebEngineView(self)
        self._web.setGeometry(0, 0, width, height)
        self._web.page().setBackgroundColor(Qt.transparent)
        
        # Enable WebGL
        settings = self._web.settings()
        settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        
        # Load viewer after server starts
        QTimer.singleShot(500, self._load_soul)
        
        # Position bottom-right
        self._position_at_corner()
        
        # Context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_menu)
        
        # Global cursor tracking
        self._screen = QApplication.primaryScreen().geometry()
        self._cursor_timer = QTimer(self)
        self._cursor_timer.timeout.connect(self._update_cursor)
        self._cursor_timer.start(16)  # ~60 FPS
        
        # Feedback check timer (check every 30 seconds)
        self._feedback_timer = QTimer(self)
        self._feedback_timer.timeout.connect(self._check_for_feedback)
        self._feedback_timer.start(30000)
        
        print("[Presence] Megumi has manifested")
        print(f"[Presence] Memories: {self._memories.db_path}")
        
        # Auto-start watching after a short delay (let UI load first)
        QTimer.singleShot(2000, self._auto_start_watching)
    
    def _auto_start_watching(self):
        """Automatically start watching - she's always observing"""
        self.start_watching(interval=2.0)
        print("[Presence] Auto-started watching (always learning)")
    
    def _start_server(self):
        """Start local HTTP server for assets"""
        def run():
            os.chdir(self._megumi_root)
            with socketserver.TCPServer(("", self._server_port), SilentHTTPHandler) as httpd:
                httpd.serve_forever()
        
        self._server_thread = threading.Thread(target=run, daemon=True)
        self._server_thread.start()
    
    def _load_soul(self):
        """Load Megumi's visual soul (VRM viewer)"""
        url = f"http://localhost:{self._server_port}/megumi/ui/soul.html"
        self._web.setUrl(QUrl(url))
    
    def _position_at_corner(self):
        """Position at bottom-right corner"""
        screen = QApplication.primaryScreen().geometry()
        x = screen.width() - self.width() - 20
        y = screen.height() - self.height() - 60
        self.move(x, y)
    
    def _update_cursor(self):
        """Send global cursor position to viewer"""
        pos = QCursor.pos()
        
        # Normalize to -1 to +1
        # X: -1 = left edge, +1 = right edge
        # Y: +1 = top edge, -1 = bottom edge (inverted for natural look direction)
        norm_x = (pos.x() / self._screen.width()) * 2 - 1
        norm_y = 1 - (pos.y() / self._screen.height()) * 2
        
        # Send to JavaScript
        js = f"if(window.setGlobalMouse) window.setGlobalMouse({norm_x}, {norm_y});"
        self._web.page().runJavaScript(js)
    
    # ==================== WATCHING ====================
    
    def _on_see(self, image, metadata):
        """Callback when Megumi sees something"""
        self._heart.observe(image, metadata)
    
    def start_watching(self, interval: float = 2.0):
        """Start watching over you - she sees and feels everything"""
        if self._is_watching:
            return
        
        self._is_watching = True
        self._heart.start_learning()
        self._eyes.start_watching(interval=interval)
        self._senses.start_sensing()  # Start feeling your input
        
        # Visual feedback - watching mode glow
        js = "if(window.setWatchingMode) window.setWatchingMode(true);"
        self._web.page().runJavaScript(js)
        
        print("[Presence] Started watching (eyes + senses)...")
    
    def stop_watching(self):
        """Stop watching"""
        if not self._is_watching:
            return
        
        self._is_watching = False
        self._eyes.stop_watching()
        self._senses.stop_sensing()  # Stop feeling input
        self._heart.stop_learning()
        
        # Visual feedback
        js = "if(window.setWatchingMode) window.setWatchingMode(false);"
        self._web.page().runJavaScript(js)
        
        pairs = self._heart.total_pairs_collected
        print(f"[Presence] Stopped watching (collected {pairs} state-action pairs)")
    
    def toggle_watching(self):
        """Toggle watching mode"""
        if self._is_watching:
            self.stop_watching()
        else:
            self.start_watching()
    
    def get_stats(self):
        """Get memory statistics"""
        return self._memories.get_stats()
    
    def _check_for_feedback(self):
        """Check for patterns that need user feedback."""
        if not self._is_watching:
            return
        
        self._feedback.check_patterns_for_questions()
        questions = self._feedback.get_pending_questions(max_count=1)
        
        if questions:
            # Show notification in console for now
            # TODO: Implement toast notification UI
            q = questions[0]
            print(f"[Feedback] Megumi asks: {q.description}")
    
    def _show_learned_patterns(self):
        """Show what Megumi has learned in a dialog."""
        from PySide6.QtWidgets import QMessageBox
        
        patterns = self._heart.get_learned_patterns(min_confidence=0.3)
        
        if not patterns:
            text = "I haven't learned any patterns yet!\n\nKeep using your computer and I'll start noticing your habits."
        else:
            lines = ["Here's what I've learned about you:\n"]
            
            # Group by type
            by_type = {}
            for p in patterns[:15]:  # Limit to 15 patterns
                ptype = p.pattern_type.replace('_', ' ').title()
                if ptype not in by_type:
                    by_type[ptype] = []
                by_type[ptype].append(p)
            
            for ptype, plist in by_type.items():
                lines.append(f"\n{ptype}:")
                for p in plist[:5]:  # Limit per type
                    explanation = self._feedback.explain_pattern({
                        'pattern_type': p.pattern_type,
                        'trigger_conditions': str(p.triggers),
                        'action_sequence': str(p.actions),
                        'confidence': p.confidence
                    })
                    conf_pct = int(p.confidence * 100)
                    lines.append(f"  • {explanation} ({conf_pct}% confident)")
            
            text = "\n".join(lines)
        
        msg = QMessageBox(self)
        msg.setWindowTitle("What Megumi Has Learned")
        msg.setText(text)
        msg.setStyleSheet("""
            QMessageBox {
                background: #1a1a2e;
                color: #fff;
            }
            QMessageBox QLabel {
                color: #fff;
                font-size: 13px;
            }
            QPushButton {
                background: #ff6b9d;
                color: #fff;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
            }
        """)
        msg.exec()
    
    # ==================== MENU ====================
    
    def _show_menu(self, pos):
        """Show right-click menu"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background: #1a1a2e;
                color: #fff;
                border: 2px solid #ff6b9d;
                border-radius: 10px;
                padding: 8px;
                font-family: 'Segoe UI', sans-serif;
            }
            QMenu::item {
                padding: 10px 25px;
                border-radius: 6px;
                margin: 2px 0;
            }
            QMenu::item:selected {
                background: linear-gradient(135deg, #ff6b9d, #c44569);
            }
            QMenu::separator {
                height: 1px;
                background: #333;
                margin: 5px 10px;
            }
        """)
        
        # Status display
        pairs = self._heart.total_pairs_collected
        stats = self.get_stats()
        
        status_text = "Always Watching" if self._is_watching else "Paused"
        status_action = menu.addAction(f"Status: {status_text}")
        status_action.setEnabled(False)
        
        # Stats
        stats_action = menu.addAction(
            f"Learned: {pairs} moments | {stats['total_patterns']} patterns"
        )
        stats_action.setEnabled(False)
        
        # Pause/Resume option
        if self._is_watching:
            pause_action = menu.addAction("Pause Watching")
            pause_action.triggered.connect(self.stop_watching)
        else:
            resume_action = menu.addAction("Resume Watching")
            resume_action.triggered.connect(lambda: self.start_watching(2.0))
        
        menu.addSeparator()
        
        # Positions
        menu.addAction("Move: Top-Left", lambda: self.move(20, 20))
        menu.addAction("Move: Top-Right", lambda: self.move(
            self._screen.width() - self.width() - 20, 20
        ))
        menu.addAction("Move: Bottom-Right", self._position_at_corner)
        
        menu.addSeparator()
        
        # Learning info
        learned_action = menu.addAction("💡 What have you learned?")
        learned_action.triggered.connect(self._show_learned_patterns)
        
        menu.addSeparator()
        
        # Quit
        quit_action = menu.addAction("Goodbye Megumi")
        quit_action.triggered.connect(self._shutdown)
        
        menu.exec(self.mapToGlobal(pos))
    
    def _shutdown(self):
        """Clean shutdown"""
        self.stop_watching()
        self._memories.close()
        self._eyes.close()
        self._senses.close()
        QApplication.quit()
    
    # Drag support
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
    
    def closeEvent(self, event):
        """Handle window close"""
        self._shutdown()
        event.accept()


# Backward compatibility
MegumiWidget = MegumiPresence
