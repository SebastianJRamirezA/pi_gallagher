"""A deliberately quiet, audio-visual combination safe game."""

import array
import math
import random

import pygame

from gale.game import Game
from gale.input_handler import InputData
from gale.text import render_text
from gale.timer import Timer
from gale.state import BaseState

import settings


class SafeCrackerState(BaseState):
    def enter(self) -> None:
        self.dial = 0.0
        self.stage = 0
        self.turning = 0
        self.fine_control = False
        self.overshot = False
        self.stutter_time = 0.0
        self.click_number = -1
        self.message = "Listen for the lock. Set the first number."
        self.complete = False
        self.click_sound = self._make_tone(170)
        self.heavy_click_sound = self._make_tone(105)
        self.confirm_sound = self._make_tone(310, 0.14)
        self.alarm_sound = self._make_tone(62, 0.28)

        self.timer = 60.0

        self.COLOR_BACKGROUND = (18, 20, 24)
        self.COLOR_PANEL = (31, 33, 38)
        self.COLOR_BRASS = (190, 147, 73)
        self.COLOR_STEEL = (116, 124, 132)
        self.COLOR_TEXT = (218, 214, 198)
        self.COLOR_MUTED = (119, 125, 130)
        self.COLOR_DANGER = (196, 72, 57)
        self.COLOR_SUCCESS = (105, 173, 116)

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
                self.message = "Too far. Complete the turn to reset this number."
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
            self.message = "Reset. Approach the number more carefully."

        if self.timer <= 0:
            Timer.clear()

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
                self.message = "The tumblers fall. The safe is open."
                self.state_machine.pop()
            else:
                self.dial = 0.0
                self.click_number = -1
                self.message = "Good. The next tumbler is listening."
        else:
            self.message = "That is not the number. Move closer and listen."

    def _reactivate_door(self) -> None:
        door = getattr(self, "door", None)
        if door is not None and hasattr(door, "active"):
            door.active = True

    def render(self, surface: pygame.Surface) -> None:
        surface.fill(self.COLOR_BACKGROUND)
        center = (settings.VIRTUAL_WIDTH // 2, 134)
        pygame.draw.rect(surface, self.COLOR_PANEL, (26, 20, 428, 230), border_radius=4)
        pygame.draw.circle(surface, (67, 64, 58), center, 91)
        pygame.draw.circle(surface, (29, 30, 33), center, 82)
        pygame.draw.circle(surface, self.COLOR_STEEL, center, 75, 2)

        for number in range(0, 100, 5):
            angle = math.radians(number * 3.6 - 90)
            inner = 66 if number % 10 else 61
            outer = 72
            start = (center[0] + math.cos(angle) * inner, center[1] + math.sin(angle) * inner)
            end = (center[0] + math.cos(angle) * outer, center[1] + math.sin(angle) * outer)
            pygame.draw.line(surface, self.COLOR_BRASS, start, end, 2 if number % 10 == 0 else 1)

        needle_angle = math.radians(self.dial - 90)
        needle_length = 65 + (4 if self.stutter_time > 0 else 0)
        needle = (center[0] + math.cos(needle_angle) * needle_length, center[1] + math.sin(needle_angle) * needle_length)
        pygame.draw.line(surface, self.COLOR_BRASS, center, needle, 3)
        pygame.draw.circle(surface, self.COLOR_BRASS, center, 7)

        render_text(surface, "THE QUIET DIAL", settings.FONTS["large"], 30, 32, self.COLOR_TEXT)
        render_text(surface, f"TUMBLER  {min(self.stage + 1, 3)} / 3", settings.FONTS["small"], 30, 72, self.COLOR_MUTED)
        render_text(surface, f"{self._dial_number():02d}", settings.FONTS["medium"], center[0], 224, self.COLOR_TEXT, center=True)
        render_text(surface, self.message, settings.FONTS["small"], 30, 238, self.COLOR_DANGER if self.overshot else self.COLOR_TEXT)

        stress = 0.0 if self.complete else min(1.0, max(0.0, (5.0 - self._target_distance()) / 5.0))
        if self.overshot:
            stress = 1.0
        pygame.draw.rect(surface, (53, 50, 48), (345, 72, 92, 9))
        pygame.draw.rect(surface, self.COLOR_DANGER if stress > 0.8 else self.COLOR_BRASS, (345, 72, int(92 * stress), 9))
        render_text(surface, "STRESS", settings.FONTS["small"], 345, 55, self.COLOR_MUTED)

        render_text(surface, "TIME: " + str(self.timer), settings.FONTS["small"], 345, 105, self.COLOR_MUTED)

        render_text(surface, "A/D or arrows  rotate     SHIFT  fine     SPACE  set", settings.FONTS["small"], 30, 260, self.COLOR_MUTED)

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "quit" and input_data.pressed:
            self.quit()
        elif input_id in ("rotate_left", "move_left"):
            self.turning = -1 if not input_data.released else 0
        elif input_id in ("rotate_right", "move_right"):
            self.turning = 1 if not input_data.released else 0
        elif input_id == "fine":
            self.fine_control = not input_data.released
        elif input_id == "confirm" and input_data.pressed:
            self._confirm()