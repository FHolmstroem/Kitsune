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
from animation import AnimationController, create_placeholder_animations
from pet import Pet, PetState
from interactions import InteractionHandler
from animation import AnimationController, Animation, load_sprite_sheet
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QTransform
from pet import Pet, PetState


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
    """Let Ctrl+C in the terminal kill the app."""
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    timer = QTimer(app)
    timer.timeout.connect(lambda: None)
    timer.start(200)


def _setup_tray(app: QApplication) -> QSystemTrayIcon:
    """Create a system tray icon with a Quit option."""
    tray = QSystemTrayIcon(_make_tray_icon(), app)
    menu = QMenu()
    quit_action = QAction("Quit Kitsune", menu)
    quit_action.triggered.connect(app.quit)
    menu.addAction(quit_action)
    tray.setContextMenu(menu)
    tray.setToolTip("Kitsune 🦊")
    tray.show()
    return tray


def _setup_animations() -> AnimationController:
    """Initialize the animation state machine with real cat sprites."""
    anim_controller = AnimationController()
    
    # --- UPDATED SIZING MATH ---
    frame_width = 80   # 640 total width / 8 frames = 80
    frame_height = 64  # Total height of the image
    
    # Since 80x64 is already decent size, let's just scale it by 1.5 or 2 
    # instead of 3 so it's a normal sized pet. (Change to 1 if it's still too big!)
    scale_factor = 2   
    new_size = QSize(int(frame_width * scale_factor), int(frame_height * scale_factor))

    def load_and_scale(filename: str, flip_horizontal: bool = False) -> list:
        """Helper to load a specific file, scale it, and optionally mirror it."""
        path = f"assets/sprites/{filename}"
        
        # This will now correctly slice the image into 8 blocks of 80x64
        frames = load_sprite_sheet(path, frame_width, frame_height)
        
        if not frames:
            print(f"Warning: Could not load {path}. Falling back to empty frames.")
            return []
        
        # Scale up using FastTransformation to keep pixel art sharp
        scaled = [f.scaled(new_size) for f in frames]
        
        # Mirror the image for left-facing movement
        if flip_horizontal:
            transform = QTransform().scale(-1, 1)
            scaled = [f.transformed(transform) for f in scaled]
            
        return scaled

    # 1. Load the files
    # Note: Assuming the original drawings face RIGHT. If your cat walks backwards, swap the True/False!
    idle_frames = load_and_scale("IDLE.png")
    walk_right_frames = load_and_scale("WALK.png", flip_horizontal=True)
    walk_left_frames = load_and_scale("WALK.png", flip_horizontal=False)
    run_right_frames = load_and_scale("RUN.png", flip_horizontal=True)
    run_left_frames = load_and_scale("RUN.png", flip_horizontal=False)

    # 2. Register the base animations (Adjust FPS to make the walk cycle look natural)
    anim_controller.add_animation(PetState.IDLE, Animation(frames=idle_frames, fps=6))
    anim_controller.add_animation(PetState.WALKING_RIGHT, Animation(frames=walk_right_frames, fps=10))
    anim_controller.add_animation(PetState.WALKING_LEFT, Animation(frames=walk_left_frames, fps=10))
    
    # 3. Register the RUN/FLEEING animations
    anim_controller.add_animation(PetState.FLEEING_RIGHT, Animation(frames=run_right_frames, fps=15))
    anim_controller.add_animation(PetState.FLEEING_LEFT, Animation(frames=run_left_frames, fps=15))
    
    # 4. Map the vertical/diagonal logic to existing visuals so it doesn't crash
    anim_controller.add_animation(PetState.WALK_UP, Animation(frames=walk_right_frames, fps=10))
    anim_controller.add_animation(PetState.WALK_DOWN, Animation(frames=walk_left_frames, fps=10))
    anim_controller.add_animation(PetState.DIAG_UP_RIGHT, Animation(frames=walk_right_frames, fps=10))
    anim_controller.add_animation(PetState.DIAG_DOWN_LEFT, Animation(frames=walk_left_frames, fps=10))
    
    return anim_controller


def _setup_pet(app: QApplication) -> Pet:
    """Create the logic brain and set its screen boundaries."""
    screen = app.primaryScreen()
    screen_rect = screen.geometry()

    sprite_size = 48
    max_x = float(screen_rect.width() - sprite_size)
    max_y = float(screen_rect.height() - sprite_size)  # Calculate Y bounds

    # Start the fox in the middle of the screen
    fox_logic = Pet(start_x=max_x / 2.0, start_y=max_y / 2.0)
    # Pass all 4 boundaries
    fox_logic.set_boundaries(min_x=0.0, max_x=max_x, min_y=0.0, max_y=max_y)
    return fox_logic


def _setup_game_loop(overlay: Overlay, fox_logic: Pet, anim_controller: AnimationController) -> None:
    """Wire the logic, animations, and Qt update loop together."""
    
    def game_loop_tick():
        delta = overlay.TICK_MS

        fox_logic.tick(delta)
        anim_controller.play(str(fox_logic.state.value))

        frame = anim_controller.tick(delta)
        if frame:
            overlay.set_sprite(frame)

        overlay.set_position(int(fox_logic.x), int(fox_logic.y))

        # Safer way to force the Qt repaint
        overlay.update()
        
        print(f"State: {fox_logic.state.value:10} | Pos: ({int(fox_logic.x):4}, {int(fox_logic.y):4})", end="\r")

    overlay._tick_timer.timeout.disconnect()
    overlay._tick_timer.timeout.connect(game_loop_tick)


def main() -> None:
    """Launch Kitsune."""
    app = QApplication(sys.argv)

    # Setup core application systems
    _setup_signal_handling(app)
    tray = _setup_tray(app)  # noqa: F841

    # Create the components
    overlay = Overlay()
    anim_controller = _setup_animations()
    fox_logic = _setup_pet(app)

    # Wire up the mouse events
    interaction_handler = InteractionHandler(overlay, fox_logic)

    _setup_game_loop(overlay, fox_logic, anim_controller)

    # Bind them together
    _setup_game_loop(overlay, fox_logic, anim_controller)

    # Display the app
    overlay.show()

    # Keyboard shortcuts
    shortcut = QShortcut(QKeySequence("Ctrl+Q"), overlay)
    shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
    shortcut.activated.connect(app.quit)

    print("🦊 Kitsune is running! Quit with Ctrl+Q or Ctrl+C in this terminal.")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()