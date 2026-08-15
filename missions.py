import os
import json
import math
import random
import datetime
import threading
import urllib.request
import pygame
import configs
from particles import Particle

# ==========================================
# BASE MISSION CLASS
# ==========================================
class BaseMission:
    def on_start(self):
        pass

    def update(self, dt, ring):
        pass

    def handle_event(self, event, ring, sfx, particles_list, trigger_shake):
        pass

    def draw(self, surface, ring, time_sec, active_palette):
        pass


# ==========================================
# LEVEL 1: ORB TIMING MISSION
# ==========================================
class SyncNode:
    def __init__(self, angle, is_green=True):
        self.angle = angle % 360.0
        self.is_green = is_green
        self.palette = configs.ORB_GREEN if is_green else configs.ORB_RED
        self.value = random.randint(19, 23)

    def get_pos(self, cx, cy, radius):
        rad = math.radians(self.angle - 90.0)
        return int(cx + math.cos(rad) * radius), int(cy + math.sin(rad) * radius)

    def draw(self, surface, cx, cy, radius):
        px, py = self.get_pos(cx, cy, radius)
        pygame.draw.circle(surface, self.palette["main"], (px, py), 8)
        pygame.draw.circle(surface, self.palette["deep"], (px, py), 5)


class OrbMission(BaseMission):
    def __init__(self):
        self.nodes = []
        self.spawn_timer = 0.0

    def on_start(self):
        self.nodes.clear()
        self.spawn_timer = 0.0

    def update(self, dt, ring):
        self.spawn_timer += dt
        if self.spawn_timer >= 0.85:
            self.spawn_timer = 0.0
            if len(self.nodes) < 5:
                is_green = random.random() < 0.70
                self.nodes.append(SyncNode(random.uniform(0, 360), is_green))

    def handle_event(self, event, ring, sfx, particles_list, trigger_shake):
        is_action = (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE) or \
                    (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1)
        if not is_action:
            return

        hit_idx = -1
        for i, n in enumerate(self.nodes):
            diff = abs(n.angle - ring.scanner_angle)
            if min(diff, 360.0 - diff) <= 22.0:
                hit_idx = i
                break

        if hit_idx != -1:
            node = self.nodes.pop(hit_idx)
            nx, ny = node.get_pos(ring.x, ring.y, ring.base_radius)
            if node.is_green:
                ring.progress = min(100.0, ring.progress + node.value)
                sfx.play(freq=580, duration=0.12, vol=0.25)
                for _ in range(14):
                    particles_list.append(Particle(nx, ny, configs.ORB_GREEN["main"]))
            else:
                ring.progress = max(0.0, ring.progress - node.value)
                trigger_shake(10.0)
                sfx.play(freq=140, duration=0.15, wave_type="square", vol=0.22)
                for _ in range(14):
                    particles_list.append(Particle(nx, ny, configs.ORB_RED["main"]))
        else:
            sfx.play(freq=240, duration=0.05, vol=0.10)

    def draw(self, surface, ring, time_sec, active_palette):
        pulse = math.sin(time_sec * 2.5) * 1.5
        current_r = ring.base_radius + pulse
        for node in self.nodes:
            node.draw(surface, ring.x, ring.y, current_r)


# ==========================================
# LEVEL 2: MATH PROBLEM MISSION
# ==========================================
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


# ==========================================
# LEVEL 3: ARROW KEY SEQUENCE MISSION
# ==========================================
class SequenceMission(BaseMission):
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


# ==========================================
# LEVEL 4: SIX SEVEN CHANT MISSION
# ==========================================
class SixSevenMission(BaseMission):
    def __init__(self):
        self.font_big = pygame.font.SysFont("monospace", 32, bold=True)
        self.font_sub = pygame.font.SysFont("monospace", 15, bold=True)
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
                for _ in range(8):
                    particles_list.append(Particle(ring.x - 85, ring.y - 165, configs.ORB_GREEN["main"]))
            elif is_7:
                trigger_shake(5.0)
                sfx.play(freq=150, duration=0.12, wave_type="square", vol=0.2)
        elif self.state == 1:
            if is_7:
                self.state = 0
                ring.progress = min(100.0, ring.progress + 20.0)
                sfx.play(freq=750, duration=0.18, vol=0.35)
                trigger_shake(12.0)
                for _ in range(22):
                    particles_list.append(Particle(ring.x + 85, ring.y - 165, configs.ORB_GREEN["main"]))
            elif is_6:
                self.state = 1
                sfx.play(freq=500, duration=0.10, vol=0.3)

    def draw(self, surface, ring, time_sec, active_palette):
        sway = math.sin(time_sec * 4.0) * 4.0

        hint = self.font_sub.render("PRESS 6 THEN 7 (REPEAT)", True, (130, 145, 165))
        surface.blit(hint, hint.get_rect(center=(ring.x, ring.y - 210)))

        # Card 6
        card_6_rect = pygame.Rect(ring.x - 135, int(ring.y - 180 + sway), 100, 42)
        col_6 = configs.ORB_GREEN["deep"] if self.state == 1 else configs.COLOR_TRACK
        b_col_6 = configs.ORB_GREEN["main"] if self.state == 1 else active_palette["main"]
        pygame.draw.rect(surface, col_6, card_6_rect, border_radius=8)
        pygame.draw.rect(surface, b_col_6, card_6_rect, 2, border_radius=8)
        txt_6 = self.font_big.render("SIX [6]", True, configs.COLOR_TEXT_BRIGHT)
        surface.blit(txt_6, txt_6.get_rect(center=card_6_rect.center))

        # Card 7
        card_7_rect = pygame.Rect(ring.x + 35, int(ring.y - 180 - sway), 100, 42)
        col_7 = configs.COLOR_TRACK
        b_col_7 = active_palette["main"] if self.state == 1 else (60, 65, 80)
        pygame.draw.rect(surface, col_7, card_7_rect, border_radius=8)
        pygame.draw.rect(surface, b_col_7, card_7_rect, 2 if self.state == 1 else 1, border_radius=8)
        txt_7 = self.font_big.render("SEVEN[7]", True, configs.COLOR_TEXT_BRIGHT if self.state == 1 else (100, 110, 130))
        surface.blit(txt_7, txt_7.get_rect(center=card_7_rect.center))


# ==========================================
# LEVEL 5: TIMO'S SLACK ID RIDDLE MISSION
# ==========================================
class TimoMission(BaseMission):
    CORRECT_ID = "U0B6FDN1542"

    def __init__(self):
        self.font_title = pygame.font.SysFont("monospace", 22, bold=True)
        self.font_hint = pygame.font.SysFont("monospace", 13, bold=False)
        self.font_input = pygame.font.SysFont("monospace", 20, bold=True)
        self.user_input = ""
        self.avatar = None
        self.load_image()

    def load_image(self):
        path = os.path.join("photos", "timo.png")
        try:
            if os.path.exists(path):
                raw = pygame.image.load(path).convert_alpha()
                size = 190
                scaled = pygame.transform.smoothscale(raw, (size, size))
                
                mask = pygame.Surface((size, size), pygame.SRCALPHA)
                pygame.draw.circle(mask, (255, 255, 255, 255), (size // 2, size // 2), size // 2)
                
                self.avatar = mask.copy()
                self.avatar.blit(scaled, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        except Exception as e:
            print(f"[TIMO MISSION] Could not load image: {e}")
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
                    particles_list.append(Particle(ring.x, ring.y - 145, configs.ORB_RED["main"]))
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
        surface.blit(q_surf, q_surf.get_rect(center=(ring.x, ring.y - 215)))

        h_surf = self.font_hint.render("hint: Go to #what_is_my_slack_id and mention me (@Timo)", True, (140, 160, 185))
        surface.blit(h_surf, h_surf.get_rect(center=(ring.x, ring.y - 190)))

        input_box = pygame.Rect(ring.x - 110, ring.y - 165, 220, 32)
        pygame.draw.rect(surface, configs.COLOR_TRACK, input_box, border_radius=6)
        pygame.draw.rect(surface, active_palette["main"], input_box, 2, border_radius=6)

        txt = self.user_input if self.user_input else "TYPE ID & ENTER"
        txt_col = configs.COLOR_TEXT_BRIGHT if self.user_input else (100, 110, 130)
        inp_surf = self.font_input.render(txt, True, txt_col)
        surface.blit(inp_surf, inp_surf.get_rect(center=input_box.center))

class WordleMission(BaseMission):
    COLOR_GREEN = (40, 205, 130)    # Correct spot
    COLOR_YELLOW = (230, 185, 45)   # Wrong spot
    COLOR_GRAY = (55, 60, 75)       # Not in word

    def __init__(self):
        self.font_title = pygame.font.SysFont("monospace", 22, bold=True)
        self.font_hint = pygame.font.SysFont("monospace", 13)
        self.font_tile = pygame.font.SysFont("monospace", 22, bold=True)
        self.today_word = "CRANE"  # Default fallback
        self.user_input = ""
        self.guesses = []
        self.fetch_live_global_wordle()

    def fetch_live_global_wordle(self):
        """Fetches the official live NYT Wordle answer for today in the background."""
        def fetcher():
            try:
                today_str = datetime.date.today().strftime("%Y-%m-%d")
                url = f"https://www.nytimes.com/svc/wordle/v2/{today_str}.json"
                req = urllib.request.Request(
                    url,
                    headers={"User-Agent": "Mozilla/5.0"}
                )
                with urllib.request.urlopen(req, timeout=3.5) as resp:
                    if resp.status == 200:
                        data = json.loads(resp.read().decode("utf-8"))
                        if "solution" in data:
                            self.today_word = data["solution"].upper()
                            print(f"[WORDLE LIVE] Today's global Wordle answer loaded successfully!")
            except Exception as e:
                print(f"[WORDLE LIVE] Offline or error fetching: {e} (Using fallback)")

        t = threading.Thread(target=fetcher, daemon=True)
        t.start()

    def on_start(self):
        self.user_input = ""
        self.guesses.clear()

    def evaluate_guess(self, guess):
        target = list(self.today_word)
        res = [self.COLOR_GRAY] * 5
        target_counts = {}

        # 1st pass: Greens
        for i in range(5):
            if guess[i] == target[i]:
                res[i] = self.COLOR_GREEN
            else:
                target_counts[target[i]] = target_counts.get(target[i], 0) + 1

        # 2nd pass: Yellows
        for i in range(5):
            if res[i] != self.COLOR_GREEN and guess[i] in target_counts and target_counts[guess[i]] > 0:
                res[i] = self.COLOR_YELLOW
                target_counts[guess[i]] -= 1

        return res

    def handle_event(self, event, ring, sfx, particles_list, trigger_shake):
        if event.type != pygame.KEYDOWN:
            return

        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            if len(self.user_input) == 5:
                guess = self.user_input.upper()
                colors = self.evaluate_guess(guess)
                self.guesses.append((guess, colors))
                if len(self.guesses) > 2:
                    self.guesses.pop(0)

                # Check if correct global answer
                if guess == self.today_word:
                    ring.progress = 100.0
                    sfx.play(freq=880, duration=0.30, vol=0.35)
                    for _ in range(35):
                        particles_list.append(Particle(ring.x, ring.y, self.COLOR_GREEN))
                else:
                    greens = colors.count(self.COLOR_GREEN)
                    yellows = colors.count(self.COLOR_YELLOW)
                    ring.progress = min(100.0, ring.progress + (greens * 8 + yellows * 3))

                    sfx.play(freq=450 + greens * 80, duration=0.12, vol=0.25)
                    trigger_shake(5.0)

                self.user_input = ""
            else:
                trigger_shake(6.0)
                sfx.play(freq=140, duration=0.15, wave_type="square", vol=0.2)
        elif event.key == pygame.K_BACKSPACE:
            self.user_input = self.user_input[:-1]
        elif event.unicode.isalpha() and len(self.user_input) < 5:
            self.user_input += event.unicode.upper()

    def draw(self, surface, ring, time_sec, active_palette):
        # 1. Title
        title_surf = self.font_title.render("GLOBAL WORDLE OF THE DAY", True, configs.COLOR_TEXT_BRIGHT)
        surface.blit(title_surf, title_surf.get_rect(center=(ring.x, ring.y - 215)))

        # 2. Subtitle Hint
        hint_surf = self.font_hint.render("Enter today's real NYT Wordle answer!", True, (130, 150, 175))
        surface.blit(hint_surf, hint_surf.get_rect(center=(ring.x, ring.y - 192)))

        # 3. Previous Guesses Row
        if self.guesses:
            last_word, last_colors = self.guesses[-1]
            total_w = 5 * 38
            start_x = ring.x - (total_w // 2)
            for i in range(5):
                tile_rect = pygame.Rect(start_x + i * 38, ring.y - 170, 32, 32)
                pygame.draw.rect(surface, last_colors[i], tile_rect, border_radius=5)
                letter_s = self.font_tile.render(last_word[i], True, (255, 255, 255))
                surface.blit(letter_s, letter_s.get_rect(center=tile_rect.center))

        # 4. Current Input Boxes
        total_w = 5 * 36
        start_x = ring.x - (total_w // 2)
        cur_y = ring.y - 132 if self.guesses else ring.y - 155

        for i in range(5):
            tile_rect = pygame.Rect(start_x + i * 36, cur_y, 30, 30)
            pygame.draw.rect(surface, configs.COLOR_TRACK, tile_rect, border_radius=5)

            is_active = (i == len(self.user_input))
            border_col = active_palette["main"] if is_active else (70, 75, 95)
            pygame.draw.rect(surface, border_col, tile_rect, 2 if is_active else 1, border_radius=5)

            if i < len(self.user_input):
                letter_s = self.font_tile.render(self.user_input[i], True, configs.COLOR_TEXT_BRIGHT)
                surface.blit(letter_s, letter_s.get_rect(center=tile_rect.center))


# ==========================================
# MISSION MANAGER
# ==========================================
class MissionManager:
    def __init__(self):
        self.missions = [
            WordleMission(),
        ]
        self.current_idx = 0
        self.current_mission.on_start()

    @property
    def current_mission(self):
        return self.missions[self.current_idx]

    def on_loop_change(self, loop_count):
        self.current_idx = loop_count % len(self.missions)
        self.current_mission.on_start()

    def update(self, dt, ring, *args, **kwargs):
        self.current_mission.update(dt, ring)

    def handle_event(self, event, ring, sfx, particles_list, trigger_shake, *args, **kwargs):
        self.current_mission.handle_event(event, ring, sfx, particles_list, trigger_shake)

    def draw(self, surface, ring, time_sec, active_palette, *args, **kwargs):
        self.current_mission.draw(surface, ring, time_sec, active_palette)