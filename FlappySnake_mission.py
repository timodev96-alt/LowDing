# flappy_mission.py
import os
import json
import webbrowser
import pygame
import configs
from particles import Particle
from missions_controller import BaseMission

class FlappySnakeMission(BaseMission):
    GITHUB_URL = "https://github.com/timodev96-alt/Flappy-Snake/releases/tag/Main"
    TARGET_SCORE = 1000

    def __init__(self):
        self.font_title = pygame.font.SysFont("monospace", 24, bold=True)
        self.font_btn = pygame.font.SysFont("monospace", 14, bold=True)
        self.font_score = pygame.font.SysFont("monospace", 17, bold=True)
        
        self.github_btn_rect = pygame.Rect(0, 0, 260, 34)
        self.pass_btn_rect = pygame.Rect(0, 0, 280, 38)
        
        self.high_score = 0
        self.file_found = False
        self.check_timer = 0.0

    def get_save_paths(self):
        local_appdata = os.environ.get("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local"))
        folder = os.path.join(local_appdata, "FlappySnake")
        return [
            os.path.join(folder, "save_data"),
            os.path.join(folder, "save_data.json"),
            os.path.join(folder, "save.json"),
            os.path.join(folder, "savedata.json")
        ]

    def read_save_data(self):
        for path in self.get_save_paths():
            if os.path.exists(path):
                self.file_found = True
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        score = data.get("high_score", data.get("highscore", data.get("score", 0)))
                        return int(score)
                except Exception:
                    pass
        self.file_found = False
        return 0

    def on_start(self):
        self.high_score = self.read_save_data()
        self.check_timer = 0.0

    def update(self, dt, ring):
        self.check_timer += dt
        if self.check_timer >= 0.4:
            self.check_timer = 0.0
            self.high_score = self.read_save_data()
            if self.high_score < self.TARGET_SCORE:
                target_pct = min(99.0, max(0.0, (self.high_score / self.TARGET_SCORE) * 100.0))
                ring.progress = max(ring.progress, target_pct)

    def trigger_pass(self, ring, sfx, particles_list):
        ring.progress = 100.0
        sfx.play(freq=880, duration=0.25, vol=0.35)
        for _ in range(35):
            particles_list.append(Particle(ring.x, ring.y, configs.ORB_GREEN["main"]))

    def handle_event(self, event, ring, sfx, particles_list, trigger_shake):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.github_btn_rect.collidepoint(event.pos):
                webbrowser.open(self.GITHUB_URL)
                sfx.play(freq=600, duration=0.1, vol=0.25)
            elif self.pass_btn_rect.collidepoint(event.pos):
                if self.high_score >= self.TARGET_SCORE:
                    self.trigger_pass(ring, sfx, particles_list)
                else:
                    trigger_shake(6.0)
                    sfx.play(freq=140, duration=0.15, wave_type="square", vol=0.2)
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_g, pygame.K_o):
                webbrowser.open(self.GITHUB_URL)
                sfx.play(freq=600, duration=0.1, vol=0.25)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                if self.high_score >= self.TARGET_SCORE:
                    self.trigger_pass(ring, sfx, particles_list)

    def draw(self, surface, ring, time_sec, active_palette):
        title = self.font_title.render("Download my game FlappySnake and get a 1000 Highscore!", True, configs.COLOR_TEXT_BRIGHT)
        surface.blit(title, title.get_rect(center=(ring.x, 70)))

        self.github_btn_rect.center = (ring.x, 112)
        gh_hover = self.github_btn_rect.collidepoint(pygame.mouse.get_pos())
        gh_bg = configs.COLOR_TRACK if not gh_hover else (35, 42, 58)
        pygame.draw.rect(surface, gh_bg, self.github_btn_rect, border_radius=6)
        pygame.draw.rect(surface, (80, 90, 115), self.github_btn_rect, 1, border_radius=6)
        gh_txt = self.font_btn.render(" OPEN GITHUB DOWNLOAD", True, (175, 195, 220))
        surface.blit(gh_txt, gh_txt.get_rect(center=self.github_btn_rect.center))

        if self.file_found:
            score_txt = f"HIGH SCORE: {self.high_score} / {self.TARGET_SCORE}"
            score_col = configs.ORB_GREEN["main"] if self.high_score >= self.TARGET_SCORE else configs.COLOR_TEXT_BRIGHT
        else:
            score_txt = "WAITING FOR FLAPPY SNAKE SAVE DATA..."
            score_col = (180, 140, 100)

        score_surf = self.font_score.render(score_txt, True, score_col)
        surface.blit(score_surf, score_surf.get_rect(center=(ring.x, 150)))

        self.pass_btn_rect.center = (ring.x, 186)
        has_passed = (self.high_score >= self.TARGET_SCORE)
        pass_hover = self.pass_btn_rect.collidepoint(pygame.mouse.get_pos())

        if has_passed:
            btn_bg = configs.ORB_GREEN["deep"] if not pass_hover else (30, 160, 95)
            btn_border = configs.ORB_GREEN["main"]
            txt_label = "CLAIM & PASS (ENTER)"
            txt_col = (255, 255, 255)
        else:
            btn_bg = configs.COLOR_TRACK
            btn_border = (60, 65, 80)
            txt_label = "REACH 1000 TO PASS"
            txt_col = (100, 110, 130)

        pygame.draw.rect(surface, btn_bg, self.pass_btn_rect, border_radius=7)
        pygame.draw.rect(surface, btn_border, self.pass_btn_rect, 2 if has_passed else 1, border_radius=7)
        pass_surf = self.font_btn.render(txt_label, True, txt_col)
        surface.blit(pass_surf, pass_surf.get_rect(center=self.pass_btn_rect.center))