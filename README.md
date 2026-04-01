# 🦊 Kitsune

A lightweight desktop pet — a white fox that roams your screen, hides behind windows, and reacts when you interact with it.

Built with Python and PyQt6.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- 🦊 Animated white fox that walks across your screen
- 🪟 Aware of open windows — hides behind them, peeks out
- 🖱️ Click to shoo, drag to move
- 🎨 Sprite-based animations (walk, idle, sleep, hide, peek)
- 💻 Cross-platform (Windows, macOS, Linux)

## Installation

```bash
git clone git@github.com:FHolmstroem/Kitsune.git
cd Kitsune
pip install -r requirements.txt
```

## Usage

```bash
python -m src.main

.\venv\Scripts\Activate.ps1
$env:QT_QPA_PLATFORM="offscreen"; $env:PYTHONPATH="src"; pytest tests/ -v; Remove-Item env:QT_QPA_PLATFORM

```

## Project Structure

```
kitsune/
├── assets/sprites/       Fox sprite sheets
├── src/
│   ├── main.py           Entry point
│   ├── pet.py            Fox behavior and state machine
│   ├── animation.py      Sprite loading and frame cycling
│   ├── overlay.py        Transparent always-on-top window
│   ├── window_manager.py OS window detection
│   └── interactions.py   Click, drag, and shoo handling
└── tests/
```

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## Support

If you enjoy Kitsune, consider buying me a coffee ☕

## License

[MIT](LICENSE)
