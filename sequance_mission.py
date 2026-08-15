# sequance_mission.py
import random
import pygame
import configs
from particles import Particle
from missions_controller import BaseMission

class SequenceMission(BaseMission):
    KEY_MAP = {
        pygame.K_UP: "UP",
        pygame.K_DOWN: "DOWN",
        pygame.K_LEFT: "LEFT",
        pygame.K_RIGHT: "RIGHT",
    }
    DIRECTIONS = ["UP", "DOWN", "LEFT", "RIGHT"]

    def __init__(self):
        self.font_title = pygame.font.SysFont("monospace", 24, bold=True)
        self.font_sub = pygame.font.SysFont("monospace", 15, bold=False)
        self.font_key = pygame.font.SysFont("monospace", 17, bold=True)
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
                    particles_list.append(Particle(ring.x, 165, configs.ORB_GREEN["main"]))
                self.generate_sequence()
        else:
            self.step = 0
            trigger_shake(6.0)
            sfx.play(freq=130, duration=0.15, wave_type="square", vol=0.22)
            for _ in range(10):
                particles_list.append(Particle(ring.x, 165, configs.ORB_RED["main"]))

    def draw(self, surface, ring, time_sec, active_palette):
        title = self.font_title.render("SECURITY OVERRIDE", True, configs.COLOR_TEXT_BRIGHT)
        surface.blit(title, title.get_rect(center=(ring.x, 75)))

        sub = self.font_sub.render("PRESS ARROW KEYS IN SEQUENCE", True, (135, 150, 175))
        surface.blit(sub, sub.get_rect(center=(ring.x, 115)))

        box_w, box_h, gap = 70, 38, 12
        total_w = 4 * box_w + 3 * gap
        start_x = ring.x - (total_w // 2)

        for i, dir_name in enumerate(self.sequence):
            bx = start_x + i * (box_w + gap)
            by = 150
            box_rect = pygame.Rect(bx, by, box_w, box_h)

            if i < self.step:
                bg_col = configs.ORB_GREEN["deep"]
                border_col = configs.ORB_GREEN["main"]
                txt_col = (255, 255, 255)
            elif i == self.step:
                bg_col = configs.COLOR_TRACK
                border_col = active_palette["main"]
                txt_col = configs.COLOR_TEXT_BRIGHT
            else:
                bg_col = configs.COLOR_TRACK
                border_col = (50, 55, 70)
                txt_col = (90, 100, 120)

            pygame.draw.rect(surface, bg_col, box_rect, border_radius=6)
            pygame.draw.rect(surface, border_col, box_rect, 2 if i == self.step else 1, border_radius=6)
            key_surf = self.font_key.render(dir_name, True, txt_col)
            surface.blit(key_surf, key_surf.get_rect(center=box_rect.center))