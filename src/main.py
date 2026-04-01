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
from pet import Pet
from interactions import InteractionHandler


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
    """Initialize the animation state machine with sprites."""
    anim_controller = AnimationController()
    placeholders = create_placeholder_animations()
    anim_controller.add_animation("idle", placeholders["idle"])
    anim_controller.add_animation("walk_left", placeholders["walk_left"])
    anim_controller.add_animation("walk_right", placeholders["walk_right"])
    return anim_controller


def _setup_pet(app: QApplication) -> Pet:
    """Create the logic brain and set its screen boundaries."""
    screen = app.primaryScreen()
    screen_rect = screen.geometry()

    sprite_size = 48
    max_x = float(screen_rect.width() - sprite_size)
    
    # 🐛 DEBUG FIX: Force the Y coordinate to the exact middle of the screen
    # so we know for a fact it isn't hiding behind the taskbar.
    ground_y = float(screen_rect.height() / 2.0) 

    # Start the fox in the middle of the screen
    fox_logic = Pet(start_x=max_x / 2.0, start_y=ground_y)
    fox_logic.set_boundaries(min_x=0.0, max_x=max_x)
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