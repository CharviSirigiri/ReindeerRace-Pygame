import pygame
from settings import (
    screen, PINK, WHITE,
    player_frames_right, player_frames_left, dead_img,
    jump_fx, coin_fx, game_over_fx, level_complete_fx,stomp_fx, drop_fx
)
from ui import draw_text
from particles import Sparkle, SnowBurst, EnemyBurst

class Player:
    def __init__(self, x, y):
        self.reset(x, y)

    def reset(self, x, y, invincible=0):
        self.images_right = player_frames_right
        self.images_left = player_frames_left
        self.dead_image = dead_img

        self.index = 0
        self.counter = 0
        self.direction = 1

        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.width = self.image.get_width()
        self.height = self.image.get_height()

        self.vel_y = 0
        self.jumped = False
        self.double_jumped = False
        self.in_air = True
        self.standing_platform = None
        self.dash_timer = 0
        self.dash_cooldown = 0
        self.stamina = 100.0
        self.max_stamina = 100.0
        self.invincible_timer = invincible
        self.trail = []

    def update(self, game_state, platform_group, coin_group, enemy_group, exit_group, sparkles, score, target_score, flash_timer, flash_color, difficulty="normal", reduced_motion=False):
        from settings import get_screen_shake_mult
        shake_mult = get_screen_shake_mult() if not reduced_motion else 0

        dx = 0
        dy = 0
        walk_speed = 4 if difficulty == "easy" else (3 if difficulty == "hard" else 3)
        jump_power = 16 if difficulty == "easy" else (14 if difficulty == "hard" else 15)
        walk_cooldown = 6
        col_thresh = 15
        screen_shake = 0
        new_flash_timer = flash_timer
        new_flash_color = flash_color

        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        if self.dash_cooldown > 0:
                self.dash_cooldown -= 1
        if self.stamina < self.max_stamina:
                self.stamina = min(self.max_stamina, self.stamina + 0.4)

        if game_state == 0:
            keys = pygame.key.get_pressed()
            # When NOT moving (idle), move with platform so reindeer stays in same spot on it
            if self.standing_platform and hasattr(self.standing_platform, 'velocity_x'):
                if not keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT] and self.dash_timer <= 0:
                    self.rect.x += self.standing_platform.velocity_x
                    self.rect.y += getattr(self.standing_platform, 'velocity_y', 0)

            if self.dash_timer > 0:
                self.dash_timer -= 1
                dx = 8 * self.direction
            else:
                if keys[pygame.K_LEFT]:
                    dx -= walk_speed
                    self.counter += 1
                    self.direction = -1

                if keys[pygame.K_RIGHT]:
                    dx += walk_speed
                    self.counter += 1
                    self.direction = 1


                if keys[pygame.K_SPACE]:
                    if not self.in_air:
                        if jump_fx:
                            jump_fx.play()
                        self.vel_y = -jump_power
                        self.jumped = True
                        self.double_jumped = False
                        self.standing_platform = None
                    elif not self.double_jumped and self.vel_y > -5:
                        if jump_fx:
                            jump_fx.play()
                        self.vel_y = -jump_power * 0.85
                        self.double_jumped = True
                else:
                    if self.in_air and self.vel_y < 0:
                        self.vel_y *= 0.6

                if keys[pygame.K_x] and self.dash_cooldown <= 0 and self.stamina >= 25:
                    self.dash_timer = 8
                    self.dash_cooldown = 45
                    self.stamina -= 25

            if not keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
                self.counter = 0
                self.index = 0
                self.image = self.images_right[self.index] if self.direction == 1 else self.images_left[self.index]

            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                self.image = self.images_right[self.index] if self.direction == 1 else self.images_left[self.index]

            self.vel_y += 0.8
            if self.vel_y > 8:
                self.vel_y = 8
            dy += self.vel_y

            self.in_air = True
            self.standing_platform = None

            for platform in platform_group:
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0

                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if self.vel_y >= 0 and abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
                        if self.in_air:
                            for _ in range(6):
                                sparkles.append(SnowBurst(self.rect.centerx, platform.rect.top))

                        self.rect.bottom = platform.rect.top
                        dy = 0
                        self.vel_y = 0
                        self.in_air = False
                        self.double_jumped = False
                        self.standing_platform = platform

                    elif self.vel_y < 0 and abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
                        dy = platform.rect.bottom - self.rect.top
                        self.vel_y = 0

            self.rect.x += dx
            self.rect.y += dy

            current_width = screen.get_width()
            current_height = screen.get_height()

            if self.rect.left < 0:
                self.rect.left = 0
            if self.rect.right > current_width:
                self.rect.right = current_width

            if self.rect.top > current_height:
                game_state = -1
                if game_over_fx:
                    game_over_fx.play()
                screen_shake = 10 * shake_mult
                new_flash_timer = 6
                new_flash_color = (255, 80, 80)

            collected = pygame.sprite.spritecollide(self, coin_group, True)
            for coin in collected:
                score += 1
                if coin_fx:
                    coin_fx.play()
                screen_shake = 5 * shake_mult
                new_flash_timer = 4
                new_flash_color = (255, 230, 120)

                for _ in range(10):
                    sparkles.append(Sparkle(coin.rect.centerx, coin.rect.centery))

            hit_enemies = pygame.sprite.spritecollide(self, enemy_group, False)
            for enemy in hit_enemies:
                if self.invincible_timer > 0:
                    continue
                if self.vel_y > 0 and self.rect.bottom <= enemy.rect.top + 15:
                    enemy.kill()
                    if stomp_fx:
                        stomp_fx.play()
                    self.vel_y = -10
                    screen_shake = 6 * shake_mult
                    new_flash_timer = 6
                    new_flash_color = (255, 80, 80)
                    for _ in range(6):
                        sparkles.append(EnemyBurst(enemy.rect.centerx, enemy.rect.centery))

                else:
                    game_state = -1
                    if game_over_fx:
                        game_over_fx.play()
                    screen_shake = 10 * shake_mult

            if pygame.sprite.spritecollide(self, exit_group, False):
                if score >= target_score:
                    game_state = 1
                    if level_complete_fx:
                        level_complete_fx.play()
                    screen_shake = 10 * shake_mult
                    new_flash_timer = 6
                    new_flash_color = (180, 220, 255)

        elif game_state == -1:
            self.image = self.dead_image

        if self.dash_timer > 0:
            self.trail.append((self.rect.topleft, self.image.copy()))
            if len(self.trail) > 5:
                self.trail.pop(0)
            for i, (pos, img) in enumerate(self.trail):
                ghost = img.copy()
                ghost.set_alpha(20 + i * 15)
                screen.blit(ghost, pos)
        else:
            self.trail.clear()

        if self.invincible_timer <= 0 or self.invincible_timer % 4 >= 2:
            screen.blit(self.image, self.rect)
        return game_state, score, screen_shake, new_flash_timer, new_flash_color