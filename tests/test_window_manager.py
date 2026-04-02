"""Tests for window_manager.py."""

import sys
import pytest

if sys.platform != "win32":
    pytest.skip("pygetwindow only supports Windows", allow_module_level=True)

from unittest.mock import patch, MagicMock
from window_manager import WindowRect, get_windows


def test_window_rect_properties():
    """Ensure the right and bottom coordinate helpers calculate correctly."""
    rect = WindowRect("Test App", x=10, y=20, width=100, height=200)
    assert rect.right == 110
    assert rect.bottom == 220


@patch("window_manager.gw.getAllWindows")
def test_get_windows_filters_correctly(mock_get_all):
    """It should ignore invisible, minimized, and title-less windows."""
    
    # Create mock pygetwindow objects
    valid_win = MagicMock(
        title="Firefox", visible=True, isMinimized=False, 
        left=0, top=0, width=1000, height=800
    )
    hidden_win = MagicMock(title="Background Task", visible=False, isMinimized=False)
    minimized_win = MagicMock(title="Spotify", visible=True, isMinimized=True)
    no_title_win = MagicMock(title="", visible=True, isMinimized=False)

    # Make the mock return our specific list
    mock_get_all.return_value = [
        valid_win, 
        hidden_win, 
        minimized_win, 
        no_title_win
    ]

    windows = get_windows()

    # Only the valid window should make it through the filter
    assert len(windows) == 1
    assert windows[0].title == "Firefox"
    assert windows[0].x == 0
    assert windows[0].width == 1000
    