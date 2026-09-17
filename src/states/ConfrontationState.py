from typing import Any, Callable, Dict, List, Optional, Tuple

import pygame

from gale.input_handler import KeyboardData, MouseClickData, MouseMotionData
from gale.state import BaseState
from gale.text import render_text
from gale.ui import Button, Container, Label, Panel, TextBox, Theme, UIManager, Window
from gale.ui.widget import Direction

import settings
from src.data.confrontation_data import MORALES_CONFRONTATION, SOFIA_CONFRONTATION, ConfrontationPhase
from src.data.cards import CARDS
from src.states.CorkboardState import CardButton, ActionBarContainer
from src.story.StoryManager import StoryManager
from src.ui.theme import NOIR_DIALOGUE_THEME, NOIR_CARD_THEME, NOIR_SIDEBAR_THEME, COLOR_ACCENT_RED, COLOR_SUCCESS


class ConfrontationState(BaseState):
    def enter(
        self,
        confrontation_id: str,
        on_complete: Optional[Callable[[], None]] = None,
    ) -> None:
        self.story = StoryManager.get_instance()
        self.on_complete = on_complete
        
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
        
        # State machine for the current phase: "statement" -> ("fail_reaction" -> "statement") or "success_reaction"
        self.phase_substate = "statement"  
        
        self._build_ui()
        
    def _get_current_phase(self) -> ConfrontationPhase:
        return self.active_phases[self.current_phase_index]

    def _build_ui(self) -> None:
        # Load player's cards
        self.cards = self.story.get_available_cards_for_corkboard()
        self.cards.sort(key=lambda c: c["id"])
        
        self.root = Container(0, 0, settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT)
        
        # Upper Dialog Window for NPC
        self.npc_win_x = 16
        self.npc_win_y = 16
        self.npc_win_w = settings.VIRTUAL_WIDTH - 32
        self.npc_win_h = 72
        
        self.npc_window = Window(
            self.npc_win_x, self.npc_win_y, self.npc_win_w, self.npc_win_h,
            title=self.npc_name, closable=False, theme=NOIR_DIALOGUE_THEME
        )
        
        self.npc_textbox = TextBox(
            self.npc_win_x + 10, self.npc_win_y + 24, self.npc_win_w - 20, 44,
            text="", lines_per_page=3, theme=NOIR_DIALOGUE_THEME
        )
        self.npc_window.add_child(self.npc_textbox)
        self.root.add_child(self.npc_window)
        
        # Lower Area for Cards (Hand)
        hand_y = 130
        hand_h = 100
        
        # Label to indicate guidance or monologue
        self.monologue_label = Label(
            16, hand_y - 20, "",
            font=settings.FONTS["small"],
            color=pygame.Color(160, 150, 135),
            theme=NOIR_DIALOGUE_THEME
        )
        self.root.add_child(self.monologue_label)
        
        # We will use ActionBarContainer to hold cards side by side
        # A simple horizontal scroll or just fit them if there are not too many.
        # Since we use virtual width 480, cards are 152w. We might need pagination if many.
        # But for now let's just lay them out side by side.
        self.card_container = ActionBarContainer(16, hand_y, settings.VIRTUAL_WIDTH - 32, 60)
        
        card_w = 120
        card_h = 36
        gap_x = 4
        
        self.card_buttons = []
        for i, card in enumerate(self.cards):
            def make_toggle(cid):
                return lambda: self._toggle_card(cid)
            
            btn = CardButton(
                16 + i * (card_w + gap_x),
                hand_y,
                card_w,
                card_h,
                card_data=card,
                on_toggle=make_toggle(card["id"]),
                theme=NOIR_CARD_THEME
            )
            self.card_buttons.append(btn)
            self.card_container.add_child(btn)
            
        self.root.add_child(self.card_container)
        
        # Present button
        self.present_btn = Button(
            settings.VIRTUAL_WIDTH // 2 - 50,
            hand_y + 50,
            100, 24,
            "Presentar [ENTER]",
            on_click=self._present_evidence,
            theme=NOIR_SIDEBAR_THEME
        )
        self.root.add_child(self.present_btn)
        
        self.ui = UIManager(
            self.root,
            virtual_width=settings.VIRTUAL_WIDTH,
            window_width=settings.WINDOW_WIDTH,
            virtual_height=settings.VIRTUAL_HEIGHT,
            window_height=settings.WINDOW_HEIGHT,
            confirm_action="enter",
            navigate_actions={
                "move_left": (-1, 0),
                "move_right": (1, 0),
                "rotate_left": (-1, 0),
                "details": (1, 0),
                "move_up": (0, -1),
                "move_down": (0, 1)
            }
        )
        
        self._update_display()
        if self.card_buttons:
            # Focus root so all children are reachable, then focus cards
            self.root._focus_first()
            self.card_container._focus_first()

    def _toggle_card(self, cid: str) -> None:
        if cid in self.selected_card_ids:
            self.selected_card_ids.remove(cid)
        else:
            # Sofia's double cobro phase requires 2 cards. Most require 1.
            phase = self._get_current_phase()
            max_cards = len(phase.required_cards)
            if len(self.selected_card_ids) < max_cards:
                self.selected_card_ids.append(cid)
            else:
                if max_cards == 1:
                    self.selected_card_ids = [cid]
        self._sync_card_buttons()

    def _sync_card_buttons(self) -> None:
        for btn in self.card_buttons:
            btn.is_threaded = btn.card_data["id"] in self.selected_card_ids

    def _set_npc_text(self, new_text: str) -> None:
        self.npc_textbox._pages = self.npc_textbox._paginate(new_text)
        self.npc_textbox.page_index = 0

    def _set_npc_title(self, new_title: str) -> None:
        # Window's title Label is the second child (index 1) after Panel (index 0)
        if len(self.npc_window.children) > 1 and isinstance(self.npc_window.children[1], Label):
            self.npc_window.children[1].set_text(new_title)

    def _update_display(self) -> None:
        phase = self._get_current_phase()
        
        if self.phase_substate == "statement":
            self._set_npc_title(self.npc_name)
            self._set_npc_text(phase.npc_statement)
            self.monologue_label.set_text(phase.guidance_hint or "Selecciona la evidencia correcta...")
            self.card_container.enabled = True
            self.card_container.visible = True
            self.present_btn.enabled = True
            self.present_btn.visible = True
            self.selected_card_ids.clear()
            self._sync_card_buttons()
            
        elif self.phase_substate == "success_reaction":
            self._set_npc_title(self.npc_name + " (Rinconado)")
            self._set_npc_text(phase.npc_reaction + "\n" + phase.success_dialogue)
            self.monologue_label.set_text("[ESPACIO] para continuar...")
            self.card_container.enabled = False
            self.card_container.visible = False
            self.present_btn.enabled = False
            self.present_btn.visible = False
            
        elif self.phase_substate == "fail_reaction":
            self._set_npc_title(self.npc_name)
            self._set_npc_text(phase.fail_reactions)
            self.monologue_label.set_text("[ESPACIO] para reintentar...")
            self.card_container.enabled = False
            self.card_container.visible = False
            self.present_btn.enabled = False
            self.present_btn.visible = False

    def _present_evidence(self) -> None:
        if not self.selected_card_ids:
            return
            
        phase = self._get_current_phase()
        
        # Check if selected cards match required cards exactly
        if set(self.selected_card_ids) == set(phase.required_cards):
            # Success
            self.phase_substate = "success_reaction"
            # Optional: Add Tween or sound effect here
        else:
            # Fail
            self.phase_substate = "fail_reaction"
            
        self._update_display()

    def _advance_substate(self) -> None:
        if self.phase_substate == "success_reaction":
            # Go to next phase
            self.current_phase_index += 1
            if self.current_phase_index >= len(self.active_phases):
                # End of confrontation
                self.state_machine.pop()
                if self.on_complete:
                    self.on_complete()
            else:
                self.phase_substate = "statement"
                self._update_display()
                if self.card_buttons:
                    self.root._focus_first()
                    self.card_container._focus_first()
                    
        elif self.phase_substate == "fail_reaction":
            # Retry
            self.phase_substate = "statement"
            self._update_display()
            if self.card_buttons:
                self.root._focus_first()
                self.card_container._focus_first()

    def update(self, dt: float) -> None:
        self.ui.update(dt)

    def on_input(self, input_id: str, input_data: Any) -> None:
        if isinstance(input_data, KeyboardData) and not input_data.pressed:
            return
            
        if self.phase_substate in ("success_reaction", "fail_reaction"):
            if input_id in ("interact", "enter", "confirm"):
                self._advance_substate()
            return

        # Treat space (interact) identically to enter for UI confirmation
        ui_input_id = "enter" if input_id in ("interact", "confirm") else input_id
        self.ui.on_input(ui_input_id, input_data)

    def render(self, surface: pygame.Surface) -> None:
        # Dark overlay
        overlay = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))
        
        self.ui.render(surface)

