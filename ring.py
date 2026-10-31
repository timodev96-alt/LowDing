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
        pygame.draw.circle(surface,self.base_color,(self.x,self.y),r,self.thickness)

        if self.display_progress > 0.5:
            rect = pygame.Rect(self.x-r,self.y-r,r*2,r*2)
            pct_deg = (self.display_progress/100.0) * 360.0

            start_rad = math.radians(90.0 - pct_deg)
            end_rad = math.radians(90.0)
            pygame.draw.arc(surface,active_palette["main"], rect, start_rad,end_rad,self.thickness)

            pygame.draw.circle(surface,active_palette["main"],(self.x,self.y - r), self.cap_radius)

            tip_rad = math.radians(pct_deg - 90.0)
            tip_x = self.x + math.cos(tip_rad) * r
            tip_y = self.y + math.sin(tip_rad) * r
            pygame.draw.circle(surface, active_palette["main"], (int(tip_x), int(tip_y)), self.cap_radius)

        scan_rad = math.radians(self.scanner_angle - 90.0)
        sx = int(self.x + math.cos(scan_rad)* r)
        sy = int(self.y + math.sin(scan_rad)* r)

        glow_size = 12
        glow_surf = pygame.Surface((glow_size * 2, glow_size *2), pygame.SRCALPHA)
        glow_col = (*active_palette["main"],45)
        pygame.draw.circle(glow_surf, glow_col, (glow_size,glow_size),glow_size)
        surface.blit(glow_surf, (sx-glow_size, sy-glow_size), special_flags=pygame.BLEND_ADD)

        pygame.draw.circle(surface, active_palette["main"], (sx,sy), self.cap_radius + 1)
        pygame.draw.circle(surface, (255,255,255),(sx,sy),3)

        font_size = int(46*self.pop_scale)
        pct_font = configs.get_font(font_size,bold=True)
        pct_surf = pct_font.render(f"{int(round(self.display_progress))}%", True, configs.COLOR_TEXT)
        surface.blit(pct_surf, pct_surf.get_rect(center=(self.x,self.y)))