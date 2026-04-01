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

from PyQt6.QtCore import Qt, QPoint, QRect, QTimer
from PyQt6.QtGui import QPainter, QPixmap
from PyQt6.QtWidgets import QWidget, QApplication


class Overlay(QWidget):
    """Full-screen transparent window the fox is painted on.

    The overlay covers the entire primary screen. It's invisible
    except where we explicitly paint a sprite. Mouse events pass
    through to whatever is underneath *unless* they land on the
    fox sprite area (controlled by the hit-test region).
    """

    # How often we repaint (milliseconds). 60 FPS ≈ 16 ms.
    TICK_MS = 16

    def __init__(self) -> None:
        super().__init__()
        self._setup_window_flags()
        self._resize_to_screen()

        # Where the fox sprite is drawn (top-left corner in screen coords).
        self._sprite_pos = QPoint(200, 200)

        # The current frame to paint. None = nothing visible yet.
        self._current_frame: QPixmap | None = None

        # Refresh timer — drives repaints so the fox animates.
        self._tick_timer = QTimer(self)
        self._tick_timer.timeout.connect(self.update)
        self._tick_timer.start(self.TICK_MS)

        # Raise timer — some Linux WMs (especially KDE/Plasma) don't
        # reliably honour WindowStaysOnTopHint for transparent tool
        # windows. Periodically calling raise_() nudges us back on top.
        # 500 ms is frequent enough to feel instant but cheap enough
        # to not waste CPU.
        self._raise_timer = QTimer(self)
        self._raise_timer.timeout.connect(self.raise_)
        self._raise_timer.start(500)

    # ------------------------------------------------------------------
    # Setup helpers
    # ------------------------------------------------------------------

    def _setup_window_flags(self) -> None:
        """Configure the window to be frameless, transparent, and on top."""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool  # hides from taskbar / alt-tab
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Let mouse events fall through to windows underneath.
        # We'll selectively consume events in the fox sprite area
        # once interactions.py is wired up.
        self.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents, True
        )

    def _resize_to_screen(self) -> None:
        """Stretch the overlay to cover the entire primary screen."""
        screen = QApplication.primaryScreen()
        if screen is not None:
            geo = screen.geometry()
            self.setGeometry(geo)

    # ------------------------------------------------------------------
    # Public interface (called by Pet / AnimationController later)
    # ------------------------------------------------------------------

    def set_sprite(self, pixmap: QPixmap) -> None:
        """Set the current sprite frame to paint."""
        self._current_frame = pixmap

    def set_position(self, x: int, y: int) -> None:
        """Move the fox to (x, y) in screen coordinates."""
        self._sprite_pos = QPoint(x, y)

    @property
    def sprite_rect(self) -> QRect:
        """Bounding box of the current sprite in screen coords.

        Useful for hit-testing clicks — is the mouse inside the fox?
        """
        if self._current_frame is None:
            return QRect(self._sprite_pos.x(), self._sprite_pos.y(), 0, 0)
        return QRect(self._sprite_pos, self._current_frame.size())

    # ------------------------------------------------------------------
    # Qt overrides
    # ------------------------------------------------------------------

    def paintEvent(self, event) -> None:  # noqa: N802 (Qt naming)
        """Draw the current sprite frame at the fox's position."""
        if self._current_frame is None:
            return
        painter = QPainter(self)
        painter.drawPixmap(self._sprite_pos, self._current_frame)
        painter.end()