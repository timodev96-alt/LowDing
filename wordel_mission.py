import os
import json
import math
import random
import datetime
import threading
import urllib.request
import pygame
import configs
from missions_controller import BaseMission
from particles import Particle

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
