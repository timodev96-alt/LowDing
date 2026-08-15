import math
import pygame
import random
import configs
from particles import Particle
import missions_controller
from missions_controller import BaseMission

class OrbMission(BaseMission):
    def __init__(self):
        self.nodes = []
        self.spawn_timer = 0.0

    def on_start(self):
        self.nodes.clear()
        self.spawn_timer = 0.0

    def update(self, dt, ring):
        self.spawn_timer += dt
        if self.spawn_timer >= 0.85:
            self.spawn_timer = 0.0
            if len(self.nodes) < 5:
                is_green = random.random() < 0.70
                self.nodes.append(missions_controller.SyncNode(random.uniform(0, 360), is_green))

    def handle_event(self, event, ring, sfx, particles_list, trigger_shake):
        is_action = (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE) or \
                    (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1)
        if not is_action:
            return

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
                ring.progress = min(100.0, ring.progress + node.value)
                sfx.play(freq=580, duration=0.12, vol=0.25)
                for _ in range(14):
                    particles_list.append(Particle(nx, ny, configs.ORB_GREEN["main"]))
            else:
                ring.progress = max(0.0, ring.progress - node.value)
                trigger_shake(10.0)
                sfx.play(freq=140, duration=0.15, wave_type="square", vol=0.22)
                for _ in range(14):
                    particles_list.append(Particle(nx, ny, configs.ORB_RED["main"]))
        else:
            sfx.play(freq=240, duration=0.05, vol=0.10)

    def draw(self, surface, ring, time_sec, active_palette):
        pulse = math.sin(time_sec * 2.5) * 1.5
        current_r = ring.base_radius + pulse
        for node in self.nodes:
            node.draw(surface, ring.x, ring.y, current_r)