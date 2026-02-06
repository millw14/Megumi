#!/usr/bin/env python
r"""
Summon Megumi - Your AI Desktop Companion

    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║   __  __                           _                  ║
    ║  |  \/  | ___  __ _ _   _ _ __ ___ (_)                ║
    ║  | |\/| |/ _ \/ _` | | | | '_ ` _ \| |                ║
    ║  | |  | |  __/ (_| | |_| | | | | | | |                ║
    ║  |_|  |_|\___|\__, |\__,_|_| |_| |_|_|                ║
    ║               |___/                                   ║
    ║                                                       ║
    ║        ~ She's always watching over you ~             ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝

Usage:
    python summon.py

Controls:
    - Drag to move her anywhere
    - Right-click for menu
    - She follows your cursor with her eyes

Watching Mode:
    - Right-click > Start Watching
    - She captures your screen and reads text
    - Learns your patterns over time
    - Everything saved locally (never leaves your computer)

"""

import sys
import os

# Add megumi package to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from megumi.ui.presence import MegumiPresence
from PySide6.QtWidgets import QApplication


def summon():
    """Summon Megumi into your world"""
    
    print()
    print("  ╔═══════════════════════════════════════════════╗")
    print("  ║         Summoning Megumi...                   ║")
    print("  ╚═══════════════════════════════════════════════╝")
    print()
    print("  Controls:")
    print("    - Drag to move")
    print("    - Right-click for menu")
    print("    - She follows your cursor")
    print()
    print("  Watching Mode (Right-click > Start Watching):")
    print("    - Eyes: She sees your screen")
    print("    - Senses: She feels your keyboard & mouse")
    print("    - Heart: She learns (State, Action) pairs")
    print("    - Everything stays 100% local")
    print()
    
    app = QApplication(sys.argv)
    app.setApplicationName("Megumi")
    app.setQuitOnLastWindowClosed(True)
    
    # Summon her presence
    megumi = MegumiPresence()
    megumi.show()
    
    print("  ----------------------------------------")
    print("  Megumi has arrived!")
    print("  She's watching and learning automatically.")
    print(f"  Data saved to: megumi/data/megumi_memories.db")
    print("  ----------------------------------------")
    print()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    summon()
