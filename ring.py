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
        self.display_progress = 0.0
        self.pop_scale = 1.0

        self.scanner_angle = 0.0
        self.spin_speed = 180.0
        self.base_color = configs.COLOR_TRACK

    def add_progress(self,amount):
        self.progress = min(100.0,max(0.0,self.progress+amount))
        self.pop_scale = 1.25
    
    def update(self, dt):
        self.scanner_angle = (self.scanner_angle + self.spin_speed * dt) % 360.0
        diff = self.progress - self.display_progress
        self.display_progress += diff * min(1.0, dt * 10.0)

        if self.pop_scale > 1.0:
            self.pop_scale = max(1.0,self.pop_scale-dt*2.0)

    def set_base_trace(self, completed_color):
        self.base_color = completed_color
        self.progress = 0.0
        self.display_progress = 0.0

    def draw(self, surface, font_pct, active_palette, time_sec):
        r = self.base_radius
        steps = 180
        for i in range(steps):
            rad= math.radians(i*(360.0/steps))
            bx = self.x + math.cos(rad) * r
            by = self.y + math.sin(rad) * r
            pygame.draw.circle(surface, self.base_color, (int(bx), int(by)),self.cap_radius)

        if self.display_progress >0.1:
            fill_steps = int((self.display_progress/100.0)*steps)
            for i in range(fill_steps+1):
                rad = math.radians((i*(360.0/steps))-90.0)
                px = self.x + math.cos(rad) * r
                py = self.y + math.sin(rad) * r
                pygame.draw.circle(surface, active_palette["main"], (int(px), int(py)), self.cap_radius)


        trail_length = 16

        for t in range(trail_length):
            tail_angle = (self.scanner_angle - 90.0) - (t*2.2)
            rad = math.radians(tail_angle)
            sx = self.x + math.cos(rad) * r
            sy = self.y + math.sin(rad) * r
            alpha_ratio = 1.0 - (t/trail_length)
            size = max(1,int(self.cap_radius * (0.4+0.7 * alpha_ratio)))

            tail_col = [
                int(c*alpha_ratio + bc * (1.0-alpha_ratio))
                for c,bc in zip(active_palette["main"],configs.COLOR_BG)
            ]
            pygame.draw.circle(surface, tail_col, (int(sx), int(sy)), size)

        font_size = int(46 * self.pop_scale)
        pct_font = configs.get_font(font_size,bold=True)
        pct_surf = pct_font.render(f"{int(round(self.display_progress))}%", True, configs.COLOR_TEXT)
        surface.blit(pct_surf,pct_surf.get_rect(center=(self.x,self.y-8)))
