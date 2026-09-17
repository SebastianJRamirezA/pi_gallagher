"""
P.I. Gallagher: The Missing Art

World — Top-down game world managing regions, camera, player movement,
conditional triggers, dynamic NPCs, and narrative progression via StoryManager.
"""

import pathlib
from typing import Any, Dict, List, Optional, Tuple

import pygame
from gale.camera import Camera
from gale.state import StateStack
from gale.text import render_text

from gale.ui import Label, Panel
import settings
from src.data.dialogues import DIALOGUES
from src.entity import NPC, Player
from src.states.ConfrontationState import ConfrontationState
from src.states.CorkboardState import CorkboardState
from src.states.DialogueState import DialogueState
from src.states.minigames import PoliceArchiveState, SafeCrackerState, StealthMinigameState
from src.story.StoryManager import StoryManager
from src.ui.theme import NOIR_PROMPT_THEME
from src.world.Region import Region
from src.world.Trigger import Trigger


class World:
    DOOR_TARGETS = ("office", "museum", "nightclub", "police_station", "alley")
    CITY_DOOR_INDEX = {target: index for index, target in enumerate(DOOR_TARGETS) if target}

    def __init__(self, stack: StateStack) -> None:
        self.stack = stack
        self.story = StoryManager.get_instance()

        map_dir = pathlib.Path(settings.BASE_DIR) / "assets" / "tilemaps"
        self.regions: Dict[str, Region] = {
            "city": Region("city", map_dir / "city.json"),
            "museum": Region("museum", map_dir / "museum.json"),
            "nightclub": Region("nightclub", map_dir / "nightclub.json"),
            "office": Region("office", map_dir / "office.json"),
            "police_station": Region("police_station", map_dir / "police_station.json"),
            "alley": Region("alley", map_dir / "alley.json"),
        }

        # Start in Office at Level 0
        self.current_region_name = "office"
        office = self.regions["office"]
        self.player = Player(241, 94)

        self.camera = Camera(settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT)
        self.camera.follow(self.player, rate=settings.CAMERA_FOLLOW_RATE)
        self._update_camera_bounds()
        self.camera.x, self.camera.y = self.player.x, self.player.y
        self.camera.update(0)

        # Setup triggers and NPCs in each region
        self._setup_triggers()
        self._populate_npcs()

        # Prompt displayed on screen when near an interactable
        self.active_prompt: Optional[str] = None
        self.active_interactable: Optional[Any] = None

        # Automatically start opening dialogue with Sofia if starting at Level 0
        if not self.story.flags["sofia_office_talked"]:
            self._start_intro_cutscene()

    @property
    def region(self) -> Region:
        return self.regions[self.current_region_name]

    # ── Configuración de Triggers ────────────────────────────────────────────

    def _setup_triggers(self) -> None:
        """Register specific interactive triggers per region."""
        # 1. Oficina: Pizarra de Corcho
        office = self.regions["office"]
        office.triggers.append(
            Trigger(
                trigger_id="corkboard",
                x=220,
                y=50,
                width=44,
                height=26,
                trigger_type="corkboard",
                prompt_text="[ESPACIO / E] Examinar Pizarra de Corcho",
                action_fn=self._open_corkboard,
            )
        )

        # 2. Museo: Marco vacío robado
        museum = self.regions["museum"]
        museum.triggers.append(
            Trigger(
                trigger_id="empty_frame",
                x=224,
                y=48,
                width=48,
                height=28,
                trigger_type="interaction",
                prompt_text="[ESPACIO / E] Inspeccionar marco vacío robado",
                action_fn=self._inspect_museum_frame,
            )
        )

        # 3. Comisaría: Acceso al archivo policial en el sótano
        police = self.regions["police_station"]
        police.triggers.append(
            Trigger(
                trigger_id="archive",
                x=320,
                y=96,
                width=40,
                height=36,
                trigger_type="minigame",
                prompt_text="[ESPACIO / E] Infiltrarse en archivo policial",
                action_fn=self._start_archive_minigame,
            )
        )

        # 4. Nightclub: Triggers visuales para las puertas de Stealth y Safecracker
        nightclub = self.regions["nightclub"]
        nightclub.triggers.append(
            Trigger(
                trigger_id="stealth_prompt",
                x=385,
                y=8,
                width=90,
                height=40,
                trigger_type="minigame",
                prompt_text="[ESPACIO / E] Entrar a oficinas traseras (Sigilo)",
                action_fn=lambda w, s: self._try_enter_club_door("stealth"),
            )
        )
        nightclub.triggers.append(
            Trigger(
                trigger_id="safecracker_prompt",
                x=98,
                y=32,
                width=32,
                height=24,
                trigger_type="minigame",
                prompt_text="[ESPACIO / E] Forzar caja fuerte de la bóveda",
                action_fn=lambda w, s: self._try_enter_club_door("safecracker"),
            )
        )

    # ── Población de NPCs ───────────────────────────────────────────────────

    def _populate_npcs(self) -> None:
        """Spawn story-relevant NPCs in their respective locations."""
        for r in self.regions.values():
            r.npcs.clear()

        # 1. Oficina
        office = self.regions["office"]
        office.npcs.append(NPC(198, 80, "Sofia Del Roscio", dialogue_key="sofia_office", direction="right"))
        office.npcs.append(NPC(160, 68, "Lauren", dialogue_key="lauren_office", direction="down"))

        # 2. Museo
        museum = self.regions["museum"]
        museum.npcs.append(NPC(200, 180, "Curador Lombardi", dialogue_key="museum_curator", direction="down"))

        # 3. Comisaría
        police = self.regions["police_station"]
        police.npcs.append(NPC(180, 160, "Sargento Bianchi", dialogue_key="police_officer", direction="down"))

        # 4. Callejón
        alley = self.regions["alley"]
        alley.npcs.append(NPC(240, 140, "Guardia Morales", dialogue_key="morales_interrogation", direction="down"))

        # 5. Nightclub
        club = self.regions["nightclub"]
        club.npcs.append(NPC(280, 180, "Sofia Del Roscio", dialogue_key="sofia_club", direction="left"))

        # 6. Ciudad
        city = self.regions["city"]
        city.npcs.append(NPC(1040, 720, "Canillita", dialogue_key="canillita", direction="down"))
        city.npcs.append(NPC(600, 730, "Desempleado", dialogue_key="citizen_unemployed", direction="right"))
        city.npcs.append(NPC(900, 730, "Parroquiano", dialogue_key="citizen_patron", direction="left"))

    # ── Acciones de Triggers e Interacciones ─────────────────────────────────

    def _start_intro_cutscene(self) -> None:
        """Play Level 0 opening scene where Sofia hires Gallagher."""
        data = DIALOGUES["sofia_office_intro"]

        def on_finish():
            self.story.flags["sofia_office_talked"] = True
            self.story.level = max(self.story.level, 1)
            self.story.push_notification("Caso aceptado: Investigar el Museo Del Roscio")

        self.stack.push(
            DialogueState(self.stack),
            text=data["pages"],
            speaker=data["speaker"],
            on_finish=on_finish,
        )

    def _open_corkboard(self, world: Any, story: StoryManager) -> None:
        self._clear_movement()
        self.stack.push(CorkboardState(self.stack))

    def _inspect_museum_frame(self, world: Any, story: StoryManager) -> None:
        self._clear_movement()
        if not story.flags["c01_inspected"]:
            data = DIALOGUES["museum_frame_inspection"]

            def on_finish():
                story.add_card("C01")
                story.flags["c01_inspected"] = True

            self.stack.push(
                DialogueState(self.stack),
                text=data["pages"],
                speaker=data["speaker"],
                on_finish=on_finish,
            )
        else:
            self.stack.push(
                DialogueState(self.stack),
                text="El marco vacío robado. Los cortes confirman que fue un trabajo interno sin forzar.",
                speaker="P.I. Gallagher",
            )

    def _start_archive_minigame(self, world: Any, story: StoryManager) -> None:
        can_access, reason = story.can_access_minigame("archive")
        if not can_access:
            self._monologue(reason)
            return
        self._clear_movement()
        self.stack.push(PoliceArchiveState(self.stack))

    def _try_enter_club_door(self, door_type: str) -> None:
        can_access, reason = self.story.can_access_minigame(door_type)
        if not can_access:
            self.player.y += 14
            self._monologue(reason)
            return

        self._clear_movement()
        if door_type == "stealth":
            self.player.y = max(self.player.y, 52)
            self.stack.push(StealthMinigameState(self.stack))
        elif door_type == "safecracker":
            self.player.y = max(self.player.y, 58)
            self.stack.push(SafeCrackerState(self.stack))

    def _monologue(self, text: str) -> None:
        """Display an internal monologue from Gallagher."""
        self._clear_movement()
        self.stack.push(DialogueState(self.stack), text=text, speaker="P.I. Gallagher")

    # ── Actualización de Cuadro y Movimiento ─────────────────────────────────

    def update(self, dt: float) -> None:
        # Movement calculation
        dx = float(self.player.held["move_right"] - self.player.held["move_left"])
        dy = float(self.player.held["move_down"] - self.player.held["move_up"])
        if dx and dy:
            dx *= 0.7071
            dy *= 0.7071

        self._move_axis(dx * Player.SPEED * dt, 0)
        self._move_axis(0, dy * Player.SPEED * dt)
        self.player.update(dt)

        self._check_door_collision()
        self._update_interaction_prompts()
        self.camera.update(dt)

        # Update floating notification banners
        self.story.update_notifications(dt)

    def _move_axis(self, dx: float, dy: float) -> None:
        if not dx and not dy:
            return
        next_rect = self.player.collision_rect.move(round(dx), round(dy))
        if self.region.is_walkable(next_rect):
            self.player.x += dx
            self.player.y += dy

    def _door_objects(self):
        return self.region.tilemap.object_layers.get("Doors", [])

    def _door_collides(self, door) -> bool:
        player_rect = self.player.collision_rect
        if not getattr(door, "width", 0) or not getattr(door, "height", 0):
            return player_rect.collidepoint(round(door.x), round(door.y))
        door_rect = pygame.Rect(
            round(door.x), round(door.y), round(door.width), round(door.height)
        )
        return player_rect.colliderect(door_rect)

    def _check_door_collision(self) -> None:
        """Verify door collisions with narrative gating."""
        for door in self._door_objects():
            if not self._door_collides(door):
                continue

            door_name = str(getattr(door, "name", "") or "").strip().lower()

            # Entering a zone from the City
            if self.current_region_name == "city":
                if door_name not in self.CITY_DOOR_INDEX:
                    continue

                can_enter, reason = self.story.can_access_zone(door_name)
                if not can_enter:
                    # Push back player slightly to prevent sticking
                    self.player.y += 12
                    self._monologue(reason)
                    return

                # Enter zone
                self.current_region_name = door_name
                self.player.x, self.player.y = self.region.entry_position("south")
                self._update_camera_bounds()
                return

            # Exit to City
            if door_name == "exit":
                self._return_to_city()
                self._update_camera_bounds()
                return

            # Minigame doors inside Nightclub
            if door_name in ("stealth", "safecracker"):
                self._try_enter_club_door(door_name)
                return

    def _return_to_city(self) -> None:
        city_door = self.regions["city"].tilemap.object_layers["Doors"][
            self.CITY_DOOR_INDEX[self.current_region_name]
        ]
        door_center = pygame.Vector2(
            city_door.x + city_door.width / 2,
            city_door.y + city_door.height / 2,
        )
        for offset_x, offset_y in (
            (0, 20), (0, -20), (20, 0), (-20, 0),
            (14, 14), (-14, 14), (14, -14), (-14, -14),
        ):
            x = door_center.x + offset_x - 1
            y = door_center.y + offset_y - 12
            player_rect = pygame.Rect(round(x + 1), round(y + 12), 16, 16)
            if (
                self.regions["city"].is_walkable(player_rect)
                and not self._door_collides_rect(player_rect, city_door)
            ):
                self.current_region_name = "city"
                self.player.x, self.player.y = x, y
                return
        self.current_region_name = "city"
        self.player.x, self.player.y = door_center.x - 1, door_center.y + 20 - 12

    @staticmethod
    def _door_collides_rect(player_rect: pygame.Rect, door) -> bool:
        if not getattr(door, "width", 0) or not getattr(door, "height", 0):
            return player_rect.collidepoint(round(door.x), round(door.y))
        door_rect = pygame.Rect(round(door.x), round(door.y), round(door.width), round(door.height))
        return player_rect.colliderect(door_rect)

    def _update_camera_bounds(self) -> None:
        self.camera.bounds = pygame.Rect(0, 0, self.region.width, self.region.height)

    # ── Prompts de Interacción ───────────────────────────────────────────────

    def _update_interaction_prompts(self) -> None:
        """Detect if the player is near an interactive trigger or NPC."""
        self.active_prompt = None
        self.active_interactable = None

        player_rect = self.player.rect

        # Check triggers in current region
        for trigger in self.region.triggers:
            if trigger.collides(player_rect):
                self.active_prompt = trigger.prompt_text
                self.active_interactable = trigger
                return

        # Check NPCs in current region (direct rect collision)
        for npc in self.region.npcs:
            if player_rect.colliderect(npc.rect):
                self.active_prompt = f"[ESPACIO / E] Hablar con {npc.name}"
                self.active_interactable = npc
                return

    # ── Manejo de Entrada (Interacción) ──────────────────────────────────────

    def on_input(self, input_id: str, input_data: Any) -> None:
        self.player.on_input(input_id, input_data)
        if input_id in ("interact", "enter") and getattr(input_data, "pressed", False):
            self._try_interact()

    def _try_interact(self) -> None:
        if self.active_interactable is None:
            return

        interactable = self.active_interactable
        self._clear_movement()

        # 1. Trigger interaction
        if isinstance(interactable, Trigger):
            if interactable.action_fn is not None:
                interactable.action_fn(self, self.story)
            return

        # 2. NPC interaction
        if isinstance(interactable, NPC):
            self._interact_with_npc(interactable)

    def _interact_with_npc(self, npc: NPC) -> None:
        key = npc.dialogue_key

        # Sofia en Oficina
        if key == "sofia_office":
            if not self.story.flags["sofia_office_talked"]:
                self._start_intro_cutscene()
            else:
                self._monologue("Sofia me espera en el museo. Debo encontrar 'La Dama del Lirio'.")
            return

        # Lauren en Oficina
        if key == "lauren_office":
            visit = self.story.get_current_corcho_visit()
            hint = DIALOGUES["lauren_office"]["hints"].get(visit, "Revise las pistas en el corcho, jefe.")
            self.stack.push(DialogueState(self.stack), text=hint, speaker="Lauren")
            return

        # Curador en Museo
        if key == "museum_curator":
            data = DIALOGUES["museum_curator"]
            self.stack.push(DialogueState(self.stack), text=data["pages"], speaker=data["speaker"])
            return

        # Oficial en Comisaría
        if key == "police_officer":
            data = DIALOGUES["police_officer"]
            self.stack.push(DialogueState(self.stack), text=data["pages"], speaker=data["speaker"])
            return

        # Morales en Callejón
        if key == "morales_interrogation":
            if not self.story.flags["morales_confronted"]:
                data = DIALOGUES["morales_interrogation"]

                def on_confrontation_complete():
                    def on_confession_end():
                        for c in data["reward_cards"]:
                            self.story.add_card(c)
                        self.story.flags["morales_confronted"] = True
                    self.stack.push(
                        DialogueState(self.stack),
                        text=data["pages"],
                        speaker=data["speaker"],
                        on_finish=on_confession_end,
                    )

                self.stack.push(
                    ConfrontationState(self.stack),
                    confrontation_id="morales",
                    on_complete=on_confrontation_complete
                )
            else:
                self.stack.push(
                    DialogueState(self.stack),
                    text="¡Ya le dije todo lo que sé! ¡No deje que el Tigre me encuentre!",
                    speaker="Guardia Morales",
                )
            return

        # Sofia en Club Velvet
        if key == "sofia_club":
            if not self.story.flags["sofia_club_talked"]:
                data = DIALOGUES["sofia_club"]

                def on_sofia_club():
                    for c in data["reward_cards"]:
                        self.story.add_card(c)
                    self.story.flags["sofia_club_talked"] = True

                self.stack.push(
                    DialogueState(self.stack),
                    text=data["pages"],
                    speaker=data["speaker"],
                    on_finish=on_sofia_club,
                )
            else:
                self.stack.push(
                    DialogueState(self.stack),
                    text="Use la llave con cuidado, detective. No llame la atención de los matones.",
                    speaker="Sofia Del Roscio",
                )
            return

        # Canillita en Ciudad
        if key == "canillita":
            if self.story.flags["corcho1_done"] and not self.story.flags["recorte_encontrado"]:
                data = DIALOGUES["canillita"]["special_c07"]

                def on_canillita():
                    self.story.add_card("C07")
                    self.story.flags["recorte_encontrado"] = True

                self.stack.push(
                    DialogueState(self.stack),
                    text=data["pages"],
                    speaker=data["speaker"],
                    on_finish=on_canillita,
                )
            else:
                import random
                line = random.choice(DIALOGUES["canillita"]["default"])
                self.stack.push(DialogueState(self.stack), text=line, speaker="Canillita")
            return

        # Transeúntes genéricos
        if key in DIALOGUES:
            data = DIALOGUES[key]
            self.stack.push(DialogueState(self.stack), text=data["pages"], speaker=data["speaker"])
            return

        # Línea de fallback
        self.stack.push(DialogueState(self.stack), text=npc.dialogue())

    def _clear_movement(self) -> None:
        for key in self.player.held:
            self.player.held[key] = False

    # ── Renderizado del Mundo y UI ───────────────────────────────────────────

    def render(self, surface: pygame.Surface) -> None:
        self.region.render(surface, self.camera)
        self.player.render(surface, self.camera)

        # Region label in top-left
        reg_text = self.current_region_name.upper()
        rw, rh = settings.FONTS["small"].size(reg_text)
        reg_panel = Panel(10, 8, rw + 14, rh + 6, theme=NOIR_PROMPT_THEME)
        reg_panel.render(surface)
        reg_label = Label(
            17,
            11,
            reg_text,
            font=settings.FONTS["small"],
            theme=NOIR_PROMPT_THEME,
        )
        reg_label.render(surface)

        # Floating Interaction Prompt badge
        if self.active_prompt:
            pw, ph = settings.FONTS["small"].size(self.active_prompt)
            badge_w = pw + 16
            badge_h = ph + 8
            badge_x = settings.VIRTUAL_WIDTH // 2 - badge_w // 2
            badge_y = settings.VIRTUAL_HEIGHT - 34

            prompt_panel = Panel(badge_x, badge_y, badge_w, badge_h, theme=NOIR_PROMPT_THEME)
            prompt_panel.render(surface)
            prompt_label = Label(
                settings.VIRTUAL_WIDTH // 2,
                badge_y + 4,
                self.active_prompt,
                font=settings.FONTS["small"],
                center=True,
                theme=NOIR_PROMPT_THEME,
            )
            prompt_label.render(surface)

        # Floating Notification Banners (at top center)
        if self.story.notifications:
            notif = self.story.notifications[0]
            nw, nh = settings.FONTS["small"].size(notif["text"])
            banner_w = nw + 24
            banner_h = nh + 8
            banner_x = settings.VIRTUAL_WIDTH // 2 - banner_w // 2
            banner_y = 10

            notif_panel = Panel(banner_x, banner_y, banner_w, banner_h, theme=NOIR_PROMPT_THEME)
            notif_panel.render(surface)
            notif_label = Label(
                settings.VIRTUAL_WIDTH // 2,
                banner_y + 4,
                notif["text"],
                font=settings.FONTS["small"],
                center=True,
                theme=NOIR_PROMPT_THEME,
            )
            notif_label.render(surface)
