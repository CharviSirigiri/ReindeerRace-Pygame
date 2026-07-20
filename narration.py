import pygame
import sys
import random
import math
from settings import *

from particles import Snowflake

try:
    FONT_NARRATION = pygame.font.SysFont("Press Start 2P", 19)
except:
    FONT_NARRATION = pygame.font.SysFont("courier", 20)

def _wrap_text(text, font, max_width):
    """Wrap text to fit within max_width."""
    words = text.split()
    lines = []
    current = ""
    for w in words:
        test = current + (" " if current else "") + w
        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines

def _draw_line_in_box(surface, text, font, color, box_rect, y, outline_col=(0, 0, 0)):
    """Draw text centered horizontally within the box."""
    if not text:
        return
    base = font.render(text, True, color)
    outline = font.render(text, True, outline_col)
    x = box_rect.centerx - base.get_width() // 2
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
        surface.blit(outline, (x + dx, y + dy))
    surface.blit(base, (x, y))



def run_narration(screen_obj, clock, bg_image):
    story_lines = [
        "Christmas is in danger...",
        "The Grinch is trying to steal all the presents!",
        "A brave reindeer must collect every gift from the Grinch.",
        "Then fly over the city and drop all gifts to the children below.",
        "Save Christmas!",
    ]
    prompt_line = "Press ENTER to continue"

    # Pre-wrap all story lines for layout (header + story + gap + prompt)
    box_w, box_h = 640, 280
    pad_x, pad_y = 44, 32
    text_width = box_w - pad_x * 2
    header = ["MISSION"]
    wrapped_story = []
    for line in story_lines:
        wrapped_story.extend(_wrap_text(line, FONT_NARRATION, text_width))
    wrapped_prompt = _wrap_text(prompt_line, FONT_NARRATION, text_width)
    all_lines = header + wrapped_story + [""] + wrapped_prompt

    current_line = 0
    char_index = 0
    displayed_lines = [""] * len(all_lines)
    typing_speed = 2
    timer = 0

    snowflakes = [Snowflake() for _ in range(50)]
    tw, th = title_main_img.get_size()
    title_small = pygame.transform.smoothscale(title_main_img, (int(tw * 0.7), int(th * 0.7)))

    # Fade in
    fade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    fade.fill((0, 0, 0))
    for alpha in range(255, -1, -15):
        screen_obj.blit(bg_image, (0, 0))
        for flake in snowflakes:
            flake.fall(screen_obj)
        title_rect = title_small.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 120))
        screen_obj.blit(title_small, title_rect)
        fade.set_alpha(alpha)
        screen_obj.blit(fade, (0, 0))
        pygame.display.update()
        clock.tick(FPS)

    waiting = True
    while waiting:
        screen_obj.blit(bg_image, (0, 0))

        for flake in snowflakes:
            flake.fall(screen_obj)

        title_rect = title_small.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 120))
        screen_obj.blit(title_small, title_rect)

        # Narration panel with padding
        box_surface = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        pygame.draw.rect(box_surface, (0, 0, 25, 180), (0, 0, box_w, box_h), border_radius=16)
        pygame.draw.rect(box_surface, (80, 120, 180, 100), (0, 0, box_w, box_h), 2, border_radius=16)
        box_rect = box_surface.get_rect(center=(SCREEN_WIDTH // 2, 385))
        screen_obj.blit(box_surface, box_rect)

        # Typewriter effect
        timer += 1
        if current_line < len(all_lines):
            if timer >= typing_speed:
                if all_lines[current_line] and char_index < len(all_lines[current_line]):
                    displayed_lines[current_line] += all_lines[current_line][char_index]
                    char_index += 1
                else:
                    current_line += 1
                    char_index = 0
                timer = 0

        # Draw text centered in box (horiz + vertical center, all white)
        line_height = 28
        gap_height = 12
        total_h = sum(line_height if ln else gap_height for ln in all_lines)
        ty = box_rect.centery - total_h // 2
        for i, line in enumerate(displayed_lines):
            if line:
                _draw_line_in_box(screen_obj, line, FONT_NARRATION, WHITE,
                                  box_rect, ty, outline_col=(0, 0, 0))
            ty += line_height if line else gap_height

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if current_line >= len(all_lines):
                        waiting = False
                    else:
                        for i in range(current_line, len(all_lines)):
                            displayed_lines[i] = all_lines[i]
                        current_line = len(all_lines)
                        waiting = False

        pygame.display.update()
        clock.tick(FPS)

    # Fade out
    fade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    fade.fill((0, 0, 0))
    for alpha in range(0, 256, 12):
        fade.set_alpha(alpha)
        screen_obj.blit(bg_image, (0, 0))
        for flake in snowflakes:
            flake.fall(screen_obj)
        title_rect = title_small.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 120))
        screen_obj.blit(title_small, title_rect)
        screen_obj.blit(fade, (0, 0))
        pygame.display.update()
        clock.tick(FPS)


def run_instructions(screen_obj, clock, bg_image):
    """Instructions screen - same box, fonts, and style as narration."""
    box_w, box_h = 640, 460
    pad_x, pad_y = 80, 40
    text_width = box_w - pad_x * 2
    line_height = 28
    gap_height = 12

    raw_lines = [
        "HOW TO PLAY",
        "",
        "OBJECTIVE",
        "Levels 1 & 2: Collect all hidden gifts and reach the Exit.",
        "Level 3: Fly over the city and press SPACE to drop all 8 gifts to the children below!",
        "CONTROLS",
        "Left/Right Arrows: Move",
        "Space Bar: Jump",
        "X: Dash",
        "",
        "SURVIVAL GUIDE",
        "Watch Your Step: Stay on platforms! Falling costs a life.",
        "The Grinch: Touching from the side or bottom costs a life.",
        "Combat: Jump on the Grinch's head to defeat him.",
        "",
        "Press ENTER to continue",
    ]

    all_lines = []
    for line in raw_lines:
        if not line:
            all_lines.append(("", gap_height))
        elif line in ("HOW TO PLAY", "OBJECTIVE", "CONTROLS", "SURVIVAL GUIDE", "Press ENTER to continue"):
            all_lines.append((line, line_height))
        else:
            for wrapped in _wrap_text(line, FONT_NARRATION, text_width):
                all_lines.append((wrapped, line_height))

    displayed_lines = [""] * len(all_lines)
    current_line = 0
    char_index = 0
    typing_speed = 2
    timer = 0

    snowflakes = [Snowflake() for _ in range(50)]
    tw, th = title_sub_img.get_size()
    subtitle_small = pygame.transform.smoothscale(title_sub_img, (int(tw * 0.7), int(th * 0.7)))

    # Fade in (match narration)
    fade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    fade.fill((0, 0, 0))
    for alpha in range(255, -1, -15):
        screen_obj.blit(bg_image, (0, 0))
        for flake in snowflakes:
            flake.fall(screen_obj)
        subtitle_rect = subtitle_small.get_rect(center=(SCREEN_WIDTH // 2, 55))
        screen_obj.blit(subtitle_small, subtitle_rect)
        box_surface = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        pygame.draw.rect(box_surface, (0, 0, 25, 180), (0, 0, box_w, box_h), border_radius=16)
        pygame.draw.rect(box_surface, (80, 120, 180, 100), (0, 0, box_w, box_h), 2, border_radius=16)
        box_rect = box_surface.get_rect(center=(SCREEN_WIDTH // 2, 320))
        screen_obj.blit(box_surface, box_rect)
        fade.set_alpha(alpha)
        screen_obj.blit(fade, (0, 0))
        pygame.display.update()
        clock.tick(FPS)

    waiting = True
    scroll_offset = 0
    total_h = sum(lh for _, lh in all_lines)
    max_scroll = max(0, total_h - box_h + pad_y * 2)

    while waiting:
        screen_obj.blit(bg_image, (0, 0))
        for flake in snowflakes:
            flake.fall(screen_obj)

        subtitle_rect = subtitle_small.get_rect(center=(SCREEN_WIDTH // 2, 55))
        screen_obj.blit(subtitle_small, subtitle_rect)

        box_surface = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        pygame.draw.rect(box_surface, (0, 0, 25, 180), (0, 0, box_w, box_h), border_radius=16)
        pygame.draw.rect(box_surface, (80, 120, 180, 100), (0, 0, box_w, box_h), 2, border_radius=16)
        box_rect = box_surface.get_rect(center=(SCREEN_WIDTH // 2, 320))
        screen_obj.blit(box_surface, box_rect)

        # Typewriter effect (same as narration)
        timer += 1
        if current_line < len(all_lines):
            if timer >= typing_speed:
                full_text, _ = all_lines[current_line]
                if not full_text:
                    current_line += 1
                elif char_index < len(full_text):
                    displayed_lines[current_line] += full_text[char_index]
                    char_index += 1
                else:
                    current_line += 1
                    char_index = 0
                timer = 0

        ty = box_rect.y + pad_y - scroll_offset
        clip = screen_obj.get_clip()
        screen_obj.set_clip(box_rect)
        for i, (_, lh) in enumerate(all_lines):
            if displayed_lines[i]:
                _draw_line_in_box(screen_obj, displayed_lines[i], FONT_NARRATION, WHITE, box_rect, ty, outline_col=(0, 0, 0))
            ty += lh
        screen_obj.set_clip(clip)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if current_line >= len(all_lines):
                        waiting = False
                    else:
                        for i in range(current_line, len(all_lines)):
                            displayed_lines[i] = all_lines[i][0]
                        current_line = len(all_lines)
                        waiting = False
                elif event.key == pygame.K_UP and max_scroll > 0:
                    scroll_offset = max(0, scroll_offset - 30)
                elif event.key == pygame.K_DOWN and max_scroll > 0:
                    scroll_offset = min(max_scroll, scroll_offset + 30)

        pygame.display.update()
        clock.tick(FPS)