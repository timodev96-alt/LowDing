# Timo_slack_mission.py
import os
import pygame
import configs
from particles import Particle
from missions_controller import BaseMission

class TimoMission(BaseMission):
    CORRECT_ID = "U0B6FDN1542"

    def __init__(self):
        self.font_title = pygame.font.SysFont("monospace", 24, bold=True)
        self.font_hint = pygame.font.SysFont("monospace", 15, bold=False)
        self.font_input = pygame.font.SysFont("monospace", 22, bold=True)
        self.user_input = ""
        self.avatar = None
        self.load_image()

    def load_image(self):
        path = os.path.join("photos", "timo.png")
        try:
            if os.path.exists(path):
                raw = pygame.image.load(path).convert_alpha()
                size = 210
                scaled = pygame.transform.smoothscale(raw, (size, size))
                mask = pygame.Surface((size, size), pygame.SRCALPHA)
                pygame.draw.circle(mask, (255, 255, 255, 255), (size // 2, size // 2), size // 2)
                self.avatar = mask.copy()
                self.avatar.blit(scaled, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        except Exception:
            self.avatar = None

    def on_start(self):
        self.user_input = ""

    def handle_event(self, event, ring, sfx, particles_list, trigger_shake):
        if event.type != pygame.KEYDOWN:
            return

        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            if self.user_input.strip().upper() == self.CORRECT_ID:
                ring.progress = 100.0
                sfx.play(freq=820, duration=0.25, vol=0.35)
                for _ in range(30):
                    particles_list.append(Particle(ring.x, ring.y, configs.ORB_GREEN["main"]))
                self.user_input = ""
            else:
                trigger_shake(8.0)
                sfx.play(freq=130, duration=0.18, wave_type="square", vol=0.25)
                for _ in range(12):
                    particles_list.append(Particle(ring.x, 165, configs.ORB_RED["main"]))
                self.user_input = ""
        elif event.key == pygame.K_BACKSPACE:
            self.user_input = self.user_input[:-1]
        elif len(self.user_input) < 18 and (event.unicode.isalnum() or event.unicode in "_-"):
            self.user_input += event.unicode.upper()

    def draw(self, surface, ring, time_sec, active_palette):
        if self.avatar:
            avatar_rect = self.avatar.get_rect(center=(ring.x, ring.y))
            surface.blit(self.avatar, avatar_rect)

        q_surf = self.font_title.render("What is Timo's slack id?", True, configs.COLOR_TEXT_BRIGHT)
        surface.blit(q_surf, q_surf.get_rect(center=(ring.x, 75)))

        h_surf = self.font_hint.render("hint: Go to #what_is_my_slack_id and mention me (@Timo)", True, (140, 160, 185))
        surface.blit(h_surf, h_surf.get_rect(center=(ring.x, 115)))

        input_box = pygame.Rect(ring.x - 120, 148, 240, 38)
        pygame.draw.rect(surface, configs.COLOR_TRACK, input_box, border_radius=8)
        pygame.draw.rect(surface, active_palette["main"], input_box, 2, border_radius=8)

        txt = self.user_input if self.user_input else "ENTER ID..."
        txt_col = configs.COLOR_TEXT_BRIGHT if self.user_input else (100, 110, 130)
        inp_surf = self.font_input.render(txt, True, txt_col)
        surface.blit(inp_surf, inp_surf.get_rect(center=input_box.center))