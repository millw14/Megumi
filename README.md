# MEGUMI

```
███╗   ███╗███████╗ ██████╗ ██╗   ██╗███╗   ███╗██╗
████╗ ████║██╔════╝██╔════╝ ██║   ██║████╗ ████║██║
██╔████╔██║█████╗  ██║  ███╗██║   ██║██╔████╔██║██║
██║╚██╔╝██║██╔══╝  ██║   ██║██║   ██║██║╚██╔╝██║██║
██║ ╚═╝ ██║███████╗╚██████╔╝╚██████╔╝██║ ╚═╝ ██║██║
╚═╝     ╚═╝╚══════╝ ╚═════╝  ╚═════╝ ╚═╝     ╚═╝╚═╝
        ~ She's always watching ~
```

<p align="center">
  <img src="assets/screenshots/preview.gif" width="300" alt="Megumi Preview">
</p>

<p align="center">
  <strong>An AI desktop companion that learns your patterns</strong>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#roadmap">Roadmap</a>
</p>

---

## What is Megumi?

**Megumi** is an AI-powered desktop companion that:

- **Watches** everything you do on your computer
- **Learns** your behavioral patterns and workflows
- **Remembers** everything in a local database
- **Mimics** your activities even when you're offline
- **Lives** on your desktop as an adorable VRM avatar

She's not just a cute anime girl floating on your screen—she's learning *you*.

Everything she observes gets stored locally. Your patterns, your workflows, your habits—all saved to a database so she can learn and eventually act on your behalf.

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
| **Local Database** | Done | Stores all observations locally |

### Coming Soon

| Feature | Phase | Description |
|---------|-------|-------------|
| **Screen Capture** | Phase 2 | Real-time screen monitoring |
| **OCR Recognition** | Phase 2 | Read text from screen |
| **UI Detection** | Phase 3 | Identify buttons, inputs, windows |
| **Pattern Learning** | Phase 4 | Understand your workflows |
| **Activity Mimicking** | Phase 5 | Replay your actions autonomously |

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

# Run Megumi
python run.py
```

---

## Usage

### Basic Controls

| Action | How |
|--------|-----|
| **Move** | Click and drag |
| **Menu** | Right-click |
| **Quit** | Right-click > Quit |

### Right-Click Menu Options

- **Move: Top-Left** — Snap to top-left corner
- **Move: Top-Right** — Snap to top-right corner  
- **Move: Bottom-Right** — Snap to bottom-right corner
- **Quit** — Close Megumi

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

- [ ] Real-time screen capture
- [ ] Region-based monitoring
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
├── README.md                 # You are here
├── requirements.txt          # Python dependencies
├── run.py                    # Entry point
│
├── assets/
│   ├── models/
│   │   └── megumi.vrm       # The VRM avatar
│   └── screenshots/          # For documentation
│
├── data/
│   ├── megumi.db            # SQLite database (auto-created)
│   └── patterns/            # Learned pattern files
│
├── megumi/                   # Main package
│   ├── core/
│   │   ├── watcher.py       # Screen monitoring
│   │   ├── learner.py       # Pattern recognition
│   │   ├── mimic.py         # Activity mimicking
│   │   └── database.py      # Database operations
│   ├── ui/
│   │   ├── widget.py        # Desktop widget
│   │   └── viewer.html      # VRM renderer
│   └── utils/
│       └── helpers.py       # Utility functions
│
├── config/
│   └── settings.py          # Configuration
│
└── docs/
    └── ROADMAP.md           # Detailed roadmap
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
  <strong>She's always watching. She's always learning. She is Megumi.</strong>
</p>

<p align="center">
  Made by the Megumi Project
</p>
