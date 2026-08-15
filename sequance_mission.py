import os
import json
import math
import random
import datetime
import threading
import urllib.request
import pygame
import configs
import missions
from particles import Particle

class SequenceMission(missions.BaseMission):
    KEY_MAP = {
        pygame.K_UP: "UP",
        pygame.K_DOWN: "DOWN",
        pygame.K_LEFT: "LEFT",
        pygame.K_RIGHT: "RIGHT",
    }
    DIRECTIONS = ["UP", "DOWN", "LEFT", "RIGHT"]

    def __init__(self):
        self.font_key = pygame.font.SysFont("monospace", 16, bold=True)
        self.font_sub = pygame.font.SysFont("monospace", 15, bold=True)
        self.sequence = []
        self.step = 0

    def on_start(self):
        self.generate_sequence()

    def generate_sequence(self):
        self.sequence = [random.choice(self.DIRECTIONS) for _ in range(4)]
        self.step = 0

    def handle_event(self, event, ring, sfx, particles_list, trigger_shake):
        if event.type != pygame.KEYDOWN or event.key not in self.KEY_MAP:
            return

        pressed = self.KEY_MAP[event.key]
        if pressed == self.sequence[self.step]:
            self.step += 1
            sfx.play(freq=480 + self.step * 70, duration=0.08, vol=0.25)

            if self.step >= len(self.sequence):
                ring.progress = min(100.0, ring.progress + 25.0)
                sfx.play(freq=780, duration=0.15, vol=0.3)
                for _ in range(20):
                    particles_list.append(Particle(ring.x, ring.y - 170, configs.ORB_GREEN["main"]))
                self.generate_sequence()
        else:
            self.step = 0
            trigger_shake(6.0)
            sfx.play(freq=130, duration=0.15, wave_type="square", vol=0.22)
            for _ in range(10):
                particles_list.append(Particle(ring.x, ring.y - 170, configs.ORB_RED["main"]))

    def draw(self, surface, ring, time_sec, active_palette):
        hint = self.font_sub.render("PRESS ARROW KEYS IN ORDER", True, (130, 145, 165))
        surface.blit(hint, hint.get_rect(center=(ring.x, ring.y - 200)))

        total_width = 4 * 65
        start_x = ring.x - (total_width // 2)

        for i, dir_name in enumerate(self.sequence):
            bx = start_x + i * 65
            by = ring.y - 170
            box_rect = pygame.Rect(bx, by, 58, 34)

            if i < self.step:
                bg_col = configs.ORB_GREEN["deep"]
                border_col = configs.ORB_GREEN["main"]
            elif i == self.step:
                bg_col = configs.COLOR_TRACK
                border_col = active_palette["main"]
            else:
                bg_col = configs.COLOR_TRACK
                border_col = (50, 55, 70)

            pygame.draw.rect(surface, bg_col, box_rect, border_radius=6)
            pygame.draw.rect(surface, border_col, box_rect, 2 if i != self.step else 3, border_radius=6)

            txt_col = configs.COLOR_TEXT_BRIGHT if i <= self.step else (100, 110, 130)
            key_surf = self.font_key.render(dir_name, True, txt_col)
            surface.blit(key_surf, key_surf.get_rect(center=box_rect.center))
