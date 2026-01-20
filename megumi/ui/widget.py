"""
Megumi Desktop Widget
~~~~~~~~~~~~~~~~~~~~~

The floating, transparent, always-on-top window
that displays Megumi on your desktop.

Now with Phase 2: She watches and learns.
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

# Phase 2 imports
from ..core.database import get_database
from ..core.watcher import get_watcher
from ..core.learner import get_learner


class SilentHTTPHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler that serves files without logging"""
    
    def log_message(self, format, *args):
        pass  # Silence is golden
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()


class MegumiWidget(QWidget):
    """
    The main Megumi desktop companion widget.
    
    Features:
    - Frameless transparent window
    - Always stays on top
    - Draggable anywhere
    - VRM character with cursor tracking
    - Right-click context menu
    - Screen watching and learning (Phase 2)
    """
    
    def __init__(
        self,
        width: int = 300,
        height: int = 420,
        port: int = 9998
    ):
        super().__init__()
        
        self._drag_pos = QPoint()
        self._server_port = port
        self._server_thread: Optional[threading.Thread] = None
        
        # Get paths
        self._megumi_root = Path(__file__).parent.parent.parent.resolve()
        self._assets_path = self._megumi_root / "assets"
        self._vrm_path = self._assets_path / "models" / "megumi.vrm"
        
        # Phase 2: Initialize watching and learning
        self._is_watching = False
        self._db = get_database()
        self._watcher = get_watcher()
        self._learner = get_learner()
        
        # Connect watcher to learner
        self._learner.watcher = self._watcher
        
        # Set up watcher callback
        self._watcher.add_callback(self._on_screen_capture)
        
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
        QTimer.singleShot(500, self._load_viewer)
        
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
        
        print("[Megumi] Widget initialized")
        print(f"[Megumi] Database: {self._db.db_path}")
    
    def _start_server(self):
        """Start local HTTP server for assets"""
        def run():
            os.chdir(self._megumi_root)
            with socketserver.TCPServer(("", self._server_port), SilentHTTPHandler) as httpd:
                httpd.serve_forever()
        
        self._server_thread = threading.Thread(target=run, daemon=True)
        self._server_thread.start()
    
    def _load_viewer(self):
        """Load the VRM viewer"""
        url = f"http://localhost:{self._server_port}/megumi/ui/viewer.html"
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
        norm_x = (pos.x() / self._screen.width()) * 2 - 1
        norm_y = -((pos.y() / self._screen.height()) * 2 - 1)
        
        # Send to JavaScript
        js = f"if(window.setGlobalMouse) window.setGlobalMouse({norm_x}, {norm_y});"
        self._web.page().runJavaScript(js)
    
    # ==================== PHASE 2: WATCHING ====================
    
    def _on_screen_capture(self, image, metadata):
        """Callback when screen is captured"""
        self._learner.observe(image, metadata)
    
    def start_watching(self, interval: float = 2.0):
        """Start watching the screen"""
        if self._is_watching:
            return
        
        self._is_watching = True
        self._learner.start_learning()
        self._watcher.start_watching(interval=interval)
        
        # Visual feedback - make Megumi blink faster or show alert
        js = "if(window.setWatchingMode) window.setWatchingMode(true);"
        self._web.page().runJavaScript(js)
        
        print("[Megumi] Started watching...")
    
    def stop_watching(self):
        """Stop watching the screen"""
        if not self._is_watching:
            return
        
        self._is_watching = False
        self._watcher.stop_watching()
        self._learner.stop_learning()
        
        # Visual feedback
        js = "if(window.setWatchingMode) window.setWatchingMode(false);"
        self._web.page().runJavaScript(js)
        
        print("[Megumi] Stopped watching")
    
    def toggle_watching(self):
        """Toggle watching mode"""
        if self._is_watching:
            self.stop_watching()
        else:
            self.start_watching()
    
    def get_stats(self):
        """Get learning statistics"""
        return self._db.get_stats()
    
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
        
        # Watching toggle
        watch_text = "Stop Watching" if self._is_watching else "Start Watching"
        watch_action = menu.addAction(watch_text)
        watch_action.triggered.connect(self.toggle_watching)
        
        # Stats
        stats = self.get_stats()
        stats_action = menu.addAction(
            f"Observations: {stats['total_observations']} | "
            f"Patterns: {stats['total_patterns']}"
        )
        stats_action.setEnabled(False)
        
        menu.addSeparator()
        
        # Positions
        menu.addAction("Move: Top-Left", lambda: self.move(20, 20))
        menu.addAction("Move: Top-Right", lambda: self.move(
            self._screen.width() - self.width() - 20, 20
        ))
        menu.addAction("Move: Bottom-Right", self._position_at_corner)
        
        menu.addSeparator()
        
        # Quit
        quit_action = menu.addAction("Quit Megumi")
        quit_action.triggered.connect(self._shutdown)
        
        menu.exec(self.mapToGlobal(pos))
    
    def _shutdown(self):
        """Clean shutdown"""
        self.stop_watching()
        self._db.close()
        self._watcher.close()
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
