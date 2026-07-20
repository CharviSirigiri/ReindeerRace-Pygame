"""Screens: Controls, Credits, Settings, Level Select."""
import pygame
from settings import *
from ui import draw_text, draw_panel, Button

def run_controls_screen(screen_obj, clock):
    back_btn = Button(SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT - 80, exit_btn_img)
    lines = [
        "CONTROLS",
        "",
        "LEFT / RIGHT  Move",
        "SPACE  Jump / Double Jump",
        "X  Dash",
        "P  Pause",
        "ESC  Menu",
    ]
    waiting = True
    while waiting:
        screen_obj.fill((15, 25, 55))
        draw_panel(screen_obj, pygame.Rect(SCREEN_WIDTH // 2 - 200, 80, 400, 400), (0, 0, 40, 200), 16, (70, 110, 170))
        y = 120
        for line in lines:
            if line:
                draw_text(line, FONT_MEDIUM if line == "CONTROLS" else FONT_SMALL, WHITE if line == "CONTROLS" else GOLD, SCREEN_WIDTH // 2 - 180, y)
            y += 42
        if back_btn.draw(screen_obj):
            waiting = False
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit"
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                waiting = False
        pygame.display.update()
        clock.tick(FPS)
    return "menu"

def run_credits_screen(screen_obj, clock):
    back_btn = Button(SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT - 80, exit_btn_img)
    lines = [
        "CREDITS",
        "",
        "A Winter Reindeer Adventure",
        "Save Christmas!",
        "",
        "Made with Pygame",
        "Thanks for playing!",
    ]
    waiting = True
    while waiting:
        screen_obj.fill((15, 25, 55))
        draw_panel(screen_obj, pygame.Rect(SCREEN_WIDTH // 2 - 220, 80, 440, 380), (0, 0, 40, 200), 16, (70, 110, 170))
        y = 120
        for line in lines:
            if line:
                draw_text(line, FONT_MEDIUM if line == "CREDITS" else FONT_SMALL, WHITE if line == "CREDITS" else GOLD, SCREEN_WIDTH // 2 - 200, y)
            y += 45
        if back_btn.draw(screen_obj):
            waiting = False
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit"
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                waiting = False
        pygame.display.update()
        clock.tick(FPS)
    return "menu"

def run_settings_screen(screen_obj, clock):
    from settings import DIFFICULTY, REDUCED_MOTION, MUSIC_VOLUME, SFX_VOLUME
    import settings as st
    back_btn = Button(SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT - 80, exit_btn_img)
    diffs = ["easy", "normal", "hard"]
    diff_idx = diffs.index(getattr(st, "DIFFICULTY", "normal"))
    reduced = getattr(st, "REDUCED_MOTION", False)
    waiting = True
    while waiting:
        screen_obj.fill((15, 25, 55))
        draw_panel(screen_obj, pygame.Rect(SCREEN_WIDTH // 2 - 200, 80, 400, 350), (0, 0, 40, 200), 16, (70, 110, 170))
        draw_text("SETTINGS", FONT_MEDIUM, WHITE, SCREEN_WIDTH // 2 - 80, 100)
        draw_text(f"Difficulty: {st.DIFFICULTY}", FONT_SMALL, GOLD, SCREEN_WIDTH // 2 - 180, 160)
        draw_text(f"Reduced Motion: {'On' if st.REDUCED_MOTION else 'Off'}", FONT_SMALL, GOLD, SCREEN_WIDTH // 2 - 180, 200)
        draw_text("(Change in code: settings.py)", FONT_SMALL, (100, 100, 100), SCREEN_WIDTH // 2 - 180, 250)
        if back_btn.draw(screen_obj):
            waiting = False
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit"
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    waiting = False
                elif e.key == pygame.K_LEFT and diff_idx > 0:
                    diff_idx -= 1
                    st.DIFFICULTY = diffs[diff_idx]
                elif e.key == pygame.K_RIGHT and diff_idx < 2:
                    diff_idx += 1
                    st.DIFFICULTY = diffs[diff_idx]
                elif e.key == pygame.K_r:
                    st.REDUCED_MOTION = not st.REDUCED_MOTION
        pygame.display.update()
        clock.tick(FPS)
    return "menu"

def run_level_select_screen(screen_obj, clock):
    from save_data import get_unlocked_levels, get_stars
    unlocked = get_unlocked_levels()
    back_btn = Button(SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT - 80, exit_btn_img)
    level_buttons = []
    for i in range(1, MAX_LEVELS + 1):
        x = 150 + (i - 1) * 180
        y = 250
        level_buttons.append((i, pygame.Rect(x, y, 120, 80)))
    selected = None
    waiting = True
    while waiting:
        screen_obj.fill((15, 25, 55))
        draw_panel(screen_obj, pygame.Rect(SCREEN_WIDTH // 2 - 350, 60, 700, 450), (0, 0, 40, 200), 16, (70, 110, 170))
        draw_text("LEVEL SELECT", FONT_BIG, GOLD, SCREEN_WIDTH // 2 - 140, 90)
        pygame.draw.rect(screen_obj, (0, 0, 0, 0), (0, 0, 0, 0))
        pos = pygame.mouse.get_pos()
        for i, rect in level_buttons:
            if i <= unlocked:
                color = (100, 180, 100) if rect.collidepoint(pos) else (60, 120, 60)
                pygame.draw.rect(screen_obj, color, rect, border_radius=8)
                draw_text(f"Level {i}", FONT_MEDIUM, WHITE, rect.x + 30, rect.y + 15)
                star_count = get_stars(i)
                draw_text("★" * star_count + "☆" * (3 - star_count), FONT_SMALL, GOLD, rect.x + 25, rect.y + 50)
                if rect.collidepoint(pos) and pygame.mouse.get_pressed()[0]:
                    selected = i
                    waiting = False
            else:
                pygame.draw.rect(screen_obj, (40, 40, 40), rect, border_radius=8)
                draw_text("Locked", FONT_SMALL, (100, 100, 100), rect.x + 35, rect.y + 30)
        if back_btn.draw(screen_obj):
            waiting = False
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit", None
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                waiting = False
        pygame.display.update()
        clock.tick(FPS)
    return "play" if selected else "menu", selected
