# SoundMaker.py
import math
import array
import pygame

class SoundFX:
    def __init__(self):
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            self.enabled = True
        except Exception:
            self.enabled = False

    def play(self, freq=440, duration=0.1, wave_type="sine", vol=0.25):
        if not self.enabled:
            return
        sample_rate = 22050
        samples = int(sample_rate * duration)
        buf = array.array("h")
        for i in range(samples):
            t = float(i) / sample_rate
            val = math.sin(2.0 * math.pi * freq * t) if wave_type == "sine" else (1.0 if math.sin(2.0 * math.pi * freq * t) > 0 else -1.0)
            decay = (1.0 - (i / samples)) ** 1.5
            buf.append(int(val * 32767 * vol * decay))
        pygame.mixer.Sound(buffer=buf).play()