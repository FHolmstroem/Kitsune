"""
Sprite loading and frame cycling.

Handles loading sprite sheets from assets/sprites/, splitting them
into individual frames, and cycling through them at a given FPS.

Each animation (walk_left, walk_right, idle, sleep, etc.) is a
named sequence of frames. The AnimationController keeps track of
which animation is playing and which frame we're on.
"""
"""
Sprite loading and frame cycling.

Handles loading sprite sheets from assets/sprites/, splitting them
into individual frames, and cycling through them at a given FPS.

Each animation (walk_left, walk_right, idle, sleep, etc.) is a
named sequence of frames. The AnimationController keeps track of
which animation is playing and which frame we're on.
"""

from dataclasses import dataclass
from pathlib import Path

from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QPixmap, QColor, QPainter


@dataclass
class Animation:
    """A sequence of frames representing one state (e.g., walk_left)."""
    frames: list[QPixmap]
    fps: int = 10

    @property
    def frame_duration_ms(self) -> float:
        """How long each frame should stay on screen."""
        return 1000.0 / self.fps if self.fps > 0 else 0.0


class AnimationController:
    """Manages playing and switching between animations."""

    def __init__(self) -> None:
        self.animations: dict[str, Animation] = {}
        self.current_anim_name: str | None = None
        self.current_frame_idx: int = 0
        self._time_accumulator_ms: float = 0.0

    def add_animation(self, name: str, animation: Animation) -> None:
        """Register a new animation sequence."""
        self.animations[name] = animation

    def play(self, name: str) -> None:
        """Switch to a new animation. Resets frame counter if it's a new state."""
        if name not in self.animations:
            return
            
        if name != self.current_anim_name:
            self.current_anim_name = name
            self.current_frame_idx = 0
            self._time_accumulator_ms = 0.0

    def tick(self, delta_ms: float) -> QPixmap | None:
        """Advance the animation by delta_ms and return the current frame."""
        if not self.current_anim_name:
            return None

        anim = self.animations[self.current_anim_name]
        if not anim.frames:
            return None

        self._time_accumulator_ms += delta_ms
        duration = anim.frame_duration_ms

        # Advance frame if enough time has passed
        if duration > 0:
            while self._time_accumulator_ms >= duration:
                self._time_accumulator_ms -= duration
                self.current_frame_idx = (self.current_frame_idx + 1) % len(anim.frames)

        return anim.frames[self.current_frame_idx]

    @property
    def current_frame(self) -> QPixmap | None:
        """Get the current frame without advancing the timer."""
        if not self.current_anim_name:
            return None
        anim = self.animations.get(self.current_anim_name)
        if not anim or not anim.frames:
            return None
        return anim.frames[self.current_frame_idx]


def load_sprite_sheet(path: str | Path, frame_width: int, frame_height: int) -> list[QPixmap]:
    """Slice a sprite sheet image into individual QPixmap frames."""
    sheet = QPixmap(str(path))
    if sheet.isNull():
        print(f"Warning: Failed to load sprite sheet {path}")
        return []

    frames = []
    cols = sheet.width() // frame_width
    rows = sheet.height() // frame_height

    for row in range(rows):
        for col in range(cols):
            rect = QRect(col * frame_width, row * frame_height, frame_width, frame_height)
            frames.append(sheet.copy(rect))

    return frames


# ----------------------------------------------------------------------
# TEMPORARY: Blob Generator (Delete once you have real Fox sprites)
# ----------------------------------------------------------------------
def _generate_blob_frames(color: QColor, eye_offset_x: int) -> list[QPixmap]:
    """Draw a bouncing blob with eyes looking in a specific direction."""
    frames = []
    # y-offsets to create a simple bouncing animation sequence
    for bounce in [0, 2, 4, 2]:  
        pixmap = QPixmap(48, 48)
        pixmap.fill(QColor(0, 0, 0, 0))  # Transparent background
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw blob body
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        # Squash and stretch slightly based on bounce
        painter.drawEllipse(8, 16 + bounce, 32, 24 - (bounce // 2))

        # Draw eyes (black dots)
        painter.setBrush(QColor(30, 30, 30))
        eye_y = 24 + bounce
        painter.drawEllipse(18 + eye_offset_x, eye_y, 4, 4)
        painter.drawEllipse(26 + eye_offset_x, eye_y, 4, 4)

        painter.end()
        frames.append(pixmap)
        
    return frames

def create_placeholder_animations() -> dict[str, Animation]:
    """Returns a dictionary of ready-to-use blob animations."""
    return {
        "idle": Animation(_generate_blob_frames(QColor(200, 200, 200), eye_offset_x=0), fps=4),
        "walk_left": Animation(_generate_blob_frames(QColor(150, 200, 255), eye_offset_x=-4), fps=8),
        "walk_right": Animation(_generate_blob_frames(QColor(255, 150, 150), eye_offset_x=4), fps=8),
    }