# MEGUMI

```
███╗   ███╗███████╗ ██████╗ ██╗   ██╗███╗   ███╗██╗
████╗ ████║██╔════╝██╔════╝ ██║   ██║████╗ ████║██║
██╔████╔██║█████╗  ██║  ███╗██║   ██║██╔████╔██║██║
██║╚██╔╝██║██╔══╝  ██║   ██║██║   ██║██║╚██╔╝██║██║
██║ ╚═╝ ██║███████╗╚██████╔╝╚██████╔╝██║ ╚═╝ ██║██║
╚═╝     ╚═╝╚══════╝ ╚═════╝  ╚═════╝ ╚═╝     ╚═╝╚═╝
        ~ She's always watching over you ~
```

<p align="center">
  <img src="assets/screenshots/preview.gif" width="300" alt="Megumi Preview">
</p>

<p align="center">
  <strong>An AI desktop companion that grows with you</strong>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#roadmap">Roadmap</a>
</p>

---

## What is Megumi?

**Megumi** is a local-first, lifelong AI companion designed to grow alongside you. She:

- **Watches** everything you do with her gentle eyes
- **Learns** your behavioral patterns with her growing heart
- **Remembers** everything in her local memories
- **Echoes** your activities when you're away
- **Lives** on your desktop as an adorable VRM avatar

She's not just a cute anime girl floating on your screen—she's learning *you*.

Everything she observes stays local. Your patterns, your workflows, your habits—all saved to her memories so she can grow and eventually act on your behalf.

---

## Features

### Currently Implemented

| Feature | Status | Description |
|---------|--------|-------------|
| **VRM Avatar** | Done | High-quality 3D anime character |
| **Cursor Tracking** | Done | Eyes and head follow your cursor |
| **Idle Animations** | Done | Breathing, blinking, subtle movements |
| **Always-on-Top** | Done | Floats over all windows |
| **Transparent Background** | Done | Only the character is visible |
| **Draggable** | Done | Move her anywhere on screen |
| **Quick Positions** | Done | Right-click to snap to corners |
| **Local Memories** | Done | Stores all observations locally |

### Coming Soon

| Feature | Phase | Description |
|---------|-------|-------------|
| **Screen Capture** | Phase 2 | Real-time screen monitoring |
| **OCR Recognition** | Phase 2 | Read text from screen |
| **UI Detection** | Phase 3 | Identify buttons, inputs, windows |
| **Pattern Learning** | Phase 4 | Understand your workflows |
| **Activity Echoing** | Phase 5 | Replay your actions autonomously |

---

## Installation

### Prerequisites

- **Python 3.10+**
- **Windows 10/11**
- **GPU** (recommended for smooth rendering)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/millw14/Megumi.git
cd megumi

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Summon Megumi
python summon.py
```

---

## Usage

### Basic Controls

| Action | How |
|--------|-----|
| **Move** | Click and drag |
| **Menu** | Right-click |
| **Quit** | Right-click > Goodbye Megumi |

### Right-Click Menu Options

- **Start/Stop Watching** — Toggle observation mode
- **Move: Top-Left** — Snap to top-left corner
- **Move: Top-Right** — Snap to top-right corner  
- **Move: Bottom-Right** — Snap to bottom-right corner
- **Goodbye Megumi** — Close Megumi

---

## Roadmap

### Phase 1: Kawaii Desktop Body [COMPLETE]
> *Give her a body to exist*

- [x] Floating transparent window
- [x] VRM model rendering with Three.js
- [x] Global cursor tracking
- [x] Idle animations (breathing, blinking)
- [x] Draggable with context menu

### Phase 2: Eyes of Waifu [IN PROGRESS]
> *Let her see the world*

- [x] Real-time screen capture
- [x] Region-based monitoring
- [ ] OCR text recognition
- [ ] Visual change detection

### Phase 3: Understanding Senpai
> *Make her understand what she sees*

- [ ] UI element detection (buttons, text fields)
- [ ] Window tracking
- [ ] Application recognition
- [ ] Context awareness

### Phase 4: Pattern Learning
> *Let her learn your ways*

- [ ] Activity sequence recording
- [ ] Pattern extraction
- [ ] Workflow modeling
- [ ] Behavior prediction

### Phase 5: Mimicry Mode
> *Watch her become you*

- [ ] Autonomous action execution
- [ ] Schedule-based automation
- [ ] Smart decision making
- [ ] Safety controls & rollback

---

## Project Structure

```
megumi/
├── summon.py                 # ✨ Entry point (summon her!)
├── README.md                 # You are here
├── requirements.txt          # Python dependencies
│
├── assets/
│   ├── models/
│   │   ├── megumi_chan.vrm   # Her VRM body
│   │   └── extras/           # Other character models
│   └── screenshots/          # For documentation
│
├── data/
│   ├── megumi_memories.db    # Her memories (auto-created)
│   └── patterns/             # Learned pattern files
│
├── megumi/                   # Her essence
│   ├── core/
│   │   ├── eyes.py           # 👀 She watches over you
│   │   ├── heart.py          # 💜 She learns and remembers
│   │   ├── memories.py       # 🧠 Where her memories live
│   │   ├── reading.py        # 📖 She reads what she sees
│   │   └── echo.py           # 🔊 She echoes your actions
│   ├── ui/
│   │   ├── presence.py       # Her presence on your desktop
│   │   └── soul.html         # Her visual soul (VRM renderer)
│   └── utils/
│       └── helpers.py        # Utility functions
│
├── config/
│   └── personality.py        # Her personality settings
│
└── docs/
    └── ROADMAP.md            # Detailed roadmap
```

---

## Safety Features

Megumi is designed with safety in mind:

- **Read-Only Mode** — Can observe without acting
- **Action Whitelist** — Only approved actions allowed
- **Kill Switch** — Instant termination hotkey
- **Action Logging** — Everything is recorded
- **Sensitive Area Blocking** — Won't touch banking/passwords

---

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](docs/CONTRIBUTING.md) first.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Credits

- VRM Model: Community contribution
- Three.js & @pixiv/three-vrm for 3D rendering
- PySide6 for the desktop framework

---

<p align="center">
  <strong>She's always watching over you. She's always learning. She is Megumi.</strong>
</p>

<p align="center">
  Made with 💜 by the Megumi Project
</p>
