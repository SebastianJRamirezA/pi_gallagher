from typing import Any, Callable, Dict, List, Optional, Tuple

import pygame

from gale.input_handler import KeyboardData
from gale.state import BaseState
from gale.ui import Container, Label, UIManager, Window

import settings
from src.data.confrontation_data import MORALES_CONFRONTATION, SOFIA_CONFRONTATION, ConfrontationPhase
from src.story.StoryManager import StoryManager
from src.ui import CardButton, CardGridContainer, DialogueTextBox
from src.ui.theme import NOIR_CARD_THEME, NOIR_DIALOGUE_THEME


class ConfrontationState(BaseState):
    def enter(
        self,
        confrontation_id: str,
        on_complete: Optional[Callable[[], None]] = None,
    ) -> None:
        self.story = StoryManager.get_instance()
        self.on_complete = on_complete

        music_path = settings.BASE_DIR / "assets" / "sounds" / "investigate.mp3"
        if music_path.exists():
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(loops=-1)

        # Select confrontation
        if confrontation_id == "morales":
            self.phases = MORALES_CONFRONTATION
            self.npc_name = "Morales"
        elif confrontation_id == "sofia":
            self.phases = SOFIA_CONFRONTATION
            self.npc_name = "Sofia Del Roscio"
        else:
            raise ValueError(f"Unknown confrontation_id: {confrontation_id}")

        # Filter phases by condition flag
        self.active_phases = [
            p for p in self.phases
            if p.condition_flag is None or self.story.flags.get(p.condition_flag, False)
        ]

        self.current_phase_index = 0
        self.selected_card_ids: List[str] = []

        # State machine for current phase: "statement" -> ("fail_reaction" -> "statement") or "success_reaction"
        self.phase_substate = "statement"

        self._build_ui()

    def _get_current_phase(self) -> ConfrontationPhase:
        return self.active_phases[self.current_phase_index]

    def _build_ui(self) -> None:
        # Load player's cards
        self.cards = self.story.get_available_cards_for_corkboard()
        self.cards.sort(key=lambda c: c["id"])

        self.root = Container(0, 0, settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT)

        # 1. Dialogue Window matching DialogueState styling
        win_x = 16
        win_y = 16
        win_w = settings.VIRTUAL_WIDTH - 32
        win_h = 88

        self.npc_window = Window(
            win_x,
            win_y,
            win_w,
            win_h,
            title="",
            closable=False,
            theme=NOIR_DIALOGUE_THEME,
        )

        # Speaker Plaque Header
        self.speaker_label = Label(
            win_x + 12,
            win_y + 8,
            text=self.npc_name.upper(),
            font=settings.FONTS.get("bold", settings.FONTS["medium"]),
            color=pygame.Color(212, 175, 55),
            theme=NOIR_DIALOGUE_THEME,
        )
        self.npc_window.add_child(self.speaker_label)

        # Typewriter Text Box
        self.npc_textbox = DialogueTextBox(
            win_x + 12,
            win_y + 26,
            win_w - 24,
            42,
            pages="",
            lines_per_page=3,
            on_close=self._on_typewriter_finished,
            theme=NOIR_DIALOGUE_THEME,
        )
        self.npc_window.add_child(self.npc_textbox)

        # Bottom Hint Label within Dialogue Window
        self.hint_label = Label(
            win_x + 12,
            win_y + win_h - 16,
            text="",
            font=settings.FONTS["small"],
            color=pygame.Color(160, 150, 135),
            theme=NOIR_DIALOGUE_THEME,
        )
        self.npc_window.add_child(self.hint_label)
        self.root.add_child(self.npc_window)

        # 2. Horizontal Card Layout (1 Row x Max 3 Visible Cards)
        grid_x = 24
        grid_y = 125
        card_w = 140
        card_h = 44
        gap_x = 8
        gap_y = 0
        cols = 3
        visible_rows = 1

        self.card_grid = CardGridContainer(
            grid_x,
            grid_y,
            (card_w + gap_x) * cols,
            card_h,
            cols=cols,
            visible_rows=visible_rows,
            card_w=card_w,
            card_h=card_h,
            gap_x=gap_x,
            gap_y=gap_y,
        )

        self.card_buttons: List[CardButton] = []
        for i, card in enumerate(self.cards):
            cx = grid_x + i * (card_w + gap_x)
            cy = grid_y
            cid = card["id"]

            def make_click(card_id: str):
                return lambda: self._on_card_selected(card_id)

            btn = CardButton(
                cx,
                cy,
                card_w,
                card_h,
                card_data=card,
                on_toggle=make_click(cid),
                theme=NOIR_CARD_THEME,
            )
            self.card_buttons.append(btn)
            self.card_grid.add_child(btn)

        self.root.add_child(self.card_grid)

        self.ui = UIManager(
            self.root,
            virtual_width=settings.VIRTUAL_WIDTH,
            window_width=settings.WINDOW_WIDTH,
            virtual_height=settings.VIRTUAL_HEIGHT,
            window_height=settings.WINDOW_HEIGHT,
            confirm_action="space",
            navigate_actions={
                "move_up": (0, -1),
                "move_down": (0, 1),
                "move_left": (-1, 0),
                "move_right": (1, 0),
            },
        )

        # Auto-highlight / focus the first card to start selecting immediately
        if self.card_buttons:
            self.card_grid.focus_saved_or_first()

        self._update_display()

    def _on_card_selected(self, card_id: str) -> None:
        """Direct trigger callback when a card is clicked/selected."""
        if self.phase_substate != "statement":
            return

        phase = self._get_current_phase()
        max_cards = len(phase.required_cards)

        if card_id not in self.selected_card_ids:
            self.selected_card_ids.append(card_id)

        # Highlight currently active cards
        for btn in self.card_buttons:
            btn.is_threaded = btn.card_data["id"] in self.selected_card_ids

        # Once required amount of cards are selected, immediately evaluate confrontation submission
        if len(self.selected_card_ids) == max_cards:
            self._present_evidence()

    def _present_evidence(self) -> None:
        phase = self._get_current_phase()

        if set(self.selected_card_ids) == set(phase.required_cards):
            self.phase_substate = "success_reaction"
        else:
            self.phase_substate = "fail_reaction"

        self._update_display()

    def _set_npc_dialogue(self, speaker_title: str, text: str) -> None:
        self.speaker_label.set_text(speaker_title.upper())
        self.npc_textbox.raw_pages = [text]
        self.npc_textbox.page_index = 0
        self.npc_textbox.pages = self.npc_textbox._paginate(text)
        self.npc_textbox._load_current_page_typewriter()

    def _update_display(self) -> None:
        phase = self._get_current_phase()

        if self.phase_substate == "statement":
            self._set_npc_dialogue(self.npc_name, phase.npc_statement)
            self.card_grid.enabled = True
            self.card_grid.visible = True
            self.selected_card_ids.clear()
            for btn in self.card_buttons:
                btn.is_threaded = False

        elif self.phase_substate == "success_reaction":
            text = f"{phase.npc_reaction}\n{phase.success_dialogue}"
            self._set_npc_dialogue(f"{self.npc_name} (RINCONADO)", text)
            self.card_grid.enabled = False
            self.card_grid.visible = False

        elif self.phase_substate == "fail_reaction":
            self._set_npc_dialogue(self.npc_name, phase.fail_reactions)
            self.card_grid.enabled = False
            self.card_grid.visible = False

        self._update_hint_text()

    def _update_hint_text(self) -> None:
        if self.phase_substate == "statement":
            phase = self._get_current_phase()
            req = len(phase.required_cards)
            sel = len(self.selected_card_ids)
            hint = phase.guidance_hint or f"Selecciona {req} evidencia(s) [{sel}/{req}]"
            self.hint_label.set_text(hint)
        else:
            self.hint_label.set_text("[ESPACIO / ENTER] Continuar...")

    def _on_typewriter_finished(self) -> None:
        pass

    def _advance_substate(self) -> None:
        if not self.npc_textbox.typewriter.finished:
            self.npc_textbox.typewriter.complete()
            return

        if self.phase_substate == "success_reaction":
            self.current_phase_index += 1
            if self.current_phase_index >= len(self.active_phases):
                pygame.mixer.music.stop()
                self.state_machine.pop()
                if self.on_complete:
                    self.on_complete()
            else:
                self.phase_substate = "statement"
                self._update_display()
                if self.card_buttons:
                    self.card_grid.focus_saved_or_first()

        elif self.phase_substate == "fail_reaction":
            self.phase_substate = "statement"
            self._update_display()
            if self.card_buttons:
                self.card_grid.focus_saved_or_first()

    def update(self, dt: float) -> None:
        self.npc_textbox.update(dt)
        self.ui.update(dt)

    def on_input(self, input_id: str, input_data: Any) -> None:
        if isinstance(input_data, KeyboardData) and not input_data.pressed:
            return

        if self.phase_substate in ("success_reaction", "fail_reaction"):
            if input_id in ("space", "enter", "confirm", "interact"):
                self._advance_substate()
            return

        if input_id == "move_right":
            self.npc_textbox.advance()
        elif input_id == "move_left":
            self.npc_textbox.regress()

        self.ui.on_input(input_id, input_data)

    def render(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        self.ui.render(surface)