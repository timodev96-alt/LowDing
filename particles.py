# particles.py
import math
import random
import pygame

class Particle:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.color = color
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(1.8, 5.0)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = 1.0
        self.decay = random.uniform(1.8, 3.0)
        self.size = random.uniform(2.5, 5.0)

    def update(self, dt):
        self.x += self.vx * 60 * dt
        self.y += self.vy * 60 * dt
        self.life -= self.decay * dt

    def draw(self, surface):
        if self.life > 0:
            s = max(1, int(self.size * self.life))
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), s)


class Ripple:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.color = color
        self.radius = 25
        self.alpha = 220

    def update(self, dt):
        self.radius += 300 * dt
        self.alpha = max(0, int(220 * (1.0 - self.radius / 260)))

    def is_dead(self):
        return self.radius >= 260

    def draw(self, surface):
        if self.alpha > 0:
            s = pygame.Surface((int(self.radius * 2 + 4), int(self.radius * 2 + 4)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, self.alpha), (int(self.radius + 2), int(self.radius + 2)), int(self.radius), 3)
            surface.blit(s, (self.x - self.radius - 2, self.y - self.radius - 2))