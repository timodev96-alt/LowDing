# plusing_mission.py
import random
import pygame
import configs
from particles import Particle
from missions_controller import BaseMission

class MathMission(BaseMission):
    def __init__(self):
        self.font_title = pygame.font.SysFont("monospace", 24, bold=True)
        self.font_sub = pygame.font.SysFont("monospace", 15, bold=False)
        self.font_math = pygame.font.SysFont("monospace", 32, bold=True)
        self.font_input = pygame.font.SysFont("monospace", 26, bold=True)
        
        self.math_problem = ""
        self.math_answer = 0
        self.user_input = ""

    def on_start(self):
        self.generate_problem()

    def generate_problem(self):
        op = random.choice(["+", "-"])
        if op == "+":
            a = random.randint(3, 25)
            b = random.randint(3, 25)
            self.math_answer = a + b
        else:
            a = random.randint(8, 35)
            b = random.randint(2, a)
            self.math_answer = a - b
        self.math_problem = f"{a} {op} {b} = ?"
        self.user_input = ""

    def handle_event(self, event, ring, sfx, particles_list, trigger_shake):
        if event.type != pygame.KEYDOWN:
            return

        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            if not self.user_input.strip():
                return
            try:
                if int(self.user_input) == self.math_answer:
                    ring.progress = min(100.0, ring.progress + random.randint(22, 26))
                    sfx.play(freq=620, duration=0.15, vol=0.3)
                    for _ in range(20):
                        particles_list.append(Particle(ring.x, 168, configs.ORB_GREEN["main"]))
                    self.generate_problem()
                else:
                    ring.progress = max(0.0, ring.progress - 10)
                    trigger_shake(8.0)
                    sfx.play(freq=130, duration=0.18, wave_type="square", vol=0.25)
                    for _ in range(12):
                        particles_list.append(Particle(ring.x, 168, configs.ORB_RED["main"]))
                    self.user_input = ""
            except ValueError:
                self.user_input = ""
        elif event.key == pygame.K_BACKSPACE:
            self.user_input = self.user_input[:-1]
        elif event.unicode.isdigit() and len(self.user_input) < 5:
            self.user_input += event.unicode

    def draw(self, surface, ring, time_sec, active_palette):
        title = self.font_title.render("SYSTEM CALCULATION", True, configs.COLOR_TEXT_BRIGHT)
        surface.blit(title, title.get_rect(center=(ring.x, 75)))

        prob = self.font_math.render(self.math_problem, True, active_palette["main"])
        surface.blit(prob, prob.get_rect(center=(ring.x, 118)))

        input_box = pygame.Rect(ring.x - 70, 150, 140, 38)
        pygame.draw.rect(surface, configs.COLOR_TRACK, input_box, border_radius=8)
        pygame.draw.rect(surface, active_palette["main"], input_box, 2, border_radius=8)

        txt = self.user_input if self.user_input else "_"
        inp = self.font_input.render(txt, True, configs.COLOR_TEXT_BRIGHT)
        surface.blit(inp, inp.get_rect(center=input_box.center))