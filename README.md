# Video Game Programming I

P.I. Gallagher: The Missing Art is a noir-inspired detective game set in a city where bureaucracy and corruption run deep. When a priceless Renaissance masterwork vanishes from the Del Roscio Museum, private investigator Tim Gallagher and his partner Lauren Summers take on a case that the police couldn't—or wouldn't—solve. What begins as a straightforward recovery job quickly unravels into a web of deceit, high-stakes heist operations, and gang-land corruption.

This videogame was developed as a final project for the *Video Game Programming I*
(ISPPV1) course at Universidad de Los Andes (ULA), Venezuela.

## Getting started

The project follows the following layout:

```
├── main.py          # Entry point: creates and runs the game instance
├── settings.py       # Window/virtual resolution, input bindings, fonts, constants
├── src/               # Game-specific code (states, entities, world, etc.)
└── assets/            # Images, spritesheets, sounds and fonts (when applicable)
```

## Requirements

- Python 3.12+
- A single dependency shared by every project: [`gale-engine`](https://pypi.org/project/gale-engine/)
  (which in turn depends on Pygame). It is declared once in the
  [`requirements.txt`](requirements.txt) at the root of this repository, since
  every study case uses the exact same dependency.

## Setup

Clone the repository and create a virtual environment at the root:

```bash
git clone https://github.com/SebastianJRamirezA/pi_gallagher.git
cd pi_gallagher
python3 -m venv .venv
source .venv/bin/activate       # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Running the game

```bash
python main.py
```
