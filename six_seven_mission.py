# six_seven_mission.py
import math
import pygame
import configs
from particles import Particle
from missions_controller import BaseMission

class SixSevenMission(BaseMission):
    def __init__(self):
        self.font_title = pygame.font.SysFont("monospace", 24, bold=True)
        self.font_sub = pygame.font.SysFont("monospace", 15, bold=False)
        self.font_card = pygame.font.SysFont("monospace", 22, bold=True)  # Scaled to fit cleanly inside boxes
        self.state = 0

    def on_start(self):
        self.state = 0

    def handle_event(self, event, ring, sfx, particles_list, trigger_shake):
        if event.type != pygame.KEYDOWN:
            return

        is_6 = event.key in (pygame.K_6, pygame.K_KP6) or event.unicode == '6'
        is_7 = event.key in (pygame.K_7, pygame.K_KP7) or event.unicode == '7'

        if self.state == 0:
            if is_6:
                self.state = 1
                sfx.play(freq=500, duration=0.10, vol=0.3)
                for _ in range(10):
                    particles_list.append(Particle(ring.x - 92, 160, configs.ORB_GREEN["main"]))
            elif is_7:
                trigger_shake(5.0)
                sfx.play(freq=150, duration=0.12, wave_type="square", vol=0.2)
        elif self.state == 1:
            if is_7:
                self.state = 0
                ring.progress = min(100.0, ring.progress + 20.0)
                sfx.play(freq=750, duration=0.18, vol=0.35)
                trigger_shake(12.0)
                for _ in range(24):
                    particles_list.append(Particle(ring.x + 92, 160, configs.ORB_GREEN["main"]))
            elif is_6:
                self.state = 1
                sfx.play(freq=500, duration=0.10, vol=0.3)

    def draw(self, surface, ring, time_sec, active_palette):
        sway = math.sin(time_sec * 3.5) * 3.5

        title = self.font_title.render("RESONANCE CHANT", True, configs.COLOR_TEXT_BRIGHT)
        surface.blit(title, title.get_rect(center=(ring.x, 75)))

        sub = self.font_sub.render("PRESS 6 THEN 7 TO BUILD CHARGE", True, (135, 150, 175))
        surface.blit(sub, sub.get_rect(center=(ring.x, 115)))

        card_w, card_h = 145, 44

        card_6_rect = pygame.Rect(ring.x - card_w - 20, int(150 + sway), card_w, card_h)
        col_6 = configs.ORB_GREEN["deep"] if self.state == 1 else configs.COLOR_TRACK
        b_col_6 = configs.ORB_GREEN["main"] if self.state == 1 else active_palette["main"]
        pygame.draw.rect(surface, col_6, card_6_rect, border_radius=8)
        pygame.draw.rect(surface, b_col_6, card_6_rect, 2, border_radius=8)
        txt_6 = self.font_card.render("SIX [6]", True, configs.COLOR_TEXT_BRIGHT)
        surface.blit(txt_6, txt_6.get_rect(center=card_6_rect.center))

        card_7_rect = pygame.Rect(ring.x + 20, int(150 - sway), card_w, card_h)
        col_7 = configs.COLOR_TRACK
        b_col_7 = active_palette["main"] if self.state == 1 else (55, 60, 75)
        pygame.draw.rect(surface, col_7, card_7_rect, border_radius=8)
        pygame.draw.rect(surface, b_col_7, card_7_rect, 2 if self.state == 1 else 1, border_radius=8)
        txt_7 = self.font_card.render("SEVEN [7]", True, configs.COLOR_TEXT_BRIGHT if self.state == 1 else (95, 105, 125))
        surface.blit(txt_7, txt_7.get_rect(center=card_7_rect.center))