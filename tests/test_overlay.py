"""Tests for overlay.py and main.py placeholder sprite."""

import sys
import pytest

from PyQt6.QtCore import Qt, QPoint, QRect
from PyQt6.QtGui import QPixmap, QColor
from PyQt6.QtWidgets import QApplication

# Need a QApplication before creating any widgets.
# This fixture keeps one alive for the whole test session.

@pytest.fixture(scope="session")
def qapp():
    """Provide a single QApplication for all tests."""
    app = QApplication.instance() or QApplication(sys.argv)
    yield app


# ---- Overlay tests --------------------------------------------------------

@pytest.fixture
def overlay(qapp):
    """Create a fresh Overlay instance."""
    from overlay import Overlay
    ov = Overlay()
    yield ov
    ov._tick_timer.stop()
    ov._raise_timer.stop()


class TestOverlayWindowFlags:
    """The overlay must be frameless, on-top, transparent, and a Tool window."""

    def test_frameless(self, overlay):
        flags = overlay.windowFlags()
        assert flags & Qt.WindowType.FramelessWindowHint

    def test_stays_on_top(self, overlay):
        flags = overlay.windowFlags()
        assert flags & Qt.WindowType.WindowStaysOnTopHint

    def test_tool_flag(self, overlay):
        """Tool flag keeps it out of taskbar / alt-tab."""
        flags = overlay.windowFlags()
        assert flags & Qt.WindowType.Tool

    def test_translucent_background(self, overlay):
        assert overlay.testAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )

    def test_transparent_for_mouse(self, overlay):
        assert overlay.testAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents
        )
    
    def test_bypass_window_manager(self, overlay):
        flags = overlay.windowFlags()
        assert flags & Qt.WindowType.BypassWindowManagerHint


class TestOverlayGeometry:
    """The overlay should cover the primary screen."""

    def test_covers_screen(self, overlay, qapp):
        screen = qapp.primaryScreen()
        if screen is None:
            pytest.skip("No screen available (headless CI)")
        expected = screen.geometry()
        assert overlay.geometry().width() == expected.width()
        assert overlay.geometry().height() == expected.height()


class TestOverlaySprite:
    """Sprite positioning and bounding-rect logic."""

    def test_set_position(self, overlay):
        overlay.set_position(100, 250)
        assert overlay._sprite_pos == QPoint(100, 250)

    def test_sprite_rect_no_frame(self, overlay):
        """With no sprite loaded, the rect should be zero-sized."""
        overlay._current_frame = None
        rect = overlay.sprite_rect
        assert rect.width() == 0 and rect.height() == 0

    def test_sprite_rect_with_frame(self, overlay):
        px = QPixmap(32, 48)
        overlay.set_sprite(px)
        overlay.set_position(10, 20)
        rect = overlay.sprite_rect
        assert rect == QRect(QPoint(10, 20), px.size())

    def test_set_sprite_stores_pixmap(self, overlay):
        px = QPixmap(16, 16)
        overlay.set_sprite(px)
        assert overlay._current_frame is px


class TestOverlayTimer:
    """The refresh timer should be running at ~60 FPS."""

    def test_timer_active(self, overlay):
        assert overlay._tick_timer.isActive()

    def test_timer_interval(self, overlay):
        assert overlay._tick_timer.interval() == overlay.TICK_MS


class TestOverlayRaiseTimer:
    """The raise timer should keep the overlay on top of other windows."""

    def test_raise_timer_active(self, overlay):
        assert overlay._raise_timer.isActive()

    def test_raise_timer_interval(self, overlay):
        assert overlay._raise_timer.interval() == 500


# ---- Placeholder sprite tests --------------------------------------------

class TestPlaceholderSprite:
    """The placeholder created in main.py should be a valid pixmap."""

    def test_returns_pixmap(self, qapp):
        from main import _make_placeholder_sprite
        px = _make_placeholder_sprite()
        assert isinstance(px, QPixmap)
        assert not px.isNull()

    def test_default_size(self, qapp):
        from main import _make_placeholder_sprite
        px = _make_placeholder_sprite()
        assert px.width() == 48 and px.height() == 48

    def test_custom_size(self, qapp):
        from main import _make_placeholder_sprite
        px = _make_placeholder_sprite(size=64)
        assert px.width() == 64 and px.height() == 64

    def test_has_transparency(self, qapp):
        """The pixmap should have an alpha channel (transparent bg)."""
        from main import _make_placeholder_sprite
        px = _make_placeholder_sprite()
        assert px.hasAlphaChannel()


# ---- Tray icon tests ------------------------------------------------------

class TestTrayIcon:
    """The system tray should provide a way to quit the app."""

    def test_tray_is_visible(self, qapp):
        from main import _setup_tray
        tray = _setup_tray(qapp)
        assert tray.isVisible()
        tray.hide()  # cleanup

    def test_tray_has_context_menu(self, qapp):
        from main import _setup_tray
        tray = _setup_tray(qapp)
        menu = tray.contextMenu()
        assert menu is not None
        tray.hide()

    def test_tray_menu_has_quit(self, qapp):
        from main import _setup_tray
        tray = _setup_tray(qapp)
        menu = tray.contextMenu()
        actions = menu.actions()
        action_texts = [a.text() for a in actions]
        assert "Quit Kitsune" in action_texts
        tray.hide()


# ---- Signal handling tests ------------------------------------------------

class TestSignalHandling:
    """Ctrl+C should work after _setup_signal_handling is called."""

    def test_sigint_restored(self, qapp):
        import signal
        from main import _setup_signal_handling
        _setup_signal_handling(qapp)
        assert signal.getsignal(signal.SIGINT) == signal.SIG_DFL