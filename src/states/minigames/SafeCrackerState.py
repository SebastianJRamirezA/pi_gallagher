"""A 1930s vintage safe game using Gale UI elements and noir aesthetics."""

import array
import math
import random

import pygame

from gale.game import Game
from gale.input_handler import InputData
from gale.timer import Timer
from gale.state import BaseState
from gale.ui import Label, Panel, Theme

import settings
from src.ui.theme import COLOR_ACCENT_RED, COLOR_BRASS, COLOR_MUTED, COLOR_SUCCESS


class SafeCrackerState(BaseState):
    def enter(self) -> None:
        music_path = settings.BASE_DIR / "assets" / "sounds" / "hurry_up.mp3"
        if music_path.exists():
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(loops=-1)

        self.dial = 0.0
        self.stage = 0
        self.turning = 0
        self.fine_control = False
        self.overshot = False
        self.stutter_time = 0.0
        self.click_number = -1
        self.message = "Escucha la cerradura. Ajusta el primer número."
        self.complete = False
        self.click_sound = self._make_tone(170)
        self.heavy_click_sound = self._make_tone(105)
        self.confirm_sound = self._make_tone(310, 0.14)
        self.alarm_sound = self._make_tone(62, 0.28)

        self.timer = 60.0

        # Colors for 1930s-1940s Black & Gold Vintage Safe Aesthetic
        self.COLOR_BACKGROUND = (12, 12, 14)
        self.COLOR_SAFE_BODY = (24, 25, 28)
        self.COLOR_SAFE_BORDER = (16, 17, 19)
        self.COLOR_GOLD = (212, 168, 75)
        self.COLOR_GOLD_DARK = (140, 105, 35)
        self.COLOR_STEEL = (110, 116, 122)
        self.COLOR_STEEL_DARK = (45, 48, 52)
        self.COLOR_TEXT = (225, 218, 200)

        self.DIAL_SPEED = 72.0
        self.FINE_DIAL_SPEED = 18.0

        # Build random combination for the safe. This is a list of three numbers between 0 and 99.
        self.COMBINATION = [random.randint(0, 99) for _ in range(3)]

        def decrement_timer():
            self.timer -= 1

            # Play warning sound on timer if we get low
            if self.timer <= 5:
                settings.SOUNDS["clock"].play()

        Timer.every(1, decrement_timer)

        self._build_ui()

    def _build_ui(self) -> None:
        """Construct static safe body, panels, and labels using gale.ui."""
        safe_x, safe_y = 20, 8
        safe_w, safe_h = settings.VIRTUAL_WIDTH - 40, 200

        # 1. Main Safe Body Frame Panel
        self.safe_theme = Theme(
            background_color=pygame.Color(*self.COLOR_SAFE_BODY),
            border_color=pygame.Color(*self.COLOR_GOLD_DARK),
            border_width=2,
        )
        self.safe_panel = Panel(safe_x, safe_y, safe_w, safe_h, theme=self.safe_theme)

        # 2. Top Left Metadata (Perfectly aligned & subordinated)
        self.lbl_title = Label(
            safe_x + 16,
            safe_y + 12,
            "CAJA FUERTE",
            font=settings.FONTS["large"],
            color=pygame.Color(*self.COLOR_GOLD),
            theme=self.safe_theme,
        )

        self.lbl_tumbler = Label(
            safe_x + 16,
            safe_y + 34,
            "DISCO 1 / 3",
            font=settings.FONTS["medium"],
            color=pygame.Color(*self.COLOR_GOLD_DARK),
            theme=self.safe_theme,
        )

        # 3. Top Right Metadata (Perfectly right-aligned with proper margin)
        self.lbl_stress = Label(
            safe_x + safe_w - 108,
            safe_y + 12,
            "ESTRÉS",
            font=settings.FONTS["medium"],
            color=pygame.Color(*self.COLOR_GOLD_DARK),
            theme=self.safe_theme,
        )

        self.lbl_timer = Label(
            safe_x + safe_w - 108,
            safe_y + 42,
            f"TIEMPO: {int(self.timer)}s",
            font=settings.FONTS["medium"],
            color=pygame.Color(*self.COLOR_GOLD_DARK),
            theme=self.safe_theme,
        )

        # 4. Central Digital Display Box for Dial Marker ("00")
        box_w, box_h = 36, 18
        box_x = settings.VIRTUAL_WIDTH // 2 - box_w // 2
        box_y = safe_y + safe_h - 26

        self.dial_box_panel = Panel(
            box_x, box_y, box_w, box_h,
            theme=Theme(
                background_color=pygame.Color(14, 15, 18),
                border_color=pygame.Color(*self.COLOR_GOLD_DARK),
                border_width=1,
            )
        )

        self.lbl_dial_val = Label(
            box_x + 10,
            box_y + 2,
            "00",
            font=settings.FONTS["medium"],
            color=pygame.Color(*self.COLOR_GOLD),
            theme=self.safe_theme,
        )

        # 5. Dedicated Instruction Panel (Below main safe body frame)
        inst_y = safe_y + safe_h + 6
        inst_h = 24
        self.inst_panel = Panel(
            safe_x, inst_y, safe_w, inst_h,
            theme=Theme(
                background_color=pygame.Color(18, 19, 22),
                border_color=pygame.Color(*self.COLOR_GOLD_DARK),
                border_width=1,
            )
        )

        self.lbl_message = Label(
            safe_x + 12,
            inst_y + 5,
            self.message,
            font=settings.FONTS["medium"],
            color=pygame.Color(*self.COLOR_TEXT),
            theme=self.safe_theme,
        )

        self.lbl_controls = Label(
            safe_x + 12,
            inst_y + inst_h + 6,
            "Flechitas: Moverse  |  SHIFT: Aumentar precisión  |  ESPACIO: Fijar disco",
            font=settings.FONTS["small"],
            color=COLOR_MUTED,
            theme=self.safe_theme,
        )

    def _make_tone(self, frequency: int, duration: float = 0.055):
        """Create a short metal-like cue without requiring an asset file."""
        try:
            sample_rate = 22050
            samples = array.array("h")
            for index in range(int(sample_rate * duration)):
                envelope = 1.0 - index / (sample_rate * duration)
                value = math.sin(2 * math.pi * frequency * index / sample_rate)
                samples.append(int(10500 * envelope * value))
            return pygame.mixer.Sound(buffer=samples.tobytes())
        except pygame.error:
            return None

    @staticmethod
    def _play(sound) -> None:
        if sound is not None:
            sound.play()

    def update(self, dt: float) -> None:
        if self.complete:
            self.state_machine.pop()
            return

        if self.turning:
            speed = self.FINE_DIAL_SPEED if self.fine_control else self.DIAL_SPEED
            previous = self.dial
            self.dial = (self.dial + self.turning * speed * dt) % 360.0
            current_number = self._dial_number()
            self.stutter_time = max(0.0, self.stutter_time - dt)

            if not self.overshot and self._passed_target(previous, self.dial, self.turning):
                self.overshot = True
                self.stage = 0
                self.message = "Demasiado lejos. Da el giro completo para reiniciar."
                self._play(self.alarm_sound)
            elif not self.overshot and current_number != self.click_number:
                self.click_number = current_number
                distance = self._target_distance()
                self._play(self.heavy_click_sound if distance <= 8 else self.click_sound)
                if distance <= 3:
                    self.stutter_time = 0.07

        if self.overshot and self._crossed_zero(self.dial, self.turning):
            self.dial = 0.0
            self.overshot = False
            self.click_number = 0
            self.message = "Reiniciado. Acércate con más cuidado."

        if self.timer <= 0:
            Timer.clear()

        # Update dynamic labels
        self.lbl_tumbler.set_text(f"DISCO {min(self.stage + 1, 3)} / 3")
        self.lbl_dial_val.set_text(f"{self._dial_number():02d}")
        self.lbl_message.set_text(self.message)
        self.lbl_message.color = COLOR_ACCENT_RED if self.overshot else pygame.Color(*self.COLOR_TEXT)
        self.lbl_timer.set_text(f"TIEMPO: {max(0, int(self.timer))}s")

    def _dial_number(self) -> int:
        return int(round(self.dial / 3.6)) % 100

    def _target_angle(self) -> float:
        return self.COMBINATION[self.stage] * 3.6

    def _target_distance(self) -> float:
        difference = abs(self.dial - self._target_angle())
        return min(difference, 360.0 - difference) / 3.6

    def _passed_target(self, previous: float, current: float, direction: int) -> bool:
        tolerance = 1 * 3.6
        effective_target = (self._target_angle() + (direction * tolerance)) % 360.0

        if direction > 0:
            travelled = (current - previous) % 360.0
            from_target = (effective_target - previous) % 360.0
        else:
            travelled = (previous - current) % 360.0
            from_target = (previous - effective_target) % 360.0

        return 0.0 < from_target <= travelled

    @staticmethod
    def _crossed_zero(dial: float, direction: int) -> bool:
        return (direction > 0 and dial < 8.0) or (direction < 0 and dial > 352.0)

    def _confirm(self) -> None:
        if self.complete or self.overshot:
            return
        if self._target_distance() <= 1.5:
            self._play(self.confirm_sound)
            self.stage += 1
            if self.stage == len(self.COMBINATION):
                self.complete = True
                Timer.clear()
                from src.story.StoryManager import StoryManager
                story = StoryManager.get_instance()
                for c in ("C15", "C16", "C17"):
                    story.add_card(c)
                story.flags["safecracker_completed"] = True
                self.message = "Los pestillos ceden. La caja fuerte está abierta."
                self.state_machine.pop()
            else:
                self.dial = 0.0
                self.click_number = -1
                self.message = "Bien. El siguiente pestillo escucha."
        else:
            self.message = "Ese no es el número. Acércate más y escucha."

    def _render_filigree(self, surface: pygame.Surface, x: int, y: int, flip_x: bool = False, flip_y: bool = False) -> None:
        """Draw decorative 1930s art-deco gold corner ornaments on the safe door."""
        sx = -1 if flip_x else 1
        sy = -1 if flip_y else 1
        points = [
            (x, y),
            (x + 12 * sx, y),
            (x + 12 * sx, y + 2 * sy),
            (x + 2 * sx, y + 2 * sy),
            (x + 2 * sx, y + 12 * sy),
            (x, y + 12 * sy)
        ]
        pygame.draw.polygon(surface, self.COLOR_GOLD_DARK, points)
        pygame.draw.polygon(surface, self.COLOR_GOLD, [(p[0] + sx, p[1] + sy) for p in points[:4]])
        pygame.draw.line(surface, self.COLOR_GOLD, (x + 4 * sx, y + 4 * sy), (x + 8 * sx, y + 8 * sy), 1)

    def render(self, surface: pygame.Surface) -> None:
        surface.fill(self.COLOR_BACKGROUND)

        # 1. Outer Safe Body Panel Frame & Inner Decorative Insets
        self.safe_panel.render(surface)

        sp_x, sp_y = self.safe_panel.x, self.safe_panel.y
        sp_w, sp_h = self.safe_panel.width, self.safe_panel.height

        # Inner Decorative Gold Frame Line
        pygame.draw.rect(
            surface,
            self.COLOR_GOLD_DARK,
            (sp_x + 5, sp_y + 5, sp_w - 10, sp_h - 10),
            1
        )

        # Corner Filigree Accents
        self._render_filigree(surface, sp_x + 8, sp_y + 8)
        self._render_filigree(surface, sp_x + sp_w - 8, sp_y + 8, flip_x=True)
        self._render_filigree(surface, sp_x + 8, sp_y + sp_h - 8, flip_y=True)
        self._render_filigree(surface, sp_x + sp_w - 8, sp_y + sp_h - 8, flip_x=True, flip_y=True)

        # Decorative Heavy Door Hinges (Right side)
        pygame.draw.rect(surface, self.COLOR_STEEL_DARK, (sp_x + sp_w - 3, sp_y + 30, 7, 24), border_radius=2)
        pygame.draw.rect(surface, self.COLOR_GOLD_DARK, (sp_x + sp_w - 2, sp_y + 32, 5, 20), border_radius=1)
        pygame.draw.rect(surface, self.COLOR_STEEL_DARK, (sp_x + sp_w - 3, sp_y + sp_h - 54, 7, 24), border_radius=2)
        pygame.draw.rect(surface, self.COLOR_GOLD_DARK, (sp_x + sp_w - 2, sp_y + sp_h - 52, 5, 20), border_radius=1)

        # 2. Central Metallic Dial Assembly
        center = (settings.VIRTUAL_WIDTH // 2, 102)
        
        # Outer Bezel & Brass Rings
        pygame.draw.circle(surface, self.COLOR_STEEL_DARK, center, 68)
        pygame.draw.circle(surface, self.COLOR_GOLD_DARK, center, 65)
        pygame.draw.circle(surface, (18, 19, 21), center, 61)
        pygame.draw.circle(surface, self.COLOR_GOLD, center, 56, 1)

        # Brass Tick Marks
        for number in range(0, 100, 5):
            angle = math.radians(number * 3.6 - 90)
            inner = 48 if number % 10 else 43
            outer = 54
            start = (center[0] + math.cos(angle) * inner, center[1] + math.sin(angle) * inner)
            end = (center[0] + math.cos(angle) * outer, center[1] + math.sin(angle) * outer)
            pygame.draw.line(surface, self.COLOR_GOLD, start, end, 2 if number % 10 == 0 else 1)

        # Dial Center Knob & Pointer Needle
        needle_angle = math.radians(self.dial - 90)
        needle_length = 49 + (3 if self.stutter_time > 0 else 0)
        needle = (center[0] + math.cos(needle_angle) * needle_length, center[1] + math.sin(needle_angle) * needle_length)
        pygame.draw.line(surface, self.COLOR_GOLD, center, needle, 2)
        pygame.draw.circle(surface, self.COLOR_GOLD, center, 10)
        pygame.draw.circle(surface, self.COLOR_GOLD_DARK, center, 10, 1)
        pygame.draw.circle(surface, self.COLOR_STEEL_DARK, center, 4)

        # Top Center Fixed Indicator Arrow
        indicator_pts = [
            (center[0], center[1] - 62),
            (center[0] - 4, center[1] - 68),
            (center[0] + 4, center[1] - 68)
        ]
        pygame.draw.polygon(surface, self.COLOR_GOLD, indicator_pts)

        # 3. Separate Panels & Labels
        self.dial_box_panel.render(surface)
        self.inst_panel.render(surface)

        self.lbl_title.render(surface)
        self.lbl_tumbler.render(surface)
        self.lbl_dial_val.render(surface)
        self.lbl_message.render(surface)
        self.lbl_stress.render(surface)
        self.lbl_timer.render(surface)
        self.lbl_controls.render(surface)

        # 4. Stress Meter Bar (Aligned under ESTRÉS label on the right)
        stress = 0.0 if self.complete else min(1.0, max(0.0, (5.0 - self._target_distance()) / 5.0))
        if self.overshot:
            stress = 1.0
        
        bar_x = sp_x + sp_w - 108
        bar_y = sp_y + 26
        pygame.draw.rect(surface, (38, 32, 28), (bar_x, bar_y, 90, 7), border_radius=1)
        if stress > 0:
            bar_color = COLOR_ACCENT_RED if stress > 0.8 else self.COLOR_GOLD
            pygame.draw.rect(surface, bar_color, (bar_x, bar_y, int(90 * stress), 7), border_radius=1)
        pygame.draw.rect(surface, self.COLOR_GOLD_DARK, (bar_x, bar_y, 90, 7), 1, border_radius=1)

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "quit" and input_data.pressed:
            self.quit()
        elif input_id == "move_left":
            self.turning = -1 if not input_data.released else 0
        elif input_id == "move_right":
            self.turning = 1 if not input_data.released else 0
        elif input_id == "fine":
            self.fine_control = not input_data.released
        elif input_id in ("space", "enter") and input_data.pressed:
            self._confirm()