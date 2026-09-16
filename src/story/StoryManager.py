"""
P.I. Gallagher: The Missing Art

StoryManager — Centralized, data-driven narrative progression service.
Manages story acts, levels, clues inventory, validated deductions, narrative flags,
floating notification banners, and semantic gating queries.
"""

from typing import Any, Dict, List, Optional, Set, Tuple

from src.data.cards import CARDS, DEDUCTIONS, FAILURE_MONOLOGUES


class StoryManager:
    _instance: Optional["StoryManager"] = None

    def __init__(self) -> None:
        self.reset()

    @classmethod
    def get_instance(cls) -> "StoryManager":
        if cls._instance is None:
            cls._instance = StoryManager()
        return cls._instance

    def reset(self) -> None:
        """Reset story progression to Level 0 (Oficina - inicio del caso)."""
        self.act: int = 1
        self.level: int = 0

        # Tarjetas actualmente en el inventario del detective
        self.collected_cards: Set[str] = set()

        # Deducciones y sospechas resueltas
        self.validated_deductions: Set[str] = set()
        self.validated_suspicions: Set[str] = set()

        # Flags narrativos
        self.flags: Dict[str, bool] = {
            "recorte_encontrado": False,
            "doble_cobro_deducido": False,
            "traicion_deducida": False,
            "sofia_office_talked": False,
            "c01_inspected": False,
            "archive_completed": False,
            "corcho1_done": False,
            "morales_confronted": False,
            "corcho2_done": False,
            "sofia_club_talked": False,
            "stealth_completed": False,
            "corcho3_done": False,
            "safecracker_completed": False,
            "corcho_final_done": False,
        }

        # Cola de notificaciones en pantalla
        self.notifications: List[Dict[str, Any]] = []

    # ── Gestión de Tarjetas y Pistas ─────────────────────────────────────────

    def add_card(self, card_id: str) -> bool:
        """Add a clue card to the inventory and queue an on-screen banner."""
        if card_id not in CARDS:
            return False

        if card_id not in self.collected_cards:
            self.collected_cards.add(card_id)
            card = CARDS[card_id]
            tipo_label = "Pista" if card["tipo"] == "pista" else card["tipo"].capitalize()
            self.push_notification(f"Nueva {tipo_label}: [{card_id}] {card['titulo']}")
            return True
        return False

    def has_card(self, card_id: str) -> bool:
        return card_id in self.collected_cards

    def get_available_cards_for_corkboard(self) -> List[Dict[str, Any]]:
        """Return full card dicts for all collected cards."""
        return [CARDS[cid] for cid in self.collected_cards if cid in CARDS]

    # ── Notificaciones en Pantalla ──────────────────────────────────────────

    def push_notification(self, text: str, duration: float = 3.5) -> None:
        self.notifications.append({"text": text, "timer": duration, "max": duration})

    def update_notifications(self, dt: float) -> None:
        remaining = []
        for notif in self.notifications:
            notif["timer"] -= dt
            if notif["timer"] > 0:
                remaining.append(notif)
        self.notifications = remaining

    # ── Consultas Semánticas de Acceso a Zonas ──────────────────────────────

    def can_access_zone(self, zone_id: str) -> Tuple[bool, str]:
        """
        Check if Gallagher can enter a specific zone.
        Returns (is_allowed, locked_monologue_reason).
        """
        zone = zone_id.lower()

        if zone in ("office", "city"):
            return True, ""

        if zone == "museum":
            if self.level >= 1:
                return True, ""
            return False, "Primero debo hablar con la señorita Del Roscio en mi oficina."

        if zone == "police_station":
            if self.level >= 1:
                return True, ""
            return False, "Aún no tengo motivos para pasar por la comisaría central."

        if zone == "alley":
            if self.flags["corcho1_done"] or "D01" in self.validated_deductions:
                return True, ""
            return (
                False,
                "No tengo nada que buscar en ese callejón todavía. Primero debo analizar "
                "las pistas en la pizarra de corcho de mi oficina.",
            )

        if zone == "nightclub":
            if self.flags["corcho2_done"] or "D02" in self.validated_deductions:
                return True, ""
            return (
                False,
                "El Club Velvet es un antro exclusivo de Cornelius Blackwood. "
                "La puerta trasera y la mirilla están cerradas. Necesito una pista para entrar.",
            )

        return True, ""

    # ── Consultas Semánticas de Minijuegos ───────────────────────────────────

    def can_access_minigame(self, minigame_id: str) -> Tuple[bool, str]:
        """
        Check if a minigame trigger is accessible.
        Returns (is_allowed, locked_monologue_reason).
        """
        mg = minigame_id.lower()

        if mg == "archive":
            if self.level >= 1:
                return True, ""
            return False, "El archivo está cerrado al público en este momento."

        if mg == "stealth":
            if self.flags["sofia_club_talked"]:
                return True, ""
            return (
                False,
                "La puerta a las oficinas traseras está custodiada. Debo reunirme con Sofia "
                "en el reservado del club antes de adentrarme.",
            )

        if mg == "safecracker":
            if self.flags["corcho3_done"] or "D03" in self.validated_deductions:
                return True, ""
            return (
                False,
                "La pesada puerta acorazada de la bóveda está cerrada con llave maestra. "
                "Debo consultar los planos y la llave en el corcho antes de intentar forzarla.",
            )

        return True, ""

    # ── Visitas a la Pizarra de Corcho ───────────────────────────────────────

    def get_current_corcho_visit(self) -> int:
        """Determine which Corkboard visit stage the player is currently on."""
        if not self.flags["corcho1_done"]:
            return 1
        elif not self.flags["corcho2_done"]:
            return 2
        elif not self.flags["corcho3_done"]:
            return 3
        else:
            return 4

    def validate_connection(self, card_ids: List[str]) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Attempt to validate a deduction connection with the selected card IDs.
        Returns (is_valid, deduction_dict_or_none, feedback_message).
        """
        selected_set = set(card_ids)

        for ded_id, ded in DEDUCTIONS.items():
            if ded["required_cards"] == selected_set:
                if ded["tipo"] == "ruido":
                    return False, None, ded["unlock_text"]

                # Deducción válida
                if ded["tipo"] == "deduccion":
                    self.validated_deductions.add(ded_id)
                elif ded["tipo"] == "sospecha":
                    self.validated_suspicions.add(ded_id)

                # Activar flags narrativos si aplica
                if "flag" in ded:
                    self.flags[ded["flag"]] = True

                # Procesar hitos de visita del corcho
                if ded_id == "D01":
                    self.flags["corcho1_done"] = True
                    self.level = max(self.level, 2)
                    self.act = 2
                elif ded_id == "D02":
                    self.flags["corcho2_done"] = True
                    self.level = max(self.level, 3)
                    self.act = 3
                elif ded_id == "D03":
                    self.flags["corcho3_done"] = True
                    self.level = max(self.level, 5)
                elif ded_id in ("D04", "D05"):
                    self.flags["corcho_final_done"] = True
                    self.level = max(self.level, 7)
                    self.act = 5

                self.push_notification(ded["unlock_text"])
                return True, ded, ded["texto"]

        # Combinación no válida
        import random
        monologue = random.choice(FAILURE_MONOLOGUES)
        return False, None, monologue

