"""
OS window detection via PyGetWindow.

Wraps pygetwindow to provide a clean list of open windows with their
position and size. The fox uses this to know where window edges are
so it can hide behind them, walk along their top edges, and peek out.
"""

from dataclasses import dataclass
import pygetwindow as gw


@dataclass
class WindowRect:
    """Clean representation of an OS window's geometry."""
    title: str
    x: int
    y: int
    width: int
    height: int

    @property
    def right(self) -> int:
        """Helper for collision detection on the right edge."""
        return self.x + self.width

    @property
    def bottom(self) -> int:
        """Helper for collision detection on the bottom edge."""
        return self.y + self.height


def get_windows() -> list[WindowRect]:
    """Return a list of visible, non-minimized windows."""
    windows = []
    
    try:
        # gw.getAllWindows() fetches everything, including hidden background tasks
        all_windows = gw.getAllWindows()
    except Exception as e:
        print(f"Warning: Failed to fetch windows: {e}")
        return []

    for win in all_windows:
        # We only care about windows the user can actually see
        if win.title and win.visible and not win.isMinimized:
            windows.append(
                WindowRect(
                    title=win.title,
                    x=win.left,
                    y=win.top,
                    width=win.width,
                    height=win.height
                )
            )
            
    return windows