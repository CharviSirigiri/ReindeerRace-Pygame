import pygame
import math
from settings import grinch_img

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, move_range=100, speed=2):
        super().__init__()
        self.image_right = grinch_img
        self.image_left = pygame.transform.flip(grinch_img, True, False)
        self.image = self.image_right
        self.rect = self.image.get_rect(topleft=(x, y))

        self.start_x = x
        self.move_range = move_range
        self.direction = 1
        self.speed = speed

    def update(self):
        self.rect.x += self.direction * self.speed

        if self.direction == 1:
            self.image = self.image_right
        else:
            self.image = self.image_left

        if self.rect.x > self.start_x + self.move_range:
            self.direction = -1
        elif self.rect.x < self.start_x:
            self.direction = 1


class FlyingEnemy(pygame.sprite.Sprite):
    """Moves in a vertical sine pattern."""
    def __init__(self, x, y, move_range=80, speed=1.5):
        super().__init__()
        self.image_right = grinch_img
        self.image_left = pygame.transform.flip(grinch_img, True, False)
        self.image = self.image_right
        self.rect = self.image.get_rect(center=(x, y))
        self.start_x = x
        self.start_y = y
        self.move_range = move_range
        self.speed = speed
        self.t = 0

    def update(self):
        self.t += 0.05
        self.rect.x = self.start_x + math.sin(self.t) * self.move_range
        self.rect.y = self.start_y + math.sin(self.t * 1.3) * 30
        self.image = self.image_right if math.sin(self.t) >= 0 else self.image_left