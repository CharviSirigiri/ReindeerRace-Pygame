import math
import random
import pygame
from settings import platform_base_img, coin_img, exit_game_img

class Checkpoint(pygame.sprite.Sprite):
    """Checkpoint - touching saves progress."""
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((32, 40), pygame.SRCALPHA)
        # Winter-themed: subtle ice crystal / snowflake marker
        pygame.draw.polygon(self.image, (180, 220, 255), [(16, 2), (20, 16), (16, 38), (12, 16)])
        pygame.draw.polygon(self.image, (140, 190, 240), [(16, 8), (26, 20), (16, 32), (6, 20)])
        pygame.draw.circle(self.image, (200, 230, 255), (16, 20), 6)
        self.rect = self.image.get_rect(midbottom=(x, y))

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width=120):
        super().__init__()
        self.image = pygame.transform.scale(platform_base_img, (width, 30))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.velocity_x = 0
        self.velocity_y = 0

    def update(self):
        pass


class MovingPlatform(Platform):
    """Platform that moves horizontally. Player moves with it when standing on top."""
    def __init__(self, x, y, width, move_range=60, speed=1.2):
        super().__init__(x, y, width)
        self.start_x = x
        self.move_range = move_range
        self.speed = speed
        self.t = 0

    def update(self):
        self.t += 0.03 * self.speed
        prev_x = self.rect.x
        self.rect.x = self.start_x + int(math.sin(self.t) * self.move_range)
        self.velocity_x = self.rect.x - prev_x
        self.velocity_y = 0

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = coin_img
        self.rect = self.image.get_rect(center=(x, y))
        self.start_y = y
        self.timer = random.randint(0, 60)

    def update(self):
        self.timer += 0.1
        self.rect.y = self.start_y + math.sin(self.timer) * 5

class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = exit_game_img
        self.rect = self.image.get_rect(midbottom=(x, y))