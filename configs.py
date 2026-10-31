# configs.py
import pygame
pygame.font.init()
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 650
FPS = 60

COLOR_BG = (10, 12, 16)
COLOR_SURFACE = (18,22,30)
COLOR_TRACK = (28,34,46)
COLOR_BORDER = (42,50,68)

COLOR_TEXT = (240,244,250)
COLOR_TXT_MUTED = (120,135,160)
COLOR_TXT_DIM = (70,80,100)

ORB_GREEN = {"main":(52,211,153),"deep":(16,110,75),"glow": (52,211,153,40)}
ORB_RED   = {"main": (248, 113, 113),  "deep": (130, 30,30), "glow": (248,113,113,40)}

RING_PALETTES = [
    {"main": (56, 189, 248), "deep": (14, 116, 144)},
    {"main": (168, 85, 247), "deep": (107, 33, 168)},
    {"main": (251, 191, 36), "deep": (180, 83, 9)},
    {"main": (244, 63, 94),  "deep": (159, 18, 57)},
    {"main": (45, 212, 191), "deep": (15, 118, 110)},
]

def get_font(size, bold=False):
    return pygame.font.SysFont("bahnschrift,segoeuivariable,segoeui,arial", size, bold=bold)
def get_mono_font(size, bold=False):
    return pygame.font.SysFont("cascadiacode,consolas,lucidaconsole", size, bold=bold)