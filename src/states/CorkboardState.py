"""
P.I. Gallagher: The Missing Art

CorkboardState — Central investigative corkboard built entirely on gale.ui.
Features 2D grid navigation across clue cards, seamless focus transition to bottom
action buttons and motion support, a dedicated full-screen Card Details
overlay, and modal dialogs for deductions and Lauren's hints.
"""

from typing import Any, Dict, List, Optional

import pygame

from gale.input_handler import InputData, KeyboardData
from gale.state import BaseState
from gale.ui import Label, Panel, TextBox, Theme, UIManager, Window

import settings
from src.data.cards import LAUREN_HINTS, OPEN_QUESTIONS
from src.story.StoryManager import StoryManager
from src.ui.theme import (
    COLOR_ACCENT_RED,
    COLOR_BRASS,
    COLOR_BRASS_LIGHT,
    COLOR_INK,
    COLOR_MUTED,
    COLOR_PAPER,
    COLOR_PAPER_SELECTED,
    COLOR_PAPER_THREADED,
    COLOR_SUCCESS,
    NOIR_CARD_THEME,
    NOIR_CORK_THEME,
    NOIR_DIALOGUE_THEME,
    NOIR_SIDEBAR_THEME,
)

from src.ui import CardButton, CardGridContainer, ModalOverlay

class CorkboardState(BaseState):
    def enter(self) -> None:
        music_path = settings.BASE_DIR / "assets" / "sounds" / "investigate.mp3"
        if music_path.exists():
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(loops=-1)

        self.story = StoryManager.get_instance()
        self.visit = self.story.get_current_corcho_visit()

        self.threaded_ids: List[str] = []

        # Modal / details screen state
        self.modal_overlay: Optional[ModalOverlay] = None
        self.modal_active: bool = False
        self.details_active: bool = False
        self.details_card: Optional[Dict[str, Any]] = None
        self.details_thread_lbl: Optional[Label] = None

        self._build_ui()

    def _build_ui(self) -> None:
        """Construct the entire corkboard interface using gale.ui widgets."""
        self.cards = self.story.get_available_cards_for_corkboard()
        self.cards.sort(key=lambda c: c["id"])

        # 1. Main Corkboard Background Panel
        self.board_panel = Panel(
            6, 6, settings.VIRTUAL_WIDTH - 12, settings.VIRTUAL_HEIGHT - 12, theme=NOIR_CORK_THEME
        )

        # 2. Card Grid Container (2 columns of cards)
        self.card_buttons: List[CardButton] = []
        grid_x = 12
        grid_y = 45
        card_w = 152
        card_h = 50
        gap_x = 8
        gap_y = 4
        cols = 2

        self.card_grid = CardGridContainer(
            grid_x, grid_y, (card_w + gap_x) * cols, (card_h + gap_y) * 4, cols=cols
        )

        # Add background panel to grid FIRST so it renders behind card buttons
        self.card_grid.add_child(self.board_panel)

        for i, card in enumerate(self.cards):
            row = i // cols
            col = i % cols
            cx = grid_x + col * (card_w + gap_x)
            cy = grid_y + row * (card_h + gap_y)

            cid = card["id"]

            def make_toggle(card_id: str):
                return lambda: self._toggle_thread(card_id)

            btn = CardButton(
                cx,
                cy,
                card_w,
                card_h,
                card_data=card,
                on_toggle=make_toggle(cid),
                theme=NOIR_CARD_THEME,
            )
            btn.is_threaded = cid in self.threaded_ids
            self.card_buttons.append(btn)
            self.card_grid.add_child(btn)

        bar_x = 12
        bar_y = 229
        bar_w = 456
        bar_h = 29

        # Header Bar
        header_text = f"PIZARRA DE INVESTIGACIÓN"
        self.header_label = Label(
            16,
            10,
            header_text,
            font=settings.FONTS["medium"],
            color=pygame.Color(45, 30, 18),
            theme=NOIR_CORK_THEME,
        )
        self.card_grid.add_child(self.header_label)

        counter_text = f"Pistas: {len(self.cards)}  |  Hilos: {len(self.threaded_ids)}"
        self.counter_label = Label(
            344,
            12,
            counter_text,
            font=settings.FONTS["small"],
            color=pygame.Color(65, 45, 28),
            theme=NOIR_CORK_THEME,
        )
        self.card_grid.add_child(self.counter_label)

        # Sidebar: Open Questions Window (Dudas Abiertas)
        sidebar_x = 328
        sidebar_y = 34
        sidebar_w = 140
        sidebar_h = 190

        self.sidebar_win = Window(
            sidebar_x,
            sidebar_y,
            sidebar_w,
            sidebar_h,
            title="DUDAS",
            closable=False,
            theme=NOIR_SIDEBAR_THEME,
        )

        questions = OPEN_QUESTIONS.get(self.visit, [])
        q_text = "\n\n".join(f"• {q}" for q in questions)
        theme_q = Theme(
            font=settings.FONTS["small"],
            text_color=pygame.Color(220, 210, 195),
            background_color=NOIR_SIDEBAR_THEME.background_color,
            border_color=NOIR_SIDEBAR_THEME.background_color,
            border_width=0,
            padding=2,
        )
        self.sidebar_tb = TextBox(
            sidebar_x + 6,
            sidebar_y + 24,
            sidebar_w - 12,
            sidebar_h - 30,
            text=q_text,
            lines_per_page=8,
            theme=theme_q,
        )
        self.sidebar_win.add_child(self.sidebar_tb)
        self.card_grid.add_child(self.sidebar_win)

        # Bottom Panel
        self.action_panel = Panel(bar_x, bar_y, bar_w, bar_h, theme=NOIR_SIDEBAR_THEME)
        self.card_grid.add_child(self.action_panel)

        # Help hint line under the buttons
        self.bar_hint_label = Label(
            20,
            bar_y + 6,
            "Flechitas: Moverse  |  ESPACIO: Hilo  |  ENTER: Deducir  |  H: Ayuda  |  ESC: Salir",
            font=settings.FONTS["small"],
            color=COLOR_MUTED,
            theme=NOIR_SIDEBAR_THEME,
        )
        self.card_grid.add_child(self.bar_hint_label)

        # Initial focus on first card
        if self.card_buttons:
            self.card_grid.focus_saved_or_first()

        # Gale UIManager initialized directly with CardGridContainer
        self.ui = UIManager(
            self.card_grid,
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

    def _get_focused_card(self) -> Optional[Dict[str, Any]]:
        """Return the card data of currently focused or hovered CardButton."""
        btn = self.card_grid.get_focused_card_button()
        if btn is not None:
            return btn.card_data
        if self.card_buttons:
            return self.card_buttons[0].card_data
        return None

    def _open_focused_card_details(self) -> None:
        """Open the Card Details Screen for the currently focused card."""
        card = self._get_focused_card()
        if card is not None:
            self._show_card_details(card)

    def _toggle_focused_card_thread(self) -> None:
        """Toggle thread connection for the currently focused card."""
        card = self._get_focused_card()
        if card is not None:
            self._toggle_thread(card["id"])

    # ── Pantalla de Detalles de Tarjeta (Card Details Screen) ────────────────

    def _show_card_details(self, card: Dict[str, Any]) -> None:
        """
        Display the full, unclipped Card Details Screen wrapped in a ModalOverlay.
        Shows ID, Title, Type, Origin, Keywords, and full narrative Description.
        """
        if self.modal_active:
            self._close_modal()

        self.details_card = card
        win_w = 390
        win_h = 210
        win_x = (settings.VIRTUAL_WIDTH - win_w) // 2
        win_y = (settings.VIRTUAL_HEIGHT - win_h) // 2

        cid = card["id"]
        title_str = f"EXPEDIENTE [{cid}]: {card['titulo']}"

        details_window = Window(
            win_x,
            win_y,
            win_w,
            win_h,
            title=title_str,
            closable=False,
            theme=NOIR_DIALOGUE_THEME,
        )

        # Row 1: Tipo & Origen
        meta_str = f"TIPO: {card['tipo'].upper()}   |   ORIGEN: {card.get('origen', 'Investigación')}"
        meta_lbl = Label(
            win_x + 12,
            win_y + 24,
            meta_str,
            font=settings.FONTS["medium"],
            color=COLOR_BRASS_LIGHT,
            theme=NOIR_DIALOGUE_THEME,
        )
        details_window.add_child(meta_lbl)

        # Row 2: Palabras Clave
        kw_str = f"PALABRAS CLAVE: {', '.join(card['claves'])}"
        kw_lbl = Label(
            win_x + 12,
            win_y + 40,
            kw_str,
            font=settings.FONTS["medium"],
            color=COLOR_ACCENT_RED,
            theme=NOIR_DIALOGUE_THEME,
        )
        details_window.add_child(kw_lbl)

        # Row 3: Full Description (Word-wrapped TextBox inside Panel)
        desc_theme = Theme(
            font=settings.FONTS["medium"],
            text_color=pygame.Color(235, 228, 215),
            background_color=NOIR_SIDEBAR_THEME.background_color,
            border_color=NOIR_SIDEBAR_THEME.background_color,
            border_width=0,
            padding=4,
        )
        desc_panel = Panel(
            win_x + 10, win_y + 56, win_w - 20, 96, theme=NOIR_SIDEBAR_THEME
        )
        details_window.add_child(desc_panel)

        desc_tb = TextBox(
            win_x + 14,
            win_y + 60,
            win_w - 28,
            88,
            text=card["descripcion"],
            lines_per_page=6,
            theme=desc_theme,
        )
        details_window.add_child(desc_tb)

        # Row 4: Static Action Prompt Labels (Non-selectable)
        is_threaded = cid in self.threaded_ids
        lbl_thread_text = (
            "Quitar del Hilo Rojo [ESPACIO]" if is_threaded else "Conectar con Hilo Rojo [ESPACIO]"
        )

        self.details_thread_lbl = Label(
            win_x + 12,
            win_y + 172,
            lbl_thread_text,
            font=settings.FONTS["medium"],
            color=COLOR_BRASS_LIGHT,
            theme=NOIR_DIALOGUE_THEME,
        )
        lbl_close = Label(
            win_x + win_w - 120,
            win_y + 172,
            "Cerrar [D / ESC]",
            font=settings.FONTS["medium"],
            color=COLOR_BRASS_LIGHT,
            theme=NOIR_DIALOGUE_THEME,
        )

        details_window.add_child(self.details_thread_lbl)
        details_window.add_child(lbl_close)

        # Wrap in ModalOverlay for full input isolation
        self.modal_overlay = ModalOverlay(
            settings.VIRTUAL_WIDTH,
            settings.VIRTUAL_HEIGHT,
            details_window,
            on_dismiss=self._close_details,
        )
        self.details_active = True

    def _update_details_thread_button(self) -> None:
        if self.details_card and self.details_thread_lbl:
            cid = self.details_card["id"]
            is_threaded = cid in self.threaded_ids
            lbl_text = (
                "Quitar del Hilo Rojo [ESPACIO]" if is_threaded else "Conectar con Hilo Rojo [ESPACIO]"
            )
            self.details_thread_lbl.set_text(lbl_text)

    def _close_details(self) -> None:
        """Close the Card Details Screen and restore focus to the card grid."""
        if self.details_active:
            self.modal_overlay = None
            self.details_card = None
            self.details_thread_lbl = None
            self.details_active = False

            # Restore focus to card grid
            self.card_grid.focus_saved_or_first()

    # ── Modal de Deducciones y Consejos ──────────────────────────────────────

    def _show_modal(self, title: str, text: str, is_success: bool = False) -> None:
        """Display a full narrative message in an isolated modal dialog."""
        if self.details_active:
            self._close_details()

        modal_w = 380
        modal_h = 150
        modal_x = (settings.VIRTUAL_WIDTH - modal_w) // 2
        modal_y = (settings.VIRTUAL_HEIGHT - modal_h) // 2

        modal_window = Window(
            modal_x,
            modal_y,
            modal_w,
            modal_h,
            title=title,
            closable=False,
            theme=NOIR_DIALOGUE_THEME,
        )

        theme_text = Theme(
            font=settings.FONTS["medium"],
            text_color=COLOR_SUCCESS if is_success else pygame.Color(235, 228, 215),
            background_color=NOIR_DIALOGUE_THEME.background_color,
            border_color=NOIR_DIALOGUE_THEME.background_color,
            border_width=0,
            padding=2,
        )

        modal_textbox = TextBox(
            modal_x + 10,
            modal_y + 24,
            modal_w - 20,
            88,
            text=text,
            lines_per_page=6,
            on_close=self._close_modal,
            theme=theme_text,
        )
        modal_window.add_child(modal_textbox)

        # Static Action Prompt Label (Non-selectable)
        lbl_dismiss = Label(
            modal_x + modal_w // 2 - 50,
            modal_y + modal_h - 22,
            "Aceptar [ENTER]",
            font=settings.FONTS["medium"],
            color=COLOR_BRASS_LIGHT,
            theme=NOIR_DIALOGUE_THEME,
        )
        modal_window.add_child(lbl_dismiss)

        # Wrap in ModalOverlay for full input isolation
        self.modal_overlay = ModalOverlay(
            settings.VIRTUAL_WIDTH,
            settings.VIRTUAL_HEIGHT,
            modal_window,
            on_dismiss=self._close_modal,
        )
        self.modal_active = True

    def _close_modal(self) -> None:
        if self.modal_active:
            self.modal_overlay = None
            self.modal_active = False

            # Restore focus to card grid
            self.card_grid.focus_saved_or_first()

    # ── Mecánica de Hilo Rojo y Deducciones ──────────────────────────────────

    def _toggle_thread(self, card_id: str) -> None:
        """Toggle whether a card is pinned to the red thread."""
        if card_id in self.threaded_ids:
            self.threaded_ids.remove(card_id)
        else:
            self.threaded_ids.append(card_id)

        # Sync visual state on card buttons
        for btn in self.card_buttons:
            btn.is_threaded = btn.card_data["id"] in self.threaded_ids

        counter_text = f"Pistas: {len(self.cards)}  |  Hilos: {len(self.threaded_ids)}"
        self.counter_label.set_text(counter_text)

    def _attempt_deduction(self) -> None:
        """Validate current red thread connection against deduction rules."""
        if self.modal_active:
            self._close_modal()
            return
        if self.details_active:
            self._close_details()

        if len(self.threaded_ids) < 2:
            self._show_modal(
                "PIZARRA DE CORCHO",
                "Debes seleccionar al menos dos tarjetas con el hilo rojo para intentar formular una deducción.",
            )
            return

        is_valid, ded, msg = self.story.validate_connection(self.threaded_ids)

        if is_valid:
            self.threaded_ids.clear()
            self.visit = self.story.get_current_corcho_visit()
            self._build_ui()
            full_msg = (
                f"{ded['titulo']}\n\n"
                f"{ded['texto']}\n\n"
                f"Efecto: {ded['unlock_text']}"
            )
            self._show_modal(f"¡DEDUCCIÓN RESUELTA: {ded['id']}!", full_msg, is_success=True)
        else:
            full_msg = (
                f"'{msg}'\n\n"
                f"Las pistas unidas no forman una relación lógica de causa y efecto. "
                f"Revisa las palabras clave e inténtalo de nuevo."
            )
            self._show_modal("GALLAGHER — MONÓLOGO INTERIOR", full_msg, is_success=False)

    def _show_hint(self) -> None:
        if self.modal_active:
            self._close_modal()
            return
        if self.details_active:
            self._close_details()

        hint = LAUREN_HINTS.get(self.visit, "Lauren no tiene más pistas por ahora.")
        self._show_modal("CONSEJO DE LAUREN", f"Lauren se acerca a la pizarra:\n\n{hint}")

    def _exit_board(self) -> None:
        if self.modal_active:
            self._close_modal()
            return
        if self.details_active:
            self._close_details()
            return
        pygame.mixer.music.stop()
        self.state_machine.pop()

    def update(self, dt: float) -> None:
        self.ui.update(dt)
        if self.modal_overlay is not None:
            self.modal_overlay.update(dt)

    def on_input(self, input_id: str, input_data: InputData) -> None:
        # Filter key releases only for KeyboardData so mouse click and motion are preserved
        if isinstance(input_data, KeyboardData) and not input_data.pressed:
            return

        # 1. When a modal or card details overlay is active:
        if self.modal_overlay is not None:
            if input_id in ("quit", "details") and self.details_active:
                self._close_details()
                return

            if input_id in ("quit", "space", "enter") and self.modal_active:
                self._close_modal()
                return

            if input_id == "space" and self.details_active and self.details_card:
                self._toggle_thread(self.details_card["id"])
                self._update_details_thread_button()
                return

            if input_id in ("space", "enter"):
                self.modal_overlay.on_confirm()
            elif input_id in self.ui.navigate_actions:
                self.modal_overlay.on_navigate(self.ui.navigate_actions[input_id])
            return

        # 2. Main corkboard screen shortcuts:
        if input_id == "quit":
            self._exit_board()
            return

        if input_id == "details" or (
            isinstance(input_data, KeyboardData) and input_data.key in (pygame.K_d, pygame.K_i)
        ):
            self._open_focused_card_details()
            return

        if input_id == "hint" or (
            isinstance(input_data, KeyboardData) and input_data.key == pygame.K_h
        ):
            self._show_hint()
            return

        # Handle ENTER / confirm:
        if input_id == "enter":
            self._attempt_deduction()
            return

        # Handle SPACE / interact:
        if input_id == "space":
            card_btn = self.card_grid.get_focused_card_button()
            if card_btn:
                self._toggle_thread(card_btn.card_data["id"])
            return

        self.ui.on_input(input_id, input_data)

    def render(self, surface: pygame.Surface) -> None:
        # Background outer wood frame
        surface.fill(pygame.Color(55, 35, 22))

        # Render main gale.ui widget tree
        self.ui.render(surface)

        # Draw Red Thread (hilo rojo) connecting pinned cards
        if len(self.threaded_ids) >= 2 and not self.details_active:
            points = []
            for cid in self.threaded_ids:
                for btn in self.card_buttons:
                    if btn.card_data["id"] == cid:
                        points.append(btn.pin_pos)
                        break
            if len(points) >= 2:
                pygame.draw.lines(surface, COLOR_ACCENT_RED, False, points, 2)

        # Render active modal / details overlay
        if self.modal_overlay is not None:
            self.modal_overlay.render(surface)