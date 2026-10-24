# ring.py
import math
import pygame
import configs

class LoadingRing:
    def __init__(self, x, y, radius=130, thickness=14):
        self.x = x
        self.y = y
        self.radius = radius
        self.thickness = thickness
        self.progress = 0.0
        self.display_progress = 0.0
        self.scanner_angle = 0.0
        self.spin_speed = 180.0
        self.scale = 1.0

    def add_progress(self, amount):
        self.progress = min(100.0, max(0.0, self.progress + amount))
        if amount > 0:
            self.scale = 1.08
        else:
            self.scale = 0.94

    def update(self, dt):
        self.scanner_angle = (self.scanner_angle + self.spin_speed * dt) % 360.0
        self.display_progress += (self.progress - self.display_progress) * min(1.0, dt*12.0)
        self.scale += (1.0 - self.scale) * min(1.0, dt * 10.0)

    def draw(self,surface, font, palette, time_sec):
        r=int(self.radius * self.scale)
        rect = pygame.Rect(self.x - r, self.y - r, r*2, r*2)
        pygame.draw.circle(surface, (24,28,38),(self.x,self.y), r,self.thickness)

        if self.display_progress>0:
            angle_span = (self.display_progress/100.0) * 360
            start_rad = math.radians(-90)
            end_rad = math.radians(-90 + angle_span)
            pygame.draw.arc(surface, palette["main"], rect, -end_rad, -start_rad, self.thickness)

            
        tip_rad = math.radians(self.scanner_angle - 90)
        tx = int(self.x + math.cos(tip_rad)*r) # yay mathh :D
        ty = int(self.x + math.sin(tip_rad)*r)
        pygame.draw.circle(surface, palette["main"], (tx,ty), self.thickness // 2+2)

        txt = font.render(f"{int(self.display_progress)}%", True, (255,255,255))
        surface.blit(txt, txt.get_rect(center=(self.x, self.y)))