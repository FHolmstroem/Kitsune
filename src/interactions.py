"""
Click, drag, and shoo handling.

Processes mouse events from the overlay and translates them into
actions for the Pet:

    - Left click on fox  → shoo (fox runs away)
    - Click and drag     → pick up and move the fox
    - Right click on fox → context menu (quit, settings, etc.)

All mouse events come from the Overlay widget. This module maps
them to Pet state changes.
"""
