from .__main__ import main
from .XOX_game import xox
from .pingpong_game import ping_pong
from .snake_game import snake_game

try:
    import tkinter
except ImportError:
    raise ImportError(
        "Tkinter is required but not found. "
        "On Linux, install it with: sudo apt-get install python3-tk"
    )