# AI Context — Kitsune 🦊

> **This file exists to onboard AI assistants in new chat sessions.**
> Delete this file before making the repo public.

## What is this project?

Kitsune is a desktop pet app — a white fox that roams the user's screen.
It hides behind OS windows, peeks out, walks around, sleeps, and can be
clicked to shoo it away or dragged to move it. Think Shimeji but modern,
minimal, and fox-themed.

## Core principles #

- **Use libraries, don't reinvent.** If a library does it, use it.
- **Clean structure.** No monolithic files. Each module has one job.
- **Minimum viable first.** Get something on screen, then iterate.

## Tech stack

- **Python 3.11** (developed on Debian/KDE Plasma)
- **PyQt6** — transparent frameless always-on-top window, sprite rendering, timers, mouse events
- **PyGetWindow** — detect open OS windows (position, size) so the fox can interact with them
- **Sprite sheets** in `assets/sprites/` — pixel art or drawn frames for each animation state
- **pytest** — test suite (run headless with `QT_QPA_PLATFORM=offscreen`)

## How to run

```bash
# Activate the venv first — always!
source venv/bin/activate

# Run the app
python src/main.py
# Quit with Ctrl+Q (anywhere) or Ctrl+C (in the terminal)

# Run tests (headless, no display needed)
QT_QPA_PLATFORM=offscreen PYTHONPATH=src pytest tests/ -v
```

## Architecture

```
src/
├── main.py           Entry point. Creates QApplication, Overlay, Pet, starts event loop.
│                     Also sets up: system tray icon (Quit menu), Ctrl+Q shortcut,
│                     Ctrl+C signal handling, and a placeholder sprite.
├── overlay.py        The transparent Qt window the fox lives on.
│                     Key flags: FramelessWindowHint, WindowStaysOnTopHint,
│                     BypassWindowManagerHint, Tool, WA_TranslucentBackground.
│                     Paints the current sprite frame. Has a tick timer (~60 FPS)
│                     for repaints and a raise timer (500 ms) to stay on top on KDE.
├── pet.py            Fox state machine. States: IDLE, WALKING, SLEEPING, HIDING,
│                     PEEKING, FLEEING. Each state has a duration and weighted
│                     transitions to next states. Pure behavior logic, no Qt code.
├── animation.py      Loads sprite sheets, splits into frames, cycles through them.
│                     Each animation is a named sequence (walk_left, idle, sleep, etc).
├── window_manager.py Wraps pygetwindow. Returns list of WindowRect dataclasses
│                     (title, x, y, width, height). Polled periodically by the pet.
├── interactions.py   Maps mouse events from Overlay to Pet state changes.
│                     Left click = shoo, drag = pick up, right click = context menu.

tests/
├── test_overlay.py   22 tests covering: window flags, geometry, sprite positioning,
│                     tick timer, raise timer, tray icon, signal handling.
├── test_animation.py Tests for FPS math, AnimationController state machine, and sprite slicing.
├── test_pet.py       Tests for logic state machine, timers, and screen boundary collisions.
```

## Implementation order

1. overlay.py — transparent window on screen
2. animation.py — load and display a sprite
3. pet.py — basic state machine (idle ↔ walking)
4. window_manager.py — detect window positions
5. interactions.py — click/drag handling

## Current status

<!-- UPDATE THIS as you make progress -->
- [x] Project scaffolded with empty modules + docstrings
- [x] overlay.py implemented — frameless transparent always-on-top window
- [x] main.py wired up — launches overlay with placeholder sprite (white circle)
- [x] Shutdown works — Ctrl+Q shortcut, Ctrl+C in terminal, tray icon quit menu
- [x] Overlay stays on top — BypassWindowManagerHint + periodic raise_() for KDE
- [x] Test suite — passing tests for overlay.py and animation.py
- [x] animation.py implemented (with temporary blob generator)
- [x] pet.py implemented — pure logic state machine with boundary collision
- [x] Fox walks across screen (bounces off monitor edges)
- [ ] interactions.py implemented
- [ ] Real sprites created
- [ ] Fox walks across screen
- [ ] Fox hides behind windows
- [ ] Click to shoo works
- [ ] Drag to move works

## Known quirks

- **KDE tray warning:** `failed to register "org.kde.StatusNotifierItem"` is harmless.
  The tray icon may or may not show depending on KDE version. Ctrl+Q is the reliable
  quit method.
- **BypassWindowManagerHint:** Needed on KDE/Plasma because WindowStaysOnTopHint alone
  doesn't keep the overlay on top. Trade-off: the WM doesn't manage the window at all,
  so we handle everything ourselves (positioning, staying on-screen, etc).

## Style and preferences

- I'm a CS student. Explain things but don't over-explain basics.
- I prefer working module by module, not getting a huge code dump.
- Keep code Pythonic. Type hints yes, over-engineering no.
- I want to understand what I'm shipping, not just copy-paste.

## Repo

- **GitHub:** git@github.com:FHolmstroem/Kitsune.git
- **License:** MIT
- **Visibility:** Private (will go public later)

## How to feed code to AI

From the project root, run:

```bash
# Collect all Python files + this context into clipboard (Linux/xclip)
{ echo "=== AI_CONTEXT.md ==="; cat AI_CONTEXT.md; for f in src/*.py; do echo ""; echo "=== $f ==="; cat "$f"; done; for f in tests/*.py; do echo ""; echo "=== $f ==="; cat "$f"; done; } | xclip -selection clipboard

# macOS variant
{ echo "=== AI_CONTEXT.md ==="; cat AI_CONTEXT.md; for f in src/*.py; do echo ""; echo "=== $f ==="; cat "$f"; done; for f in tests/*.py; do echo ""; echo "=== $f ==="; cat "$f"; done; } | pbcopy

# Windows (Git Bash / WSL)
{ echo "=== AI_CONTEXT.md ==="; cat AI_CONTEXT.md; for f in src/*.py; do echo ""; echo "=== $f ==="; cat "$f"; done; for f in tests/*.py; do echo ""; echo "=== $f ==="; cat "$f"; done; } | clip.exe

# Windows (PowerShell)
(Get-Content AI_CONTEXT.md; Get-ChildItem src/*.py | ForEach-Object { "`n=== $($_.Name) ==="; Get-Content $_ }; Get-ChildItem tests/*.py | ForEach-Object { "`n=== $($_.Name) ==="; Get-Content $_ }) | Set-Clipboard
```

Then just paste into a new chat. The AI will have full context immediately.