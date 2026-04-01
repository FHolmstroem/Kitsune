# AI Context — Kitsune 🦊

> **This file exists to onboard AI assistants in new chat sessions.**
> Delete this file before making the repo public.

## What is this project?

Kitsune is a desktop pet app — a white fox that roams the user's screen.
It hides behind OS windows, peeks out, walks around, sleeps, and can be
clicked to shoo it away or dragged to move it. Think Shimeji but modern,
minimal, and fox-themed.

## Core principles

- **Use libraries, don't reinvent.** If a library does it, use it.
- **Clean structure.** No monolithic files. Each module has one job.
- **Minimum viable first.** Get something on screen, then iterate.

## Tech stack

- **Python 3.10+**
- **PyQt6** — transparent frameless always-on-top window, sprite rendering, timers, mouse events
- **PyGetWindow** — detect open OS windows (position, size) so the fox can interact with them
- **Sprite sheets** in `assets/sprites/` — pixel art or drawn frames for each animation state

## Architecture

```
src/
├── main.py           Entry point. Creates QApplication, Overlay, Pet, starts event loop.
├── overlay.py        The transparent Qt window the fox lives on.
│                     Key flags: FramelessWindowHint, WindowStaysOnTopHint, Tool,
│                     WA_TranslucentBackground. Paints the current sprite frame.
├── pet.py            Fox state machine. States: IDLE, WALKING, SLEEPING, HIDING,
│                     PEEKING, FLEEING. Each state has a duration and weighted
│                     transitions to next states. Pure behavior logic, no Qt code.
├── animation.py      Loads sprite sheets, splits into frames, cycles through them.
│                     Each animation is a named sequence (walk_left, idle, sleep, etc).
├── window_manager.py Wraps pygetwindow. Returns list of WindowRect dataclasses
│                     (title, x, y, width, height). Polled periodically by the pet.
├── interactions.py   Maps mouse events from Overlay to Pet state changes.
│                     Left click = shoo, drag = pick up, right click = context menu.
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
- [ ] overlay.py implemented
- [ ] animation.py implemented
- [ ] pet.py implemented
- [ ] window_manager.py implemented
- [ ] interactions.py implemented
- [ ] Placeholder sprites created
- [ ] Fox walks across screen
- [ ] Fox hides behind windows
- [ ] Click to shoo works
- [ ] Drag to move works

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
{ echo "=== AI_CONTEXT.md ==="; cat AI_CONTEXT.md; for f in src/*.py; do echo ""; echo "=== $f ==="; cat "$f"; done; } | xclip -selection clipboard

# macOS variant
{ echo "=== AI_CONTEXT.md ==="; cat AI_CONTEXT.md; for f in src/*.py; do echo ""; echo "=== $f ==="; cat "$f"; done; } | pbcopy

# Windows (Git Bash / WSL)
{ echo "=== AI_CONTEXT.md ==="; cat AI_CONTEXT.md; for f in src/*.py; do echo ""; echo "=== $f ==="; cat "$f"; done; } | clip.exe

# Windows (PowerShell)
(Get-Content AI_CONTEXT.md; Get-ChildItem src/*.py | ForEach-Object { "`n=== $($_.Name) ==="; Get-Content $_ }) | Set-Clipboard
```

Then just paste into a new chat. The AI will have full context immediately.
