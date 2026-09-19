"""
P.I. Gallagher: The Missing Art

VictoryState — Case Closed / Victory screen after resolving the final confrontation with Sofia.
Displays case resolution dossier, stats, and allows restarting the story or returning to the title menu.
"""

from typing import Any

import pygame
from gale.input_handler import KeyboardData
from gale.state import BaseState

import settings
from src.story.StoryManager import StoryManager


class VictoryState(BaseState):
    def enter(self) -> None:
        self.story = StoryManager.get_instance()
        self.selected_index = 0  # 0: Reiniciar Historia, 1: Menú Principal

        # Play victory / ambient resolution soundtrack
        music_path = settings.BASE_DIR / "assets" / "sounds" / "investigate.mp3"
        if music_path.exists():
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(loops=-1)

        # Button bounding rects for keyboard & mouse support
        btn_w, btn_h = 160, 26
        btn_y = 202
        self.btn_restart_rect = pygame.Rect(
            settings.VIRTUAL_WIDTH // 2 - btn_w - 12, btn_y, btn_w, btn_h
        )
        self.btn_menu_rect = pygame.Rect(
            settings.VIRTUAL_WIDTH // 2 + 12, btn_y, btn_w, btn_h
        )

    def exit(self) -> None:
        pygame.mixer.music.fadeout(500)

    def update(self, dt: float) -> None:
        pass

    def on_input(self, input_id: str, input_data: Any) -> None:
        if isinstance(input_data, KeyboardData) and not input_data.pressed:
            return

        # Navigation
        if input_id in ("move_left", "move_up"):
            self.selected_index = 0
            return
        elif input_id in ("move_right", "move_down"):
            self.selected_index = 1
            return

        # Confirm selection
        if input_id in ("enter", "space"):
            self._execute_option(self.selected_index)
            return

        # Direct shortcuts
        if input_id == "quit":  # ESC key
            self._go_to_main_menu()
            return

        # Check raw key for 'R' shortcut to restart
        if hasattr(input_data, "key"):
            if input_data.key == pygame.K_r:
                self._restart_story()
                return

    def _execute_option(self, index: int) -> None:
        if index == 0:
            self._restart_story()
        else:
            self._go_to_main_menu()

    def _restart_story(self) -> None:
        """Completely reset story progression and start fresh in Gallagher's office."""
        from src.states.PlayState import PlayState

        # 1. Reset story state completely
        self.story.reset()

        # 2. Stop music and clear the entire state stack
        pygame.mixer.music.stop()
        self.state_machine.clear()

        # 3. Launch a fresh PlayState
        self.state_machine.push(PlayState(self.state_machine))

    def _go_to_main_menu(self) -> None:
        """Reset story progression and return to the StartState title screen."""
        from src.states.StartState import StartState

        # 1. Reset story state completely
        self.story.reset()

        # 2. Stop music and clear the entire state stack
        pygame.mixer.music.stop()
        self.state_machine.clear()

        # 3. Launch StartState
        self.state_machine.push(StartState(self.state_machine))

    def render(self, surface: pygame.Surface) -> None:
        # 1. Background and ornamental noir borders
        surface.fill((14, 16, 22))
        pygame.draw.rect(
            surface,
            (45, 50, 65),
            pygame.Rect(4, 4, settings.VIRTUAL_WIDTH - 8, settings.VIRTUAL_HEIGHT - 8),
            1,
        )
        pygame.draw.rect(
            surface,
            (160, 130, 45),
            pygame.Rect(8, 8, settings.VIRTUAL_WIDTH - 16, settings.VIRTUAL_HEIGHT - 16),
            1,
        )

        # 2. Header
        title = settings.FONTS["large"].render("CASO RESUELTO", True, (235, 215, 150))
        surface.blit(title, title.get_rect(center=(settings.VIRTUAL_WIDTH // 2, 28)))

        subtitle = settings.FONTS["small"].render(
            "P.I. GALLAGHER - THE MISSING ART", True, (170, 180, 190)
        )
        surface.blit(subtitle, subtitle.get_rect(center=(settings.VIRTUAL_WIDTH // 2, 48)))

        # Decorative gold divider
        pygame.draw.line(
            surface,
            (180, 145, 50),
            (40, 58),
            (settings.VIRTUAL_WIDTH - 40, 58),
            1,
        )

        # 3. Central Dossier Box
        box_x, box_y, box_w, box_h = 28, 66, settings.VIRTUAL_WIDTH - 56, 126
        pygame.draw.rect(surface, (20, 24, 32), (box_x, box_y, box_w, box_h))
        pygame.draw.rect(surface, (70, 75, 90), (box_x, box_y, box_w, box_h), 1)

        # Dossier Title
        dossier_title = settings.FONTS["small"].render(
            "EXPEDIENTE POLICIAL N 1933-DL - CASO CERRADO", True, (212, 175, 55)
        )
        surface.blit(dossier_title, (box_x + 14, box_y + 8))
        pygame.draw.line(
            surface,
            (50, 55, 70),
            (box_x + 10, box_y + 24),
            (box_x + box_w - 10, box_y + 24),
            1,
        )

        # Bullet points
        lines = [
            ("- Cuadro 'La Dama del Lirio':", " Recuperado de la boveda de Niko Stieger."),
            ("- Guardia Morales:", " Confeso el soborno y su complicidad en el museo."),
            ("- Niko Stieger 'El Tigre':", " Neutralizado en el sotano del Club Velvet."),
            ("- Sofia Del Roscio:", " Desmascarada como socia de Blackwood y detenida."),
        ]
        for i, (bold_txt, desc_txt) in enumerate(lines):
            ly = box_y + 32 + (i * 17)
            s1 = settings.FONTS["small"].render(bold_txt, True, (230, 210, 140))
            s2 = settings.FONTS["small"].render(desc_txt, True, (200, 205, 215))
            surface.blit(s1, (box_x + 14, ly))
            surface.blit(s2, (box_x + 14 + s1.get_width() + 4, ly))

        # Stats bar
        pygame.draw.line(
            surface,
            (50, 55, 70),
            (box_x + 10, box_y + 104),
            (box_x + box_w - 10, box_y + 104),
            1,
        )
        cards_count = len(self.story.collected_cards)
        deductions_count = len(self.story.validated_deductions)
        stats_txt = settings.FONTS["small"].render(
            f"Pistas: {cards_count}/18   |   Deducciones: {deductions_count}/5   |   Veredicto: EXITO TOTAL",
            True,
            (160, 195, 210),
        )
        surface.blit(stats_txt, stats_txt.get_rect(center=(box_x + box_w // 2, box_y + 114)))

        # 4. Interactive Buttons
        # Button 0: Reiniciar Historia
        is_b0 = self.selected_index == 0
        bg0 = (55, 45, 22) if is_b0 else (22, 26, 34)
        border0 = (235, 195, 80) if is_b0 else (60, 65, 80)
        col0 = (255, 235, 150) if is_b0 else (160, 165, 175)
        pygame.draw.rect(surface, bg0, self.btn_restart_rect)
        pygame.draw.rect(surface, border0, self.btn_restart_rect, 2 if is_b0 else 1)
        prefix0 = "> " if is_b0 else "  "
        t0 = settings.FONTS["medium"].render(f"{prefix0}Reiniciar Historia", True, col0)
        surface.blit(t0, t0.get_rect(center=self.btn_restart_rect.center))

        # Button 1: Menú Principal
        is_b1 = self.selected_index == 1
        bg1 = (55, 45, 22) if is_b1 else (22, 26, 34)
        border1 = (235, 195, 80) if is_b1 else (60, 65, 80)
        col1 = (255, 235, 150) if is_b1 else (160, 165, 175)
        pygame.draw.rect(surface, bg1, self.btn_menu_rect)
        pygame.draw.rect(surface, border1, self.btn_menu_rect, 2 if is_b1 else 1)
        prefix1 = "> " if is_b1 else "  "
        t1 = settings.FONTS["medium"].render(f"{prefix1}Menu Principal", True, col1)
        surface.blit(t1, t1.get_rect(center=self.btn_menu_rect.center))

        # 5. Footer instructions
        footer = settings.FONTS["small"].render(
            "[FLECHAS] Seleccionar   *   [ENTER / ESPACIO] Confirmar   *   [ESC] Salir",
            True,
            (120, 125, 135),
        )
        surface.blit(footer, footer.get_rect(center=(settings.VIRTUAL_WIDTH // 2, 246)))

