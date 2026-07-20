import pygame
import random
import math
import math as _math
import settings as st
from settings import *
from ui import draw_text, draw_panel, Button
from player import Player
from levels import build_level, get_target_score, get_player_start
from narration import run_narration, run_instructions
from particles import Snowflake, Sparkle, SnowBurst, EnemyBurst, PortalParticle, FloatingText
from save_data import load, save, set_high_score, get_high_score, set_stars, get_stars, unlock_level, get_unlocked_levels, add_achievement, has_achievement

# Music
try:
    pygame.mixer.music.load(asset_path("img", "music.mp3"))
    pygame.mixer.music.set_volume(st.MUSIC_VOLUME)
    pygame.mixer.music.play(-1)
except (NotImplementedError, Exception):
    pass
set_sfx_volume(st.SFX_VOLUME)



run_narration(screen, clock, bg_image=narration_bg_img)
run_instructions(screen, clock, bg_image=narration_bg_img)

main_menu = True
level = 1
score = 0
target_score = get_target_score(level)
game_state = 0
sparkles = []
portal_particles = []
floating_texts = []
flash_timer = 0
flash_color = (255, 255, 255)
screen_shake = 0
bg_scroll = 0
level_complete_timer = 0
fade_alpha = 255
snowflakes = [Snowflake() for _ in range(40)]
lives = st.LIVES
checkpoint_pos = None
paused = False
level_start_time = 0
deaths_this_level = 0


level3_gifts_dropped = 0
level3_targets = []       # rooftop drop zones
level3_dropped_pos = []   # where gifts were successfully dropped
level3_auto_x = 0.0       # reindeer auto-fly x position
LEVEL3_GIFT_TOTAL = 8
space_was_held = False    # stops holding SPACE from spamming gifts


player = Player(70, 340)
platform_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
checkpoint_group = pygame.sprite.Group()

def init_level3():
    global level3_gifts_dropped, level3_targets, level3_dropped_pos, level3_auto_x
    level3_gifts_dropped = 0
    level3_dropped_pos = []
    level3_auto_x = float(player.rect.x)
    # Drop zones above each rooftop platform (except first and last)
    level3_targets = []
    for plat in platform_group.sprites():
        cx = plat.rect.centerx
        if 200 < cx < 800:  # skip spawn and exit platforms
            level3_targets.append(pygame.Rect(cx - 40, plat.rect.top - 80, 80, 80))

def reset_level(use_checkpoint=False):
    global score, game_state, sparkles, portal_particles, flash_timer, level_complete_timer, checkpoint_pos, floating_texts
    score = 0
    game_state = 0
    sparkles = []
    portal_particles = []
    floating_texts = []
    flash_timer = 0
    level_complete_timer = 0
    build_level(level, platform_group, coin_group, exit_group, enemy_group, checkpoint_group, st.DIFFICULTY)
    if use_checkpoint and checkpoint_pos:
        cx, floor_y = checkpoint_pos
        start_x = int(cx - player.width / 2)
        start_y = int(floor_y - player.height)
        player.reset(start_x, start_y, invincible=60)
    else:
        start_x, start_y = get_player_start(level)
        player.reset(start_x, start_y)
        checkpoint_pos = (start_x, start_y)
    # Level 3 special init
    if level == 3:
        init_level3()

start_button = Button(0, 0, start_img)
exit_button = Button(0, 0, exit_btn_img)
restart_button = Button(SCREEN_WIDTH // 2 - restart_img.get_width() // 2, SCREEN_HEIGHT // 2 + 20, restart_img)

vignette_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
for i in range(100):
    a = int(30 * (1 - i / 100))
    pygame.draw.rect(vignette_surf, (0, 0, 10, a), (0, i, SCREEN_WIDTH, 1))
    pygame.draw.rect(vignette_surf, (0, 0, 10, a), (0, SCREEN_HEIGHT - 1 - i, SCREEN_WIDTH, 1))
    pygame.draw.rect(vignette_surf, (0, 0, 10, a), (i, 0, 1, SCREEN_HEIGHT))
    pygame.draw.rect(vignette_surf, (0, 0, 10, a), (SCREEN_WIDTH - 1 - i, 0, 1, SCREEN_HEIGHT))

run = True
while run:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()
            if event.key == pygame.K_p and not main_menu and level_complete_timer == 0 and game_state != -1:
                paused = not paused
            if event.key == pygame.K_ESCAPE:
                if paused:
                    paused = False
                elif not main_menu and level_complete_timer == 0:
                    main_menu = True
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and main_menu:
                main_menu = False
                level = 1
                lives = st.LIVES
                deaths_this_level = 0
                level_start_time = pygame.time.get_ticks()
                reset_level()
    t = pygame.time.get_ticks()
    shake_mult = 1 if not st.REDUCED_MOTION else 0
    shake_x = (screen_shake * shake_mult * ((1 if t % 2 else -1))) if screen_shake else 0
    shake_y = (screen_shake * shake_mult * ((1 if (t // 2) % 2 else -1))) if screen_shake else 0
    # Parallax background: scroll tied to player movement when in gameplay
    if main_menu:
        bg_scroll = (bg_scroll - 0.4) % (SCREEN_WIDTH * 2)
        scroll_x = int(-bg_scroll) % SCREEN_WIDTH
    else:
        scroll_x = int(player.rect.x * 0.4) % SCREEN_WIDTH  # background moves with reindeer
    active_bg = city_loop_bg if level == 3 else (loop_bg2 if level == 2 else loop_bg)
    bg_portion = active_bg.subsurface(pygame.Rect(scroll_x, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(bg_portion, (int(shake_x), int(shake_y)))

    if main_menu:
        for flake in snowflakes:
            flake.fall(screen)

        # Centered menu panel - both buttons inside
        panel_w, panel_h = 440, 500
        px = SCREEN_WIDTH // 2 - panel_w // 2
        py = SCREEN_HEIGHT // 2 - panel_h // 2
        panel_rect = pygame.Rect(px, py, panel_w, panel_h)
        cx = px + panel_w // 2

        # Panel with subtle shadow
        shadow = pygame.Surface((panel_w + 12, panel_h + 12), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 50), (6, 6, panel_w, panel_h), border_radius=12)
        screen.blit(shadow, (px - 6, py - 6))
        inner = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(inner, (22, 38, 72, 235), (0, 0, panel_w, panel_h), border_radius=10)
        pygame.draw.rect(inner, (70, 110, 170), (0, 0, panel_w, panel_h), 2, border_radius=10)
        pygame.draw.rect(inner, (100, 150, 210, 80), (4, 4, panel_w - 8, panel_h - 8), 1, border_radius=8)
        screen.blit(inner, panel_rect.topleft)

        # Title - centered
        title_w = FONT_TITLE.size("SAVE CHRISTMAS")[0]
        draw_text("SAVE CHRISTMAS", FONT_TITLE, GOLD, cx - title_w // 2, py + 28)

        # Hi-score - centered
        hi_w = FONT_SMALL.size(f"HI-SCORE: {get_high_score()}")[0]
        draw_text(f"HI-SCORE: {get_high_score()}", FONT_SMALL, WHITE, cx - hi_w // 2, py + 72)

        # Buttons - centered, stacked inside panel
        start_x = cx - start_img.get_width() // 2
        exit_x = cx - exit_btn_img.get_width() // 2
        start_y = py + 105
        exit_y = start_y + start_img.get_height() + 22
        start_button.rect.topleft = (start_x, start_y)
        exit_button.rect.topleft = (exit_x, exit_y)

        # Small nav links under the buttons
        menu_items = ["CONTROLS"]
        for i, item in enumerate(menu_items):
            iw = FONT_SMALL.size(item)[0]
            ix = cx - iw // 2
            iy = exit_y + exit_btn_img.get_height() + 10 + i * 26
            color = GOLD if pygame.Rect(ix - 6, iy - 2, iw + 12, 22).collidepoint(pygame.mouse.get_pos()) else (180, 200, 255)
            draw_text(item, FONT_SMALL, color, ix, iy)
            if pygame.mouse.get_pressed()[0] and pygame.Rect(ix - 6, iy - 2, iw + 12, 22).collidepoint(pygame.mouse.get_pos()):
                if item == "CONTROLS":
                    from screens import run_controls_screen
                    run_controls_screen(screen, clock)
                elif item == "SETTINGS":
                    from screens import run_settings_screen
                    run_settings_screen(screen, clock)
                elif item == "CREDITS":
                    from screens import run_credits_screen
                    run_credits_screen(screen, clock)

        # Press start - centered at bottom
        press_w = FONT_SMALL.size("PRESS START")[0]
        draw_text("PRESS START", FONT_SMALL, (180, 200, 255), cx - press_w // 2, py + panel_h - 38)
        if start_button.draw(screen):
            main_menu = False
            level = 1
            lives = st.LIVES
            deaths_this_level = 0
            level_start_time = pygame.time.get_ticks()
            reset_level()
        elif exit_button.draw(screen):
            run = False

    else:
        if paused:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            draw_text("PAUSED", FONT_BIG, GOLD, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 60)
            draw_text("P to resume", FONT_SMALL, WHITE, SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 + 10)
        else:
            for flake in snowflakes:
                flake.fall(screen)


            target_score = get_target_score(level)
            platform_group.draw(screen)
            checkpoint_group.draw(screen)
            coin_group.draw(screen)
            exit_group.draw(screen)
            enemy_group.draw(screen)
            # Ellipse shadow tracks below player (motion tracking effect)
            shadow_surf = pygame.Surface((player.width + 10, 12), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surf, (0, 0, 0, 70), (0, 0, player.width + 10, 12))
            screen.blit(shadow_surf, (player.rect.x - 5, player.rect.bottom - 4))

            # Portal particles around exit when all gifts are collected
            if score >= target_score:
                for exit_obj in exit_group:
                     if random.randint(1, 4) == 1:
                        portal_particles.append(PortalParticle(exit_obj.rect.centerx, exit_obj.rect.centery - 40))

            for p in portal_particles:
                p.update()
                p.draw()

            portal_particles = [p for p in portal_particles if p.life > 0]


            for cp in checkpoint_group:
                if cp.rect.colliderect(player.rect):
                    checkpoint_pos = (cp.rect.centerx, cp.rect.bottom)
                    break

            # ── LEVEL 3 SPECIAL LOOP ──────────────────────────────
            if level == 3 and game_state == 0 and level_complete_timer <= 0:
                # Auto-fly reindeer left to right
                level3_auto_x += 1.2
                player.rect.x = int(level3_auto_x)
                player.rect.y = 150

                # Draw player
                screen.blit(player.images_right[0], player.rect)

                # SPACE to drop a falling gift
                keys = pygame.key.get_pressed()
                if keys[pygame.K_SPACE] and level3_gifts_dropped < LEVEL3_GIFT_TOTAL:
                    # Only spawn one gift per keypress
                    if not space_was_held:
                        level3_dropped_pos.append([float(player.rect.centerx), float(player.rect.bottom)])
                        level3_gifts_dropped += 1
                        for _ in range(8):
                            sparkles.append(Sparkle(player.rect.centerx, player.rect.centery))
                        if drop_fx:
                            drop_fx.play()
                        floating_texts.append(FloatingText(player.rect.centerx, player.rect.top - 20, "GIFT DROPPED!"))
                    space_was_held = True
                else:
                    space_was_held = False

                # Update and draw falling gifts
                for gift in level3_dropped_pos:
                    gift[1] += 4  # fall speed
                    screen.blit(coin_img, (int(gift[0]) - coin_img.get_width() // 2, int(gift[1])))
                    # Sparkle trail while falling
                    if random.randint(1, 4) == 1:
                        sparkles.append(Sparkle(int(gift[0]), int(gift[1])))

                # Update sparkles and floating texts
                for s in sparkles:
                    s.update()
                    s.draw()
                sparkles = [s for s in sparkles if getattr(s, "life", 1) > 0]
                for ft in floating_texts:
                    ft.update()
                    ft.draw(screen, FONT_SMALL)
                floating_texts = [ft for ft in floating_texts if ft.life > 0]

                # HUD
                hud_rect = pygame.Rect(12, 12, 240, 52)
                draw_panel(screen, hud_rect, (15, 25, 55, 230), border_radius=10, border_color=(60, 100, 160))
                draw_text(f"Gifts: {level3_gifts_dropped}/{LEVEL3_GIFT_TOTAL}", FONT_SMALL, GOLD, hud_rect.x + 14, hud_rect.y + 10)
                draw_text(f"Level {level}", FONT_SMALL, WHITE, SCREEN_WIDTH - 100, 22)
                draw_text("SPACE to drop gifts!", FONT_SMALL, WHITE, SCREEN_WIDTH // 2 - 100, 20)

                # Win condition - all gifts dropped and reindeer reached right side
                if level3_gifts_dropped >= LEVEL3_GIFT_TOTAL:
                    game_state = 2

                # Loop reindeer back if flew off without finishing
                if level3_auto_x > SCREEN_WIDTH + 50:
                    level3_auto_x = -50.0

                pygame.display.update()
                clock.tick(FPS)
                continue
            # ── END LEVEL 3 ───────────────────────────────────────

            if level_complete_timer <= 0 and level <= MAX_LEVELS:
                platform_group.update()
                coin_group.update()
                enemy_group.update()
                for s in sparkles:
                    s.update()
                    s.draw()
                sparkles = [s for s in sparkles if getattr(s, "life", 1) > 0]
                
                for ft in floating_texts:
                    ft.update()
                    ft.draw(screen, FONT_SMALL)
                floating_texts = [ft for ft in floating_texts if ft.life > 0]
                
                prev_score = score
                game_state, score, screen_shake, flash_timer, flash_color = player.update(
                    game_state, platform_group, coin_group, enemy_group, exit_group,
                    sparkles, score, target_score, flash_timer, flash_color,
                    difficulty=st.DIFFICULTY, reduced_motion=st.REDUCED_MOTION
                )
                if score > prev_score:
                    # spawn a +1 above where the last coin was collected
                    floating_texts.append(FloatingText(player.rect.centerx, player.rect.top - 10))

                if score > 0 and prev_score == 0 and not has_achievement("first_coin"):
                    add_achievement("first_coin")

            if flash_timer > 0:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((*flash_color, min(80, int(flash_timer * 15))))
                screen.blit(overlay, (0, 0))
                flash_timer = max(0, flash_timer - 0.5)
            if screen_shake > 0:
                screen_shake = max(0, screen_shake - 1)

            hud_rect = pygame.Rect(12, 12, 200, 68)
            draw_panel(screen, hud_rect, (15, 25, 55, 230), border_radius=10, border_color=(60, 100, 160))
            draw_text(f"Gifts: {score}/{target_score}", FONT_SMALL, GOLD, hud_rect.x + 14, hud_rect.y + 10)
            draw_text(f"Lives: {lives}", FONT_SMALL, PINK, hud_rect.x + 14, hud_rect.y + 28)
            # stamina bar
            bar_x = hud_rect.x + 14
            bar_y = hud_rect.y + 46
            bar_w = 120
            bar_h = 8
            fill = int(bar_w * (player.stamina / player.max_stamina))
            pygame.draw.rect(screen, (40, 40, 80), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
            pygame.draw.rect(screen, (80, 180, 255), (bar_x, bar_y, fill, bar_h), border_radius=4)
            draw_text("DASH", FONT_SMALL, (80, 180, 255), bar_x + bar_w + 6, bar_y - 4)
            draw_text(f"Level {level}", FONT_SMALL, WHITE, SCREEN_WIDTH - 100, 22)

            if game_state == -1:
                deaths_this_level += 1
                lives -= 1
                if lives > 0:
                    game_state = 0
                    reset_level(use_checkpoint=True)
                else:
                    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                    overlay.fill((0, 0, 0, 100))
                    screen.blit(overlay, (0, 0))
                    _go = "GAME OVER!"
                    _cx, _cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
                    draw_text(_go, FONT_VICTORY_BIG, (255, 50, 50), _cx - FONT_VICTORY_BIG.size(_go)[0] // 2, _cy - 50, outline_col=(0, 0, 0))
                    if restart_button.draw(screen):
                        level = 1
                        lives = st.LIVES
                        deaths_this_level = 0
                        reset_level()

            elif game_state == 1:
                stars = 1
                if score >= target_score and deaths_this_level == 0:
                    stars = 3
                elif score >= target_score:
                    stars = 2
                set_stars(level, stars)
                unlock_level(level + 1)
                set_high_score(score)
                if not has_achievement("first_win") and level == 1:
                    add_achievement("first_win")
                if deaths_this_level == 0 and level > 1:
                    add_achievement("no_deaths")

                level += 1
                if level > MAX_LEVELS:
                    game_state = 2  # rendering handled by the elif game_state == 2 block below
                else:
                    game_state = 0
                    level_complete_timer = 45
                    deaths_this_level = 0
                    level_start_time = pygame.time.get_ticks()
                

            elif game_state == 2:
                # Game complete - show overlay and restart button every frame
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 30, 60, 180))
                screen.blit(overlay, (0, 0))
                # Falling snow on win screen
                for flake in snowflakes:
                    flake.fall(screen)
                # Win screen sparkle burst
                if random.randint(1, 3) == 1:
                    sparkles.append(Sparkle(random.randint(100, SCREEN_WIDTH - 100), random.randint(50, SCREEN_HEIGHT - 100)))
                if random.randint(1, 4) == 1:
                    sparkles.append(PortalParticle(random.randint(100, SCREEN_WIDTH - 100), random.randint(50, SCREEN_HEIGHT - 100)))
                for s in sparkles:
                    s.update()
                    s.draw()
                sparkles = [s for s in sparkles if getattr(s, "life", 1) > 0]
                _t1 = "CHRISTMAS IS SAVED!"
                _t2 = "All gifts delivered to the children!"
                _cx, _cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
                
                draw_text(_t1, FONT_VICTORY_BIG, GOLD, _cx - FONT_VICTORY_BIG.size(_t1)[0] // 2, _cy - 50, outline_col=(0, 0, 0))
                draw_text(_t2, FONT_VICTORY_SMALL, (180, 220, 255), _cx - FONT_VICTORY_SMALL.size(_t2)[0] // 2, _cy - 5, outline_col=(0, 0, 0))
                # Three gold stars above restart button
                for i in range(3):
                    scx = _cx - 40 + i * 40
                    scy = _cy + 35
                    pts = []
                    for j in range(10):
                        angle = _math.pi / 2 + j * 2 * _math.pi / 10
                        r = 14 if j % 2 == 0 else 7
                        pts.append((scx + int(r * _math.cos(angle)), scy + int(r * _math.sin(angle))))
                    pygame.draw.polygon(screen, GOLD, pts)
                    pygame.draw.polygon(screen, (255, 240, 100), pts, 2)
                if restart_button.draw(screen):
                    level = 1
                    lives = st.LIVES
                    deaths_this_level = 0
                    game_state = 0
                    sparkles = []
                    reset_level()

            if level_complete_timer > 0 and level <= MAX_LEVELS:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 20, 50, 100))
                screen.blit(overlay, (0, 0))
                draw_text("LEVEL COMPLETE!", FONT_BIG, GOLD, SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 40)

                # Animated stars - pop in one by one based on timer countdown
                stars_earned = 1
                if score >= target_score and deaths_this_level == 0:
                    stars_earned = 3
                elif score >= target_score:
                    stars_earned = 2
                stars_to_show = 3 - (level_complete_timer // 15)  # one star every 15 frames
                stars_to_show = max(0, min(stars_to_show, 3))
                for i in range(3):
                    cx = SCREEN_WIDTH // 2 - 60 + i * 60
                    cy = SCREEN_HEIGHT // 2 + 30
                    if i < stars_to_show:
                        # scale pop effect on the frame it appears
                        scale = 1.4 if level_complete_timer == 45 - (i * 15) else 1.0
                        color = GOLD if i < stars_earned else (60, 60, 80)
                        size = int(22 * scale)
                        # draw star as two overlapping polygons
                        points = []
                        
                        for j in range(10):
                            angle = _math.pi / 2 + j * 2 * _math.pi / 10
                            r = size if j % 2 == 0 else size // 2
                            points.append((cx + int(r * _math.cos(angle)), cy + int(r * _math.sin(angle))))
                        pygame.draw.polygon(screen, color, points)
                        if i < stars_earned:
                            pygame.draw.polygon(screen, (255, 240, 100), points, 2)

                level_complete_timer -= 1
                if level_complete_timer <= 0:
                    reset_level()

    if not st.REDUCED_MOTION:
        screen.blit(vignette_surf, (0, 0))

    if fade_alpha > 0:
        fade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        fade.fill((0, 0, 0))
        fade.set_alpha(fade_alpha)
        screen.blit(fade, (0, 0))
        fade_alpha = max(0, fade_alpha - 18)

    pygame.display.update()

pygame.quit()