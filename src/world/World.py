"""
P.I. Gallagher: The Missing Art

World — Top-down game world managing regions, camera, player movement,
conditional triggers, dynamic NPCs, and narrative progression via StoryManager.
"""

import pathlib
from typing import Any, Dict, List, Optional, Tuple, Callable
import random

import pygame
from gale.camera import Camera
from gale.state import StateStack
from gale.text import render_text
from gale.timer import Timer

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
from src.text_utils import wrap_text


class World:
    DOOR_TARGETS = ("office", "museum", "nightclub", "police_station", "alley")
    CITY_DOOR_INDEX = {target: index for index, target in enumerate(DOOR_TARGETS) if target}

    # Configuration map linking dialogue keys to display names and default facing directions
    NPC_CONFIGS = {
        "sofia_office": {"display_name": "Sofia Del Roscio", "direction": "right"},
        "lauren_office": {"display_name": "Lauren", "direction": "down"},
        "museum_curator": {"display_name": "Curador Lombardi", "direction": "down"},
        "police_officer": {"display_name": "Sargento Bianchi", "direction": "down"},
        "morales_interrogation": {"display_name": "Guardia Morales", "direction": "down"},
        "sofia_club": {"display_name": "Sofia Del Roscio", "direction": "left"},
        "canillita": {"display_name": "Canillita", "direction": "down"},
        "citizen_unemployed": {"display_name": "Desempleado", "direction": "right"},
        "citizen_patron": {"display_name": "Parroquiano", "direction": "left"},
    }

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

        # Transition effect variables
        self.transitioning = False
        self.transition_alpha = 255
        Timer.tween(0.4, [(self, {"transition_alpha": 0})], ease_function_name="out_cubic")

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

    # ── Configuración de Transiciones ───────────────────────────────────────

    def _start_transition(self, on_middle_action: Callable[[], None]) -> None:
        """Handles screen fade-out and fade-in when changing rooms/zones."""
        if self.transitioning:
            return

        self.transitioning = True
        self.transition_alpha = 0
        self._clear_movement()

        def on_fade_out_complete():
            on_middle_action()
            Timer.tween(
                0.4,
                [(self, {"transition_alpha": 0})],
                ease_function_name="out_cubic",
                on_finish=lambda: setattr(self, "transitioning", False),
            )

        Timer.tween(
            0.4,
            [(self, {"transition_alpha": 255})],
            ease_function_name="in_cubic",
            on_finish=on_fade_out_complete,
        )

    # ── Configuración de Triggers ────────────────────────────────────────────

    def _setup_triggers(self) -> None:
        """Bind dynamic actions and prompts to tilemap-loaded triggers."""
        trigger_configs = {
            "corkboard": {
                "prompt": "[ESPACIO] Examinar Pizarra de Corcho",
                "action": self._open_corkboard,
            },
            "empty_frame": {
                "prompt": "[ESPACIO] Inspeccionar marco vacío robado",
                "action": self._inspect_museum_frame,
            },
            "archive": {
                "prompt": "[ESPACIO] Infiltrarse en archivo policial",
                "action": self._start_archive_minigame,
            },
            "stealth": {
                "prompt": "[ESPACIO] Entrar a oficinas traseras (Sigilo)",
                "action": lambda w, s: self._try_enter_club_door("stealth"),
            },
            "safecracker": {
                "prompt": "[ESPACIO] Forzar caja fuerte de la bóveda",
                "action": lambda w, s: self._try_enter_club_door("safecracker"),
            },
        }

        for region in self.regions.values():
            for trigger in region.triggers:
                if trigger.trigger_id in trigger_configs:
                    cfg = trigger_configs[trigger.trigger_id]
                    if not trigger.prompt_text:
                        trigger.prompt_text = cfg["prompt"]
                    trigger.action_fn = cfg["action"]

    # ── Población de NPCs ───────────────────────────────────────────────────

    def _populate_npcs(self) -> None:
        """Dynamically populate NPCs in each region based on Tiled NPC layers."""
        for region in self.regions.values():
            region.npcs.clear()
            npc_layer = region.tilemap.object_layers.get("NPCs", [])

            for obj in npc_layer:
                dialogue_key = str(getattr(obj, "name", "") or "").strip()
                if not dialogue_key:
                    continue

                # Match against configuration metadata or fallback to Tiled attributes
                config = self.NPC_CONFIGS.get(
                    dialogue_key,
                    {
                        "display_name": getattr(obj, "display_name", dialogue_key.capitalize()),
                        "direction": getattr(obj, "direction", "down"),
                    },
                )

                npc = NPC(
                    x=obj.x,
                    y=obj.y,
                    name=config["display_name"],
                    dialogue_key=dialogue_key,
                    direction=config["direction"],
                )
                region.npcs.append(npc)

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
        if not self.transitioning:
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
        """Verify door collisions with narrative gating and trigger transitions."""
        if self.transitioning:
            return

        for door in self._door_objects():
            if not self._door_collides(door):
                continue

            door_name = str(getattr(door, "name", "") or "").strip().lower()

            if self.current_region_name == "city":
                if door_name not in self.CITY_DOOR_INDEX:
                    continue

                can_enter, reason = self.story.can_access_zone(door_name)
                if not can_enter:
                    self.player.y += 12
                    self._monologue(reason)
                    return

                def enter_door_action():
                    self.current_region_name = door_name
                    self.player.x, self.player.y = self.region.entry_position("south")
                    self._sync_camera_instant()

                    # Play door sound for indoor locations, bypass open street transitions like the alley
                    if door_name != "alley":
                        settings.SOUNDS[f"doorOpen_{random.randint(1, 2)}"].play()

                self._start_transition(enter_door_action)
                return

            if door_name == "exit":
                def exit_door_action():
                    # Play door sound only when leaving an indoor room, not when walking out of the alley
                    if self.current_region_name != "alley":
                        settings.SOUNDS[f"doorClose_{random.randint(1, 4)}"].play()

                    self._return_to_city()
                    self._sync_camera_instant()

                self._start_transition(exit_door_action)
                return

            if door_name in ("stealth", "safecracker"):
                self._try_enter_club_door(door_name)
                return
            
    def _sync_camera_instant(self) -> None:
        """Instantly align camera position with player and update bounds to avoid jumps."""
        self._update_camera_bounds()
        self.camera.x, self.camera.y = self.player.x, self.player.y
        self.camera.update(0)

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

        for trigger in self.region.triggers:
            if trigger.collides(player_rect):
                self.active_prompt = trigger.prompt_text
                self.active_interactable = trigger
                return

        for npc in self.region.npcs:
            if player_rect.colliderect(npc.rect):
                self.active_prompt = f"[ESPACIO] Hablar con {npc.name}"
                self.active_interactable = npc
                return

    # ── Manejo de Entrada (Interacción) ──────────────────────────────────────

    def on_input(self, input_id: str, input_data: Any) -> None:
        if self.transitioning:
            return
        self.player.on_input(input_id, input_data)
        if input_id in ("space", "enter") and getattr(input_data, "pressed", False):
            self._try_interact()

    def _try_interact(self) -> None:
        if self.active_interactable is None:
            return

        interactable = self.active_interactable
        self._clear_movement()

        if isinstance(interactable, Trigger):
            if interactable.action_fn is not None:
                interactable.action_fn(self, self.story)
            return

        if isinstance(interactable, NPC):
            self._interact_with_npc(interactable)

    def _interact_with_npc(self, npc: NPC) -> None:
        key = npc.dialogue_key

        if key == "sofia_office":
            if not self.story.flags["sofia_office_talked"]:
                self._start_intro_cutscene()
            else:
                self._monologue("Sofia me espera en el museo. Debo encontrar 'La Dama del Lirio'.")
            return

        if key == "lauren_office":
            visit = self.story.get_current_corcho_visit()
            hint = DIALOGUES["lauren_office"]["hints"].get(visit, "Revise las pistas en el corcho, jefe.")
            self.stack.push(DialogueState(self.stack), text=hint, speaker="Lauren")
            return

        if key == "museum_curator":
            data = DIALOGUES["museum_curator"]
            self.stack.push(DialogueState(self.stack), text=data["pages"], speaker=data["speaker"])
            return

        if key == "police_officer":
            data = DIALOGUES["police_officer"]
            self.stack.push(DialogueState(self.stack), text=data["pages"], speaker=data["speaker"])
            return

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

        if key in DIALOGUES:
            data = DIALOGUES[key]
            self.stack.push(DialogueState(self.stack), text=data["pages"], speaker=data["speaker"])
            return

        self.stack.push(DialogueState(self.stack), text=npc.dialogue())

    def _clear_movement(self) -> None:
        for key in self.player.held:
            self.player.held[key] = False

    # ── Renderizado del Mundo y UI ───────────────────────────────────────────

    def render(self, surface: pygame.Surface) -> None:
        self.region.render(surface, self.camera)
        self.player.render(surface, self.camera)

        font = settings.FONTS["medium"]

        if not self.story.notifications:
            reg_text = self.current_region_name.upper()
            rw, rh = font.size(reg_text)

            reg_panel = Panel(10, 8, rw + 16, rh + 8, theme=NOIR_PROMPT_THEME)
            reg_panel.render(surface)

            reg_label = Label(
                18,
                12,
                reg_text,
                font=font,
                theme=NOIR_PROMPT_THEME,
            )
            reg_label.render(surface)
        else:
            notif = self.story.notifications[0]
            max_text_w = settings.VIRTUAL_WIDTH - 60

            lines = wrap_text(font, notif["text"], max_text_w)

            line_height = font.get_linesize()
            text_w = max(font.size(line)[0] for line in lines)

            banner_w = text_w + 24
            banner_h = (line_height * len(lines)) + 12
            banner_x = (settings.VIRTUAL_WIDTH - banner_w) // 2
            banner_y = 10

            notif_panel = Panel(banner_x, banner_y, banner_w, banner_h, theme=NOIR_PROMPT_THEME)
            notif_panel.render(surface)

            for i, line in enumerate(lines):
                line_y = banner_y + 6 + (i * line_height)
                notif_label = Label(
                    banner_x + 12,
                    line_y,
                    line,
                    font=font,
                    theme=NOIR_PROMPT_THEME,
                )
                notif_label.render(surface)

        if self.active_prompt:
            pw, ph = font.size(self.active_prompt)
            badge_w = pw + 20
            badge_h = ph + 10
            badge_x = (settings.VIRTUAL_WIDTH - badge_w) // 2
            badge_y = settings.VIRTUAL_HEIGHT - 36

            prompt_panel = Panel(badge_x, badge_y, badge_w, badge_h, theme=NOIR_PROMPT_THEME)
            prompt_panel.render(surface)

            prompt_label = Label(
                badge_x + 10,
                badge_y + 5,
                self.active_prompt,
                font=font,
                theme=NOIR_PROMPT_THEME,
            )
            prompt_label.render(surface)

        if self.transition_alpha > 0:
            overlay = pygame.Surface(
                (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT),
                pygame.SRCALPHA,
            )
            overlay.fill((0, 0, 0, int(self.transition_alpha)))
            surface.blit(overlay, (0, 0))