"""
P.I. Gallagher: The Missing Art

BaseEntityState — base class for all entity (character) states.
Follows the same pattern as 06_princess: each state holds a reference
to the entity it controls and to the entity's own StateMachine.
"""

from typing import TypeVar

from gale.state import BaseState, StateMachine


class BaseEntityState(BaseState):
    def __init__(
        self, entity: TypeVar("Actor"), state_machine: StateMachine
    ) -> None:
        super().__init__(state_machine)
        self.entity = entity

