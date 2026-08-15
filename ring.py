# ring.py
import math
import pygame
import configs

class LoadingRing:
    def __init__(self, x, y, radius=120, thickness=13):
        self.x = x
        self.y = y
        self.base_radius = radius
        self.thickness = thickness
        self.cap_radius = thickness // 2
        
        self.progress = 0.0
        self.scanner_angle = 0.0
        self.spin_speed = 180.0
        self.base_color = configs.COLOR_TRACK
    def update(self, dt):
        self.scanner_angle = (self.scanner_angle + self.spin_speed * dt) % 360.0

    def set_base_trace(self, completed_color):
        self.base_color = completed_color
        self.progress = 0.0

    def draw(self, surface, font_pct, active_palette, time_sec):
        pulse = math.sin(time_sec * 2.5) * 1.5
        current_r = self.base_radius + pulse

        for i in range(360):
            rad = math.radians(i)
            bx = self.x + math.cos(rad) * current_r
            by = self.y + math.sin(rad) * current_r
            pygame.draw.circle(surface, self.base_color, (int(bx), int(by)), self.cap_radius)

        if self.progress > 0:
            steps = int((self.progress / 100.0) * 360.0 * 2)
            for i in range(steps + 1):
                rad = math.radians((i * 0.5) - 90.0)
                px = self.x + math.cos(rad) * current_r
                py = self.y + math.sin(rad) * current_r
                pygame.draw.circle(surface, active_palette["main"], (int(px), int(py)), self.cap_radius)

        scan_rad = math.radians(self.scanner_angle - 90.0)
        sx = self.x + math.cos(scan_rad) * current_r
        sy = self.y + math.sin(scan_rad) * current_r
        pygame.draw.circle(surface, active_palette["main"], (int(sx), int(sy)), self.cap_radius + 2)
        pygame.draw.circle(surface, active_palette["deep"], (int(sx), int(sy)), self.cap_radius - 2)

        pct_txt = font_pct.render(f"{int(self.progress)}%", True, configs.COLOR_TEXT_BRIGHT)
        surface.blit(pct_txt, pct_txt.get_rect(center=(self.x, self.y)))