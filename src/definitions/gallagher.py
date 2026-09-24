"""
P.I. Gallagher: The Missing Art

Animation and entity definitions for Gallagher (player character).

Spritesheet: gallagher.png — 80x101 pixels, 4 columns x 3 rows of 20x33 frames.
  Row 0 (frames 0-3): walking down (frames 0, 1 used)
  Row 1 (frames 4-7): looking/walking up (frames 4, 5 used)
  Row 2 (frames 8-11): walking right (frames 8, 9, 10, 11 used; flipped horizontally for facing left)
"""

from typing import Any, Dict

GALLAGHER_DEFS: Dict[str, Any] = {
    "walk_speed": 150,
    "animations": {
        # Idle — single frame per direction
        "idle-down": {"frames": [0], "texture": "gallagher"},
        "idle-up": {"frames": [4], "texture": "gallagher"},
        "idle-right": {"frames": [8], "texture": "gallagher"},
        "idle-left": {"frames": [8], "texture": "gallagher"},
        # Walk cycles
        "walk-down": {
            "frames": [0, 1],
            "interval": 0.20,
            "texture": "gallagher",
        },
        "walk-up": {
            "frames": [4, 5],
            "interval": 0.20,
            "texture": "gallagher",
        },
        "walk-right": {
            "frames": [8, 9, 10, 11],
            "interval": 0.15,
            "texture": "gallagher",
        },
        "walk-left": {
            "frames": [8, 9, 10, 11],
            "interval": 0.15,
            "texture": "gallagher",
        },
    },
}

