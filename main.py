import sys
import math
import random
import pygame

import configs
import particles
import ring
import SoundMaker
from missions_controller import MissionManager

# --- SIMPLE SCROLLING GRID BACKGROUND ---
def draw_moving_grid(surface, time_sec, cell_size=40, speed=25.0):
    grid_color = (18, 22, 32)  # Subtle dark grid line color
    # Offset moves towards top-left (0, 0)
    offset = (time_sec * speed) % cell_size

    # Vertical grid lines
    for x in range(int(-offset), configs.SCREEN_WIDTH + cell_size, cell_size):
        pygame.draw.line(surface, grid_color, (x, 0), (x, configs.SCREEN_HEIGHT), 1)

    # Horizontal grid lines
    for y in range(int(-offset), configs.SCREEN_HEIGHT + cell_size, cell_size):
        pygame.draw.line(surface, grid_color, (0, y), (configs.SCREEN_WIDTH, y), 1)


class LoadingScreenGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("LowDing!")
        self.screen = pygame.display.set_mode((configs.SCREEN_WIDTH, configs.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.font_pct = pygame.font.SysFont("monospace", 38, bold=True)
        self.font_loops = pygame.font.SysFont("monospace", 24, bold=True)

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
        self.wiggle_timer = 0.0
        self.time = 0.0
        self.palette_idx = 0
        self.loops = 0

    def trigger_shake(self, intensity=8.0):
        self.shake = intensity

    def trigger_wiggle(self, duration=2.5):
        self.wiggle_timer = duration

    def trigger_loop_warp(self):
        # Check if the level we just completed was Level 4 (SixSevenMission)
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

            # 1. Fill base dark color
            render_surface = pygame.Surface((configs.SCREEN_WIDTH, configs.SCREEN_HEIGHT))
            render_surface.fill(configs.COLOR_BG)

            # 2. Draw simple moving grid background
            draw_moving_grid(render_surface, self.time, cell_size=42, speed=24.0)

            # 3. Draw game elements on top
            for rip in self.ripples:
                rip.draw(render_surface)
            for p in self.particles:
                p.draw(render_surface)

            self.ring.draw(render_surface, self.font_pct, active_palette, self.time)
            self.mission_manager.draw(render_surface, self.ring, self.time, active_palette)

            # Loops counter
            loops_txt = self.font_loops.render(f"LOOPS: {self.loops}", True, configs.COLOR_TEXT_BRIGHT)
            render_surface.blit(loops_txt, loops_txt.get_rect(topright=(configs.SCREEN_WIDTH - 24, 24)))

            # Screen Wiggle / Shake
            if self.wiggle_timer > 0:
                progress = (2.5 - self.wiggle_timer)
                fade = (self.wiggle_timer / 2.5)
                wiggle_y = math.sin(progress * 7.0) * 32.0 * fade
                wiggle_x = math.cos(progress * 3.5) * 10.0 * fade
                self.wiggle_timer = max(0.0, self.wiggle_timer - dt)
            else:
                wiggle_x = 0
                wiggle_y = 0

            shake_x = (random.randint(-int(self.shake), int(self.shake)) if self.shake > 0 else 0) + int(wiggle_x)
            shake_y = (random.randint(-int(self.shake), int(self.shake)) if self.shake > 0 else 0) + int(wiggle_y)

            self.screen.fill(configs.COLOR_BG)
            self.screen.blit(render_surface, (shake_x, shake_y))
            pygame.display.flip()

if __name__ == "__main__":
    game = LoadingScreenGame()
    game.run()