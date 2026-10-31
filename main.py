import os
import sys
if hasattr(sys, '_MEIPASS'):
    os.chdir(sys._MEIPASS)
import math
import random
import pygame

import configs
import particles
import ring
import SoundMaker
from missions_controller import MissionManager


def get_ui_font(size, bold=False):
    for font_name in ["segoeui", "inter", "sfprodisplay", "helveticaneue", "arial", "dejavusans"]:
        try:
            return pygame.font.SysFont(font_name, size, bold=bold)
        except Exception:
            pass
    return pygame.font.Font(None, size)


class LoadingScreenGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("LowDing!")
        self.screen = pygame.display.set_mode((configs.SCREEN_WIDTH, configs.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.font_pct = get_ui_font(44, bold=True)
        self.font_badge = get_ui_font(13, bold=True)
        self.font_title = get_ui_font(14, bold=True)

        self.sfx = SoundMaker.SoundFX()
        self.play_bg_music()

        self.ring = ring.LoadingRing(
            configs.SCREEN_WIDTH // 2,
            360,
            radius=135,
            thickness=14
        )
        self.mission_manager = MissionManager()
        self.particles = []
        self.ripples = []
        self.shake = 0.0
        self.wiggle_timer = 0.0
        self.time = 0.0
        self.palette_idx = 0
        self.loops = 0

        self.bg_cache = self._create_bg_surface()

    def _create_bg_surface(self):
        bg = pygame.Surface((configs.SCREEN_WIDTH, configs.SCREEN_HEIGHT))
        bg_col = getattr(configs, "COLOR_BG", (12, 14, 20))
        bg.fill(bg_col)

        spacing = 30
        dot_color = (24, 29, 42)
        for x in range(spacing // 2, configs.SCREEN_WIDTH, spacing):
            for y in range(spacing // 2, configs.SCREEN_HEIGHT, spacing):
                bg.set_at((x, y), dot_color)

        vignette = pygame.Surface((configs.SCREEN_WIDTH, configs.SCREEN_HEIGHT), pygame.SRCALPHA)
        cx, cy = configs.SCREEN_WIDTH // 2, configs.SCREEN_HEIGHT // 2
        max_dist = math.hypot(cx, cy)
        
        for r in range(int(max_dist * 0.4), int(max_dist), 24):
            alpha = int(90 * ((r - max_dist * 0.4) / (max_dist * 0.6)))
            pygame.draw.circle(vignette, (5, 7, 10, min(140, alpha)), (cx, cy), r, 24)
        
        bg.blit(vignette, (0, 0))
        return bg

    def play_bg_music(self):
        for filename in ["bg.mp3", "bg.ogg", "bg.wav", "bg"]:
            if os.path.exists(filename):
                try:
                    pygame.mixer.music.load(filename)
                    pygame.mixer.music.set_volume(0.35)
                    pygame.mixer.music.play(-1)
                    break
                except Exception:
                    pass

    def trigger_shake(self, intensity=8.0):
        self.shake = intensity

    def trigger_wiggle(self, duration=2.5):
        self.wiggle_timer = duration

    def trigger_loop_warp(self):
        was_six_seven = (self.mission_manager.current_idx == 3)
        self.loops += 1

        old_palette = configs.RING_PALETTES[self.palette_idx]
        self.palette_idx = (self.palette_idx + 1) % len(configs.RING_PALETTES)
        new_palette = configs.RING_PALETTES[self.palette_idx]

        self.ring.set_base_trace(old_palette["main"])
        self.mission_manager.on_loop_change(self.loops)

        self.ripples.append(particles.Ripple(self.ring.x, self.ring.y, new_palette["main"]))
        for _ in range(24):
            self.particles.append(particles.Particle(self.ring.x, self.ring.y, new_palette["main"]))

        self.sfx.play(freq=350, duration=0.25, vol=0.3)

        if was_six_seven:
            self.trigger_wiggle(2.5)
            self.trigger_shake(15.0)
        else:
            self.trigger_shake(8.0)

        self.ring.spin_speed = min(360.0, self.ring.spin_speed + 12.0)

    def draw_header_bar(self, surface, active_palette):

        pill_w, pill_h = 110, 30
        pill_x = configs.SCREEN_WIDTH - pill_w - 24
        pill_y = 15
        pill_rect = pygame.Rect(pill_x, pill_y, pill_w, pill_h)

        pygame.draw.circle(surface, active_palette["main"], (pill_x + 16, pill_y + pill_h // 2), 4)

    def run(self):
        while True:
            dt = self.clock.tick(configs.FPS) / 1000.0
            self.time += dt
            active_palette = configs.RING_PALETTES[self.palette_idx]

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                self.mission_manager.handle_event(
                    event, self.ring, self.sfx, self.particles, self.trigger_shake
                )

            self.ring.update(dt)
            self.mission_manager.update(dt, self.ring)

            if self.ring.progress >= 100.0:
                self.trigger_loop_warp()

            if self.shake > 0:
                self.shake = max(0.0, self.shake - dt * 25.0)

            for p in self.particles[:]:
                p.update(dt)
                if p.life <= 0:
                    self.particles.remove(p)

            for r in self.ripples[:]:
                r.update(dt)
                if r.is_dead():
                    self.ripples.remove(r)

            render_surface = pygame.Surface((configs.SCREEN_WIDTH, configs.SCREEN_HEIGHT))
            render_surface.blit(self.bg_cache, (0, 0))

            for rip in self.ripples:
                rip.draw(render_surface)
            for p in self.particles:
                p.draw(render_surface)

            try:
                self.ring.draw(render_surface, self.font_pct, active_palette, self.time)
            except TypeError:
                self.ring.draw(render_surface, active_palette, self.time)

            self.mission_manager.draw(render_surface, self.ring, self.time, active_palette)

            self.draw_header_bar(render_surface, active_palette)

            if self.wiggle_timer > 0:
                progress = (2.5 - self.wiggle_timer)
                fade = (self.wiggle_timer / 2.5)
                wiggle_y = math.sin(progress * 7.0) * 22.0 * fade
                wiggle_x = math.cos(progress * 3.5) * 8.0 * fade
                self.wiggle_timer = max(0.0, self.wiggle_timer - dt)
            else:
                wiggle_x = 0
                wiggle_y = 0

            shake_x = (random.uniform(-self.shake, self.shake) if self.shake > 0 else 0) + wiggle_x
            shake_y = (random.uniform(-self.shake, self.shake) if self.shake > 0 else 0) + wiggle_y

            self.screen.fill(getattr(configs, "COLOR_BG", (12, 14, 20)))
            self.screen.blit(render_surface, (int(shake_x), int(shake_y)))
            pygame.display.flip()


if __name__ == "__main__":
    game = LoadingScreenGame()
    game.run()