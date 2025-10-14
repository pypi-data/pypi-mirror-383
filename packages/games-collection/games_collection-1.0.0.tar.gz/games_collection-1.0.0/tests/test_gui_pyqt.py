"""Tests for PyQt5 GUI implementations.

These tests verify that PyQt5-based GUI components work correctly.
"""

from __future__ import annotations

import pathlib
import sys

import pytest

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Check if PyQt5 is available
try:
    from PyQt5 import QtWidgets  # noqa: F401

    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False

pytestmark = pytest.mark.skipif(not PYQT5_AVAILABLE, reason="PyQt5 not available")


@pytest.mark.gui
class TestDotsAndBoxesPyQt:
    """Test Dots and Boxes PyQt5 GUI components."""

    def test_dots_boxes_pyqt_gui_import(self):
        """Test that Dots and Boxes PyQt5 GUI can be imported."""
        from paper_games.dots_and_boxes.gui_pyqt import DotsAndBoxesGUI

        assert DotsAndBoxesGUI is not None

    @pytest.mark.skipif(not sys.platform.startswith("linux") or not sys.stdout.isatty(), reason="Requires display")
    def test_dots_boxes_pyqt_gui_initialization(self, qtbot):
        """Test Dots and Boxes PyQt5 GUI initialization."""
        try:
            from paper_games.dots_and_boxes.gui_pyqt import DotsAndBoxesGUI

            window = DotsAndBoxesGUI(size=2, show_hints=False)
            qtbot.addWidget(window)
            assert window is not None
            assert window.game is not None
            assert window.size == 2
            assert window.player_turn is True
        except Exception as e:
            if "display" in str(e).lower() or "DISPLAY" in str(e):
                pytest.skip("No display available for GUI testing")
            raise


@pytest.mark.gui
class TestBaseGUIPyQt:
    """Test PyQt5 BaseGUI components."""

    def test_base_gui_pyqt_import(self):
        """Test that PyQt5 BaseGUI can be imported."""
        from common.gui_base_pyqt import BaseGUI, GUIConfig

        assert BaseGUI is not None
        assert GUIConfig is not None

    def test_gui_config_defaults(self):
        """Test GUIConfig default values."""
        from common.gui_base_pyqt import GUIConfig

        config = GUIConfig()
        assert config.window_title == "Game"
        assert config.window_width == 800
        assert config.window_height == 600
        assert config.enable_sounds is False
        assert config.enable_animations is True


@pytest.mark.gui
def test_pyqt5_modules_available():
    """Test that PyQt5 GUI modules can be imported."""
    gui_modules = [
        "paper_games.dots_and_boxes.gui_pyqt",
        "common.gui_base_pyqt",
    ]

    available_modules = []
    for module_name in gui_modules:
        try:
            __import__(module_name)
            available_modules.append(module_name)
        except ImportError as e:
            if "pyqt5" not in str(e).lower():
                raise

    # At least some GUI modules should be available if PyQt5 is present
    if PYQT5_AVAILABLE:
        assert len(available_modules) > 0, "No PyQt5 GUI modules available despite PyQt5 being present"
