"""
P.I. Gallagher: The Missing Art

Custom gale.ui Themes for 1932 Noir aesthetic.
"""

import pygame
from gale.ui.theme import Theme

import settings

# ── 1932 Noir Palette ───────────────────────────────────────────────────────
COLOR_NOIR_BG = pygame.Color(28, 24, 22)
COLOR_NOIR_PANEL = pygame.Color(42, 35, 30)
COLOR_NOIR_PANEL_LIGHT = pygame.Color(58, 48, 40)
COLOR_BRASS = pygame.Color(175, 140, 65)
COLOR_BRASS_LIGHT = pygame.Color(215, 180, 105)
COLOR_PAPER = pygame.Color(232, 222, 198)
COLOR_PAPER_SELECTED = pygame.Color(255, 248, 225)
COLOR_PAPER_THREADED = pygame.Color(248, 220, 220)
COLOR_INK = pygame.Color(28, 24, 22)
COLOR_MUTED = pygame.Color(145, 135, 120)
COLOR_ACCENT_RED = pygame.Color(210, 35, 35)
COLOR_SUCCESS = pygame.Color(60, 140, 60)
COLOR_DANGER = pygame.Color(190, 50, 40)

# ── Diálogo Theme ──────────────────────────────────────────────────────────
NOIR_DIALOGUE_THEME = Theme(
    font=settings.FONTS["small"],
    text_color=pygame.Color(235, 228, 215),
    background_color=COLOR_NOIR_BG,
    border_color=COLOR_BRASS,
    border_width=2,
    accent_color=COLOR_BRASS_LIGHT,
    hover_color=COLOR_NOIR_PANEL_LIGHT,
    focus_color=COLOR_BRASS_LIGHT,
    disabled_color=COLOR_MUTED,
    padding=6,
)

# ── Pizarra de Corcho: Base Board Theme ─────────────────────────────────────
NOIR_CORK_THEME = Theme(
    font=settings.FONTS["small"],
    text_color=COLOR_INK,
    background_color=pygame.Color(148, 112, 78),
    border_color=pygame.Color(55, 35, 22),
    border_width=4,
    accent_color=COLOR_ACCENT_RED,
    hover_color=COLOR_PAPER_SELECTED,
    focus_color=COLOR_BRASS,
    padding=4,
)

# ── Tarjeta de Corcho Theme ────────────────────────────────────────────────
NOIR_CARD_THEME = Theme(
    font=settings.FONTS["small"],
    text_color=COLOR_INK,
    background_color=COLOR_PAPER,
    border_color=pygame.Color(140, 130, 115),
    border_width=1,
    accent_color=COLOR_ACCENT_RED,
    hover_color=COLOR_PAPER_SELECTED,
    focus_color=COLOR_BRASS_LIGHT,
    padding=4,
)

NOIR_CARD_THREADED_THEME = Theme(
    font=settings.FONTS["small"],
    text_color=COLOR_INK,
    background_color=COLOR_PAPER_THREADED,
    border_color=COLOR_ACCENT_RED,
    border_width=2,
    accent_color=COLOR_ACCENT_RED,
    hover_color=COLOR_PAPER_SELECTED,
    focus_color=COLOR_BRASS_LIGHT,
    padding=4,
)

# ── Sidebar y Dudas Abiertas Theme ──────────────────────────────────────────
NOIR_SIDEBAR_THEME = Theme(
    font=settings.FONTS["small"],
    text_color=pygame.Color(220, 210, 195),
    background_color=COLOR_NOIR_PANEL,
    border_color=COLOR_BRASS,
    border_width=1,
    accent_color=COLOR_BRASS_LIGHT,
    padding=6,
)

# ── Botones de Acción Theme ────────────────────────────────────────────────
NOIR_BUTTON_THEME = Theme(
    font=settings.FONTS["small"],
    text_color=pygame.Color(235, 225, 210),
    background_color=COLOR_NOIR_PANEL,
    border_color=COLOR_BRASS,
    border_width=1,
    hover_color=COLOR_NOIR_PANEL_LIGHT,
    focus_color=COLOR_BRASS_LIGHT,
    padding=4,
)

# ── HUD / Prompts Theme ────────────────────────────────────────────────────
NOIR_PROMPT_THEME = Theme(
    font=settings.FONTS["small"],
    text_color=pygame.Color(235, 225, 205),
    background_color=COLOR_NOIR_BG,
    border_color=COLOR_BRASS,
    border_width=1,
    padding=4,
)

# ── Menú de Pausa Theme ────────────────────────────────────────────────────
NOIR_MENU_THEME = Theme(
    font=settings.FONTS["small"],
    text_color=pygame.Color(235, 230, 215),
    background_color=COLOR_NOIR_BG,
    border_color=COLOR_BRASS,
    border_width=2,
    hover_color=COLOR_NOIR_PANEL_LIGHT,
    focus_color=COLOR_BRASS_LIGHT,
    accent_color=COLOR_BRASS_LIGHT,
    padding=6,
)

