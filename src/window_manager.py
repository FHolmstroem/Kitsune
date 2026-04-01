"""
OS window detection via PyGetWindow.

Wraps pygetwindow to provide a clean list of open windows with their
position and size. The fox uses this to know where window edges are
so it can hide behind them, walk along their top edges, and peek out.

Main interface:
    get_windows() -> list[WindowRect]

WindowRect is a simple dataclass with: title, x, y, width, height.
"""
