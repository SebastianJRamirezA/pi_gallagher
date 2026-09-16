"""
P.I. Gallagher: The Missing Art

This file contains the main program to run the game.
"""

from src.states.Safecracker import Safecracker
from src.PiGallagher import PiGallagher

if __name__ == "__main__":
    game = PiGallagher()
    game.exec()
