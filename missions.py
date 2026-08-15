# missions.py
import math
import random
import pygame
import configs
from particles import Particle

class SyncNode:
    def __init__(self, angle, is_green=True):
        self.angle = angle % 360.0
        self.is_green = is_green
        self.palette = configs.ORB_GREEN if is_green else configs.ORB_RED
        # Random value between 6% and 11%
        self.value = random.randint(6, 11)

    def get_pos(self, cx, cy, radius):
        rad = math.radians(self.angle - 90.0)
        return int(cx + math.cos(rad) * radius), int(cy + math.sin(rad) * radius)

    def draw(self, surface, cx, cy, radius):
        px, py = self.get_pos(cx, cy, radius)
        pygame.draw.circle(surface, self.palette["main"], (px, py), 8)
        pygame.draw.circle(surface, self.palette["deep"], (px, py), 5)


class MissionManager:
    def __init__(self):
        self.nodes = []
        self.spawn_timer = 0.0

    def update(self, dt):
        self.spawn_timer += dt
        if self.spawn_timer >= 0.9:
            self.spawn_timer = 0.0
            if len(self.nodes) < 5:
                is_green = random.random() < 0.70
                self.nodes.append(SyncNode(random.uniform(0, 360), is_green))

    def handle_hit(self, ring, sfx, particles_list, trigger_shake):
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
                # Add random 6-11%
                ring.progress = min(100.0, ring.progress + node.value)
                sfx.play(freq=580, duration=0.12, vol=0.25)
                for _ in range(12):
                    particles_list.append(Particle(nx, ny, configs.ORB_GREEN["main"]))
            else:
                # Deduct random 6-11%
                ring.progress = max(0.0, ring.progress - node.value)
                trigger_shake(10.0)
                sfx.play(freq=140, duration=0.15, wave_type="square", vol=0.22)
                for _ in range(14):
                    particles_list.append(Particle(nx, ny, configs.ORB_RED["main"]))
        else:
            sfx.play(freq=240, duration=0.05, vol=0.12)

    def handle_event(self, event, ring, sfx, particles_list, trigger_shake):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.handle_hit(ring, sfx, particles_list, trigger_shake)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.handle_hit(ring, sfx, particles_list, trigger_shake)

    def draw(self, surface, ring, time_sec):
        pulse = math.sin(time_sec * 2.5) * 1.5
        current_r = ring.base_radius + pulse
        for node in self.nodes:
            node.draw(surface, ring.x, ring.y, current_r)