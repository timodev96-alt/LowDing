# main.py
import sys
import random
import pygame

import configs
import particles
import ring
import SoundMaker
from missions import MissionManager

class LoadingScreenGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("LowDing!")
        self.screen = pygame.display.set_mode((configs.SCREEN_WIDTH, configs.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.font_pct = pygame.font.SysFont("monospace", 38, bold=True)

        self.sfx = SoundMaker.SoundFX()
        self.ring = ring.LoadingRing(
            configs.SCREEN_WIDTH // 2,
            configs.SCREEN_HEIGHT // 2,
            radius=120,
            thickness=13
        )
        self.mission_manager = MissionManager()
        self.particles = []
        self.ripples = []
        self.shake = 0.0
        self.time = 0.0
        self.palette_idx = 0

    def trigger_shake(self, intensity=8.0):
        self.shake = intensity

    def trigger_loop_warp(self):
        old_palette = configs.RING_PALETTES[self.palette_idx]
        self.palette_idx = (self.palette_idx + 1) % len(configs.RING_PALETTES)
        new_palette = configs.RING_PALETTES[self.palette_idx]

        self.ring.set_base_trace(old_palette["main"])

        self.ripples.append(particles.Ripple(self.ring.x, self.ring.y, new_palette["main"]))
        for _ in range(24):
            self.particles.append(particles.Particle(self.ring.x, self.ring.y, new_palette["main"]))

        self.sfx.play(freq=350, duration=0.25, vol=0.3)
        self.trigger_shake(8.0)
        self.ring.spin_speed = min(360.0, self.ring.spin_speed + 12.0)

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
            self.mission_manager.update(dt)

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
            render_surface.fill(configs.COLOR_BG)

            for rip in self.ripples:
                rip.draw(render_surface)
            for p in self.particles:
                p.draw(render_surface)

            self.ring.draw(render_surface, self.font_pct, active_palette, self.time)
            self.mission_manager.draw(render_surface, self.ring, self.time)

            shake_x = random.randint(-int(self.shake), int(self.shake)) if self.shake > 0 else 0
            shake_y = random.randint(-int(self.shake), int(self.shake)) if self.shake > 0 else 0
            self.screen.fill(configs.COLOR_BG)
            self.screen.blit(render_surface, (shake_x, shake_y))
            pygame.display.flip()

if __name__ == "__main__":
    game = LoadingScreenGame()
    game.run()