import sys
from pathlib import Path
import pygame

# Set up paths so we can import from src
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

import settings
from gale.state import StateMachine
from src.states.ConfrontationState import ConfrontationState
from src.story.StoryManager import StoryManager


from gale.game import Game
from gale.state import StateStack
from gale.input_handler import InputData

class TestGame(Game):
    def __init__(self, confrontation_id):
        self.confrontation_id = confrontation_id
        super().__init__(
            settings.TITLE,
            settings.WINDOW_WIDTH,
            settings.WINDOW_HEIGHT,
            settings.VIRTUAL_WIDTH,
            settings.VIRTUAL_HEIGHT
        )

    def init(self):
        self.state_stack = StateStack()
        self.state_stack.push(ConfrontationState(self.state_stack), confrontation_id=self.confrontation_id, on_complete=lambda: sys.exit(0))
        
    def update(self, dt: float) -> None:
        self.state_stack.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((40, 40, 40))
        self.state_stack.render(surface)

    def on_input(self, input_id: str, input_data: InputData) -> None:
        self.state_stack.on_input(input_id, input_data)

def main():
    story = StoryManager.get_instance()
    
    print("Elige el careo a probar:")
    print("1. Morales (con C01, C02, C03)")
    print("2. Sofia (básico, sin flags extra)")
    print("3. Sofia (con 'doble_cobro_deducido')")
    print("4. Sofia (con todos los flags: 'doble_cobro_deducido', 'traicion_deducida')")
    
    choice = input("Opción (1-4): ").strip()
    
    confrontation_id = "morales"
    
    if choice == "1":
        story.collected_cards = {"C01", "C02", "C03"}
        confrontation_id = "morales"
    elif choice == "2":
        story.collected_cards = {"C07", "C09", "C10", "C11", "C13", "C15"}
        confrontation_id = "sofia"
    elif choice == "3":
        story.collected_cards = {"C07", "C09", "C10", "C11", "C13", "C15"}
        story.flags["doble_cobro_deducido"] = True
        confrontation_id = "sofia"
    elif choice == "4":
        story.collected_cards = {"C07", "C09", "C10", "C11", "C13", "C15"}
        story.flags["doble_cobro_deducido"] = True
        story.flags["traicion_deducida"] = True
        confrontation_id = "sofia"
    else:
        print("Opción inválida. Saliendo.")
        sys.exit(0)
        
    game = TestGame(confrontation_id)
    game.exec()

if __name__ == "__main__":
    main()
