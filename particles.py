import random
import math
import pygame
from settings import screen, SCREEN_WIDTH, SCREEN_HEIGHT, WHITE

class Snowflake:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(-50, SCREEN_HEIGHT)
        self.layer = random.choice([1, 2, 3])

        if self.layer == 1:
            self.speed = random.uniform(0.6, 1.2)
            self.size = random.randint(1, 2)
        elif self.layer == 2:
            self.speed = random.uniform(1.2, 2.0)
            self.size = random.randint(2, 3)
        else:
            self.speed = random.uniform(2.0, 3.2)
            self.size = random.randint(3, 4)

        self.drift = random.uniform(-0.4, 0.4)

    def fall(self, surface=None):
        from settings import screen as _screen
        surf = surface or _screen
        self.y += self.speed
        self.x += self.drift + math.sin(self.y * 0.02) * 0.15

        pygame.draw.circle(surf, WHITE, (int(self.x), int(self.y)), self.size)

        if self.y > SCREEN_HEIGHT:
            self.y = random.randint(-50, -10)
            self.x = random.randint(0, SCREEN_WIDTH)

class Sparkle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(2, 4)
        self.speed_x = random.uniform(-1.5, 1.5)
        self.speed_y = random.uniform(-2, -0.5)
        self.life = random.randint(12, 18)

        self.color = random.choice([
            (255, 230, 120),
            (255, 215, 80),
            (255, 200, 60),
            (255, 240, 160)
        ])

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= 1

        if self.size > 1:
            self.size -= 0.05

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))



class SnowBurst:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(2, 5)
        self.speed_x = random.uniform(-1.5, 1.5)
        self.speed_y = random.uniform(-2, -0.5)
        self.life = random.randint(12, 20)

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= 1
        if self.size > 1:
            self.size -= 0.1

    def draw(self):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), int(self.size))

class EnemyBurst:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(3, 6)
        self.speed_x = random.uniform(-2, 2)
        self.speed_y = random.uniform(-3, 1)
        self.life = random.randint(10, 16)
        self.color = random.choice([
            (120, 255, 120),
            (80, 220, 80),
            (180, 255, 180)
        ])

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= 1
        if self.size > 1:
            self.size -= 0.12

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))

class PortalParticle:
    def __init__(self, x, y):
        self.x = x + random.randint(-20, 20)
        self.y = y + random.randint(-20, 20)

        self.size = random.randint(2, 4)

        self.speed_x = random.uniform(-0.5, 0.5)
        self.speed_y = random.uniform(-1.2, -0.2)

        self.life = random.randint(18, 30)

        self.color = random.choice([
            (220, 40, 40),   # Christmas red
            (30, 170, 60),   # Christmas green
            (255, 215, 0),   # gold sparkle
            (255, 255, 255)  # snow white
        ])

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= 1

        if self.size > 1:
            self.size -= 0.05

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))


class FloatingText:
    def __init__(self, x, y, text="+1"):
        self.x = x
        self.y = y
        self.text = text
        self.life = 45
        self.max_life = 45

    def update(self):
        self.y -= 1.2
        self.life -= 1

    def draw(self, surface, font):
        if self.life > 0:
            alpha = int((self.life / self.max_life) * 255)
            surf = font.render(self.text, True, (255, 60, 60))
            surf.set_alpha(alpha)
            surface.blit(surf, (int(self.x) - surf.get_width() // 2, int(self.y)))