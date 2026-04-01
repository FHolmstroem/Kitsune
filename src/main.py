"""
Entry point for Kitsune.

Initializes the Qt application, creates the overlay window,
spawns the fox, and starts the main event loop.
"""

import signal
import sys

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QColor, QPainter, QIcon, QAction, QShortcut, QKeySequence
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu

from overlay import Overlay


def _make_placeholder_sprite(size: int = 48) -> QPixmap:
    """Create a simple colored square so we have *something* visible.

    This gets replaced once animation.py loads real sprite sheets.
    """
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor(0, 0, 0, 0))  # transparent background
    painter = QPainter(pixmap)
    painter.setBrush(QColor(255, 255, 255))       # white fill (the fox!)
    painter.setPen(QColor(60, 60, 60))             # dark outline
    painter.drawEllipse(4, 4, size - 8, size - 8)  # simple circle
    painter.end()
    return pixmap


def _make_tray_icon() -> QIcon:
    """Tiny 16x16 icon for the system tray."""
    pixmap = QPixmap(16, 16)
    pixmap.fill(QColor(0, 0, 0, 0))
    painter = QPainter(pixmap)
    painter.setBrush(QColor(255, 255, 255))
    painter.setPen(QColor(80, 80, 80))
    painter.drawEllipse(1, 1, 14, 14)
    painter.end()
    return QIcon(pixmap)


def _setup_signal_handling(app: QApplication) -> None:
    """Let Ctrl+C in the terminal kill the app.

    PyQt installs its own signal handler that swallows SIGINT.
    The fix: restore Python's default handler, and use a short
    QTimer to give Python a chance to process it between Qt events.
    """
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Python signal handlers only run between bytecode instructions.
    # Qt's event loop blocks in C, so Python never gets control.
    # This dummy timer wakes Python up every 200 ms so it can
    # notice the signal and exit.
    timer = QTimer(app)
    timer.timeout.connect(lambda: None)
    timer.start(200)


def _setup_tray(app: QApplication) -> QSystemTrayIcon:
    """Create a system tray icon with a Quit option.

    This is the main way to close the app since the overlay
    has no title bar and hides from the taskbar.
    """
    tray = QSystemTrayIcon(_make_tray_icon(), app)

    menu = QMenu()
    quit_action = QAction("Quit Kitsune", menu)
    quit_action.triggered.connect(app.quit)
    menu.addAction(quit_action)

    tray.setContextMenu(menu)
    tray.setToolTip("Kitsune 🦊")
    tray.show()
    return tray


def main() -> None:
    """Launch Kitsune."""
    app = QApplication(sys.argv)

    _setup_signal_handling(app)
    tray = _setup_tray(app)  # noqa: F841 — prevent garbage collection

    overlay = Overlay()
    overlay.set_sprite(_make_placeholder_sprite())
    overlay.set_position(400, 300)
    overlay.show()

    # Ctrl+Q to quit — works even when tray icon fails (e.g. KDE).
    # ApplicationShortcut context means it fires regardless of which
    # widget has focus.
    shortcut = QShortcut(QKeySequence("Ctrl+Q"), overlay)
    shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
    shortcut.activated.connect(app.quit)

    print("🦊 Kitsune is running! Quit with Ctrl+Q or Ctrl+C in this terminal.")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()