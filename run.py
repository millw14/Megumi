#!/usr/bin/env python
r"""
Run Megumi - Your AI Desktop Companion

 __  __ _____ ____ _   _ __  __ ___ 
|  \/  | ____/ ___| | | |  \/  |_ _|
| |\/| |  _|| |  _| | | | |\/| || | 
| |  | | |__| |_| | |_| | |  | || | 
|_|  |_|_____\____|\___/|_|  |_|___|

~ She's always watching ~
"""

import sys
import os

# Add megumi package to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from megumi.ui.widget import MegumiWidget
from PySide6.QtWidgets import QApplication


def main():
    """Launch Megumi"""
    print()
    print("  Starting Megumi...")
    print("  -----------------------------")
    print("  Controls:")
    print("    - Drag to move")
    print("    - Right-click for menu")
    print("    - She follows your cursor")
    print("  -----------------------------")
    print()
    
    app = QApplication(sys.argv)
    app.setApplicationName("Megumi")
    app.setQuitOnLastWindowClosed(True)
    
    # Create and show Megumi
    megumi = MegumiWidget()
    megumi.show()
    
    print("  Megumi is now watching...")
    print()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
