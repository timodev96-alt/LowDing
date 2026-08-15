import math
import random
import pygame
import configs
from particles import Particle

class BaseMission:
    def on_start(self):
        pass

    def update(self, dt, ring):
        pass

    def handle_event(self, event, ring, sfx, particles_list, trigger_shake):
        pass

    def draw(self, surface, ring, time_sec, active_palette):
        pass


class SyncNode:
    def __init__(self, angle, is_green=True):
        self.angle = angle % 360.0
        self.is_green = is_green
        self.palette = configs.ORB_GREEN if is_green else configs.ORB_RED
        self.value = random.randint(19, 23)

    def get_pos(self, cx, cy, radius):
        rad = math.radians(self.angle - 90.0)
        return int(cx + math.cos(rad) * radius), int(cy + math.sin(rad) * radius)

    def draw(self, surface, cx, cy, radius):
        px, py = self.get_pos(cx, cy, radius)
        pygame.draw.circle(surface, self.palette["main"], (px, py), 8)
        pygame.draw.circle(surface, self.palette["deep"], (px, py), 5)

from orb_mission import OrbMission
from wordel_mission import WordleMission
from sequance_mission import SequenceMission
from six_seven_mission import SixSevenMission
from Timo_slack_mission import TimoMission
from plusing_mission import MathMission
from FlappySnake_mission import FlappySnakeMission

class MissionManager:
    def __init__(self):
        self.missions = [
            OrbMission(),
            MathMission(),
            SixSevenMission(),
            TimoMission(),
            WordleMission(),
            SequenceMission(),
            FlappySnakeMission(),
        ]
        self.current_idx = 0
        self.current_mission.on_start()

    @property
    def current_mission(self):
        return self.missions[self.current_idx]

    def on_loop_change(self, loop_count):
        self.current_idx = loop_count % len(self.missions)
        self.current_mission.on_start()

    def update(self, dt, ring, *args, **kwargs):
        self.current_mission.update(dt, ring)

    def handle_event(self, event, ring, sfx, particles_list, trigger_shake, *args, **kwargs):
        self.current_mission.handle_event(event, ring, sfx, particles_list, trigger_shake)

    def draw(self, surface, ring, time_sec, active_palette, *args, **kwargs):
        self.current_mission.draw(surface, ring, time_sec, active_palette)