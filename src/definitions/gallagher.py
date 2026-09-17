"""
P.I. Gallagher: The Missing Art

Animation and entity definitions for Gallagher (player character).

Spritesheet: gallagher.png — 57×112 pixels, 3 columns × 4 rows of 19×28 frames.
  Row 0 (frames 0-2): facing down
  Row 1 (frames 3-5): facing up
  Row 2 (frames 6-8): facing right
  Row 3 (frames 9-11): facing left

Each row: frame 0 = idle/neutral, frames 1-2 = walk cycle steps.
"""

from typing import Any, Dict

GALLAGHER_DEFS: Dict[str, Any] = {
    "walk_speed": 150,
    "animations": {
        # Idle — single frame per direction
        "idle-down": {"frames": [0], "texture": "gallagher"},
        "idle-up": {"frames": [3], "texture": "gallagher"},
        "idle-right": {"frames": [6], "texture": "gallagher"},
        "idle-left": {"frames": [9], "texture": "gallagher"},
        # Walk — 4-step cycle: neutral, step A, neutral, step B
        "walk-down": {
            "frames": [0, 1, 0, 2],
            "interval": 0.15,
            "texture": "gallagher",
        },
        "walk-up": {
            "frames": [3, 4, 3, 5],
            "interval": 0.15,
            "texture": "gallagher",
        },
        "walk-right": {
            "frames": [6, 7, 6, 8],
            "interval": 0.15,
            "texture": "gallagher",
        },
        "walk-left": {
            "frames": [9, 10, 9, 11],
            "interval": 0.15,
            "texture": "gallagher",
        },
    },
}

