
"""Tests for animation.py."""

import sys
import pytest

from PyQt6.QtGui import QPixmap, QColor
from PyQt6.QtWidgets import QApplication

from animation import (
    Animation,
    AnimationController,
    load_sprite_sheet,
    create_placeholder_animations
)

# We need a QApplication fixture here too, because QPixmap operations
# will fail if the Qt event loop hasn't been initialized.
@pytest.fixture(scope="session")
def qapp():
    """Provide a single QApplication for all tests."""
    app = QApplication.instance() or QApplication(sys.argv)
    yield app


# ---- Data Class Tests -----------------------------------------------------

def test_animation_duration():
    """Test frame duration calculation based on FPS."""
    # 10 FPS = 100ms per frame
    anim = Animation(frames=[], fps=10)
    assert anim.frame_duration_ms == 100.0

    # 0 FPS should safely fall back to 0ms to avoid division by zero
    anim_zero = Animation(frames=[], fps=0)
    assert anim_zero.frame_duration_ms == 0.0


# ---- Controller Tests -----------------------------------------------------

class TestAnimationController:
    """Test the state machine and frame timing logic."""

    @pytest.fixture
    def dummy_frames(self, qapp):
        """Create 3 empty 10x10 pixmaps for testing."""
        return [QPixmap(10, 10) for _ in range(3)]

    @pytest.fixture
    def controller(self, dummy_frames):
        """Provide a controller with a 'walk' animation loaded."""
        ctrl = AnimationController()
        # 10 FPS = 100ms per frame
        anim = Animation(frames=dummy_frames, fps=10)
        ctrl.add_animation("walk", anim)
        return ctrl

    def test_initial_state(self, controller):
        """A new controller should have no active animation."""
        assert controller.current_anim_name is None
        assert controller.current_frame is None

    def test_play_valid_animation(self, controller, dummy_frames):
        """Playing a known animation should reset the state to frame 0."""
        controller.play("walk")
        assert controller.current_anim_name == "walk"
        assert controller.current_frame_idx == 0
        assert controller.current_frame is dummy_frames[0]

    def test_play_invalid_animation(self, controller):
        """Attempting to play an unknown animation should do nothing."""
        controller.play("fly")
        assert controller.current_anim_name is None

    def test_tick_advances_frames(self, controller, dummy_frames):
        """Ticking should only advance the frame if enough time has passed."""
        controller.play("walk")
        
        # Tick 50ms (duration is 100ms). Shouldn't change frame yet.
        frame = controller.tick(50.0)
        assert controller.current_frame_idx == 0
        assert frame is dummy_frames[0]

        # Tick another 60ms (Total accumulator: 110ms). Should advance to frame 1.
        frame = controller.tick(60.0)
        assert controller.current_frame_idx == 1
        assert frame is dummy_frames[1]

    def test_tick_loops_around(self, controller, dummy_frames):
        """Ticking past the end of the frames should loop back to the start."""
        controller.play("walk")
        
        # Tick 350ms (3.5 frames worth of time). 
        # Total frames = 3, so it should loop back to frame 0.
        frame = controller.tick(350.0)
        assert controller.current_frame_idx == 0
        assert frame is dummy_frames[0]


# ---- Integration Tests ----------------------------------------------------

def test_load_sprite_sheet(tmp_path, qapp):
    """Test slicing a large image into smaller QPixmap frames."""
    # Create a 64x32 mock sprite sheet (Two 32x32 frames side-by-side)
    sheet = QPixmap(64, 32)
    sheet.fill(QColor("red"))
    
    # Save to a temporary file (tmp_path is a built-in pytest fixture)
    sheet_path = tmp_path / "test_sheet.png"
    sheet.save(str(sheet_path))

    # Try to load and slice it
    frames = load_sprite_sheet(sheet_path, frame_width=32, frame_height=32)
    
    assert len(frames) == 2
    assert frames[0].width() == 32
    assert frames[0].height() == 32
    assert frames[1].width() == 32

def test_create_placeholder_animations(qapp):
    """Ensure the placeholder generator creates valid data."""
    anims = create_placeholder_animations()
    
    assert "idle" in anims
    assert "walk_left" in anims
    assert "walk_right" in anims
    
    assert len(anims["idle"].frames) > 0
    assert isinstance(anims["idle"].frames[0], QPixmap)
