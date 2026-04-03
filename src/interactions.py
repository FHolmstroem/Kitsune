"""
Click, drag, and shoo handling.
"""

from PyQt6.QtCore import QObject, QEvent, Qt, QPoint
from PyQt6.QtGui import QMouseEvent, QAction
from PyQt6.QtWidgets import QMenu, QApplication

from pet import Pet, PetState
from overlay import Overlay


class InteractionHandler(QObject):
    """Intercepts mouse events on the Overlay and routes them to the Pet."""

    def __init__(self, overlay: Overlay, pet: Pet) -> None:
        super().__init__(overlay)
        self.overlay = overlay
        self.pet = pet

        self.is_dragging = False
        self.drag_offset = QPoint()
        self.has_moved = False

        self.overlay.installEventFilter(self)

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        if obj is not self.overlay:
            return super().eventFilter(obj, event)

        if event.type() == QEvent.Type.MouseButtonPress:
            return self._handle_mouse_press(event)
        elif event.type() == QEvent.Type.MouseMove:
            return self._handle_mouse_move(event)
        elif event.type() == QEvent.Type.MouseButtonRelease:
            return self._handle_mouse_release(event)

        return super().eventFilter(obj, event)

    def _handle_mouse_press(self, event: QMouseEvent) -> bool:
        click_pos = event.position().toPoint()
        if not self.overlay.sprite_rect.contains(click_pos):
            return False

        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.has_moved = False
            self.drag_offset = click_pos - self.overlay.sprite_rect.topLeft()
            return True

        elif event.button() == Qt.MouseButton.RightButton:
            self._show_context_menu(event.globalPosition().toPoint())
            return True

        return False

    def _handle_mouse_move(self, event: QMouseEvent) -> bool:
        if not self.is_dragging:
            return False

        self.has_moved = True
        new_pos = event.position().toPoint() - self.drag_offset
        
        self.pet.x = float(new_pos.x())
        self.pet.y = float(new_pos.y())
        self.overlay.set_position(new_pos.x(), new_pos.y())
        return True

    def _handle_mouse_release(self, event: QMouseEvent) -> bool:
        if event.button() == Qt.MouseButton.LeftButton and self.is_dragging:
            self.is_dragging = False
            
            if not self.has_moved:
                self._shoo_fox()
                
            return True
        return False

    def _shoo_fox(self) -> None:
        if self.pet.x > (self.pet.max_x / 2.0):
            self.pet.enter_state(PetState.FLEEING_LEFT)
        else:
            self.pet.enter_state(PetState.FLEEING_RIGHT)

    def _show_context_menu(self, global_pos: QPoint) -> None:
        menu = QMenu()
        
        laser_text = "Turn Laser Off" if self.pet.is_laser_active else "Turn Laser On"
        laser_action = QAction(laser_text, menu)
        laser_action.triggered.connect(self._toggle_laser)
        menu.addAction(laser_action)
        
        menu.addSeparator()

        quit_action = QAction("Quit Kitsune", menu)
        app = QApplication.instance()
        if app:
            quit_action.triggered.connect(app.quit)
            
        menu.addAction(quit_action)
        menu.exec(global_pos)

    def _toggle_laser(self) -> None:
        self.pet.is_laser_active = not self.pet.is_laser_active
        if not self.pet.is_laser_active:
            self.pet.enter_state(PetState.IDLE)