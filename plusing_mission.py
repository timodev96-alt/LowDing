import random
import pygame
import configs
from missions_controller import BaseMission
from particles import Particle

class MathMission(BaseMission):
    def __init__(self):
        self.font_math = pygame.font.SysFont("monospace", 28, bold=True)
        self.font_sub = pygame.font.SysFont("monospace", 15, bold=True)
        self.math_problem = ""
        self.math_answer = 0
        self.user_input = ""

    def on_start(self):
        self.generate_problem()

    def generate_problem(self):
        op = random.choice(["+", "-"])
        if op == "+":
            a = random.randint(2, 20)
            b = random.randint(2, 20)
            self.math_answer = a + b
        else:
            a = random.randint(5, 30)
            b = random.randint(1, a)
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
                    for _ in range(18):
                        particles_list.append(Particle(ring.x, ring.y - 150, configs.ORB_GREEN["main"]))
                    self.generate_problem()
                else:
                    ring.progress = max(0.0, ring.progress - 10)
                    trigger_shake(8.0)
                    sfx.play(freq=130, duration=0.18, wave_type="square", vol=0.25)
                    for _ in range(12):
                        particles_list.append(Particle(ring.x, ring.y - 150, configs.ORB_RED["main"]))
                    self.user_input = ""
            except ValueError:
                self.user_input = ""
        elif event.key == pygame.K_BACKSPACE:
            self.user_input = self.user_input[:-1]
        elif event.unicode.isdigit() and len(self.user_input) < 5:
            self.user_input += event.unicode

    def draw(self, surface, ring, time_sec, active_palette):
        hint = self.font_sub.render("TYPE ANSWER & PRESS ENTER", True, (130, 145, 165))
        surface.blit(hint, hint.get_rect(center=(ring.x, ring.y - 200)))

        prob = self.font_math.render(self.math_problem, True, configs.COLOR_TEXT_BRIGHT)
        surface.blit(prob, prob.get_rect(center=(ring.x, ring.y - 170)))

        input_box = pygame.Rect(ring.x - 60, ring.y - 145, 120, 32)
        pygame.draw.rect(surface, configs.COLOR_TRACK, input_box, border_radius=6)
        pygame.draw.rect(surface, active_palette["main"], input_box, 2, border_radius=6)

        txt = self.user_input if self.user_input else "_"
        inp = self.font_math.render(txt, True, configs.COLOR_TEXT_BRIGHT)
        surface.blit(inp, inp.get_rect(center=input_box.center))
