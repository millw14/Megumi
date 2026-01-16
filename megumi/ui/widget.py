"""
Megumi Desktop Widget
~~~~~~~~~~~~~~~~~~~~~

The floating, transparent, always-on-top window
that displays Megumi on your desktop.
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
        
        # Positions
        menu.addAction("Move: Top-Left", lambda: self.move(20, 20))
        menu.addAction("Move: Top-Right", lambda: self.move(
            self._screen.width() - self.width() - 20, 20
        ))
        menu.addAction("Move: Bottom-Right", self._position_at_corner)
        
        menu.addSeparator()
        
        # Quit
        quit_action = menu.addAction("Quit Megumi")
        quit_action.triggered.connect(QApplication.quit)
        
        menu.exec(self.mapToGlobal(pos))
    
    # Drag support
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
