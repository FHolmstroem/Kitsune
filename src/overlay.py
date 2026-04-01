"""
Transparent always-on-top Qt window.

This is the "canvas" the fox lives on. It's a frameless, transparent
QWidget that covers the screen (or relevant portion of it) and stays
on top of other windows. The fox sprite is painted onto this widget.

Key Qt flags used:
    - Qt.FramelessWindowHint
    - Qt.WindowStaysOnTopHint
    - Qt.Tool                    (hides from taskbar)
    - Qt.WA_TranslucentBackground
    - Qt.WA_TransparentForMouseEvents (on the window itself,
      but NOT on the fox sprite area — we need clicks there)
"""
