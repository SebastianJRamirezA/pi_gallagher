"""
P.I. Gallagher: The Missing Art

PoliceArchiveState — Main state for Minigame 1: Police Archive (Lauren).
Uses HierarchicalState with a sub-state machine to manage:
  IntroSubstate   → PhaseASubstate ↔ PhaseAFailSubstate
                  → PhaseBSubstate ↔ PhaseBFailSubstate
                  → SuccessSubstate
"""

from gale.state import HierarchicalState
from gale.timer import Timer

from src.states.archive_substates.IntroSubstate import IntroSubstate
from src.states.archive_substates.PhaseASubstate import PhaseASubstate
from src.states.archive_substates.PhaseAFailSubstate import PhaseAFailSubstate
from src.states.archive_substates.PhaseBSubstate import PhaseBSubstate
from src.states.archive_substates.PhaseBFailSubstate import PhaseBFailSubstate
from src.states.archive_substates.SuccessSubstate import SuccessSubstate


class PoliceArchiveState(HierarchicalState):
    """
    Top-level state for the Police Archive minigame, pushed onto the
    game's StateStack.  Shared data (collected clues, expedition status)
    lives here so sub-states can read/write it freely.
    """

    def __init__(self, state_machine):
        super().__init__(
            state_machine,
            substates={
                "intro": lambda sm: IntroSubstate(sm, self),
                "phase_a": lambda sm: PhaseASubstate(sm, self),
                "phase_a_fail": lambda sm: PhaseAFailSubstate(sm, self),
                "phase_b": lambda sm: PhaseBSubstate(sm, self),
                "phase_b_fail": lambda sm: PhaseBFailSubstate(sm, self),
                "success": lambda sm: SuccessSubstate(sm, self),
            },
            initial_substate="intro",
        )
        # Shared minigame data
        self.collected_clues = []
        self.expedition_found = False

    def exit(self):
        """Clean up all timers when leaving the minigame entirely."""
        self.substate_machine.current.exit()
        Timer.clear()
