"""Tests for interactions.py."""

import sys
import pytest

from PyQt6.QtCore import Qt, QPoint, QEvent
from PyQt6.QtGui import QMouseEvent, QPixmap
from PyQt6.QtWidgets import QApplication

from pet import Pet, PetState
from overlay import Overlay
from interactions import InteractionHandler

@pytest.fixture(scope="session")
def qapp():
    """Provide a single QApplication for all tests."""
    app = QApplication.instance() or QApplication(sys.argv)
    yield app

@pytest.fixture
def interaction_setup(qapp):
    """Setup overlay, pet, and handler for a test."""
    overlay = Overlay()
    pet = Pet(start_x=100.0, start_y=100.0)
    
    # Give overlay a fake sprite so we have a valid bounding rect
    pixmap = QPixmap(50, 50)
    overlay.set_sprite(pixmap)
    overlay.set_position(100, 100)
    
    handler = InteractionHandler(overlay, pet)
    
    yield overlay, pet, handler
    
    overlay._tick_timer.stop()
    if overlay._raise_timer:
        overlay._raise_timer.stop()

def create_mouse_event(event_type: QEvent.Type, button: Qt.MouseButton, pos: QPoint) -> QMouseEvent:
    """Helper to mock Qt mouse events."""
    return QMouseEvent(
        event_type,
        pos.toPointF(),
        pos.toPointF(),  # global position
        button,
        button,
        Qt.KeyboardModifier.NoModifier
    )

def test_ignore_clicks_outside_fox(interaction_setup):
    overlay, pet, handler = interaction_setup
    
    # Fox is at (100, 100) to (150, 150). Click at (10, 10).
    event = create_mouse_event(QEvent.Type.MouseButtonPress, Qt.MouseButton.LeftButton, QPoint(10, 10))
    handled = handler._handle_mouse_press(event)
    
    assert not handled
    assert not handler.is_dragging

def test_left_click_starts_drag(interaction_setup):
    overlay, pet, handler = interaction_setup
    
    # Click exactly on the fox at (110, 110)
    event = create_mouse_event(QEvent.Type.MouseButtonPress, Qt.MouseButton.LeftButton, QPoint(110, 110))
    handled = handler._handle_mouse_press(event)
    
    assert handled
    assert handler.is_dragging
    assert handler.drag_offset == QPoint(10, 10)  # Clicked 10px into the sprite

def test_dragging_moves_pet(interaction_setup):
    overlay, pet, handler = interaction_setup
    
    # Press
    press_event = create_mouse_event(QEvent.Type.MouseButtonPress, Qt.MouseButton.LeftButton, QPoint(110, 110))
    handler._handle_mouse_press(press_event)
    
    # Move to (200, 200)
    move_event = create_mouse_event(QEvent.Type.MouseMove, Qt.MouseButton.NoButton, QPoint(200, 200))
    handled = handler._handle_mouse_move(move_event)
    
    assert handled
    assert handler.has_moved
    
    # New position should be Mouse(200) - Offset(10) = 190
    assert pet.x == 190.0
    assert pet.y == 190.0
    assert overlay._sprite_pos == QPoint(190, 190)

def test_click_without_move_shoos_fox(interaction_setup):
    overlay, pet, handler = interaction_setup
    pet.enter_state(PetState.IDLE)
    
    # Press
    press_event = create_mouse_event(QEvent.Type.MouseButtonPress, Qt.MouseButton.LeftButton, QPoint(110, 110))
    handler._handle_mouse_press(press_event)
    
    # Release without moving
    release_event = create_mouse_event(QEvent.Type.MouseButtonRelease, Qt.MouseButton.LeftButton, QPoint(110, 110))
    handler._handle_mouse_release(release_event)
    
    assert not handler.is_dragging
    # Should no longer be IDLE because it got shooed
    assert pet.state != PetState.IDLE