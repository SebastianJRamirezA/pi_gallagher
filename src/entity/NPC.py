from src.entity import Actor

class NPC(Actor):
    """Non-player character with story and ambient dialogue support."""

    LINES = (
        "Dicen que los Del Roscio perdieron mucho en el crack del 29.",
        "El guardia nocturno del museo ha estado actuando muy nervioso últimamente.",
        "Nadie entra a la trastienda de Cornelius Blackwood sin su permiso.",
    )

    def __init__(
        self,
        x: float,
        y: float,
        name: str,
        dialogue_key: str = "",
        direction: str = "down",
    ) -> None:
        super().__init__(x, y, "npc", name, direction=direction)
        self.dialogue_key = dialogue_key

    def dialogue(self) -> str:
        import random

        return f"{self.name}: {random.choice(self.LINES)}"
