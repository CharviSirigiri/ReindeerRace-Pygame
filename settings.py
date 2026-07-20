import os
import pygame

# Path setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
def asset_path(*parts):
    return os.path.join(BASE_DIR, *parts)

pygame.init()
try:
    pygame.mixer.init()
    MIXER_AVAILABLE = True
except (NotImplementedError, Exception):
    MIXER_AVAILABLE = False

# Settings
FPS = 60
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
GAME_TITLE = "Reindeer Race"
MAX_LEVELS = 3

# Game options (loaded from save, can be overridden)
DIFFICULTY = "normal"  # easy, normal, hard
LIVES = 3
REDUCED_MOTION = False
MUSIC_VOLUME = 0.7
SFX_VOLUME = 1.0

clock = pygame.time.Clock()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

def get_screen_shake_mult():
    return 0 if REDUCED_MOTION else 1

# Colours - unified winter palette
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GOLD = (255, 215, 0)
MARIGOLD = (255, 140, 0)
PINK = (255, 105, 180)
DEEP_BLUE = (15, 25, 55)
SOFT_BLUE = (40, 70, 120)
OUTLINE_COLOR = (20, 40, 80)  # Softer than black for text

# Sound FX
if MIXER_AVAILABLE:
    jump_fx = pygame.mixer.Sound(asset_path("img", "jump.wav"))
    game_over_fx = pygame.mixer.Sound(asset_path("img", "game_over.wav"))
    coin_fx = pygame.mixer.Sound(asset_path("img", "coin.wav"))
    try:
        level_complete_fx = pygame.mixer.Sound(asset_path("img", "coin.wav"))
    except:
        level_complete_fx = pygame.mixer.Sound(asset_path("img", "jump.wav"))
    try:
        stomp_fx = pygame.mixer.Sound(asset_path("img", "dead.mp3"))
    except:
        stomp_fx = jump_fx
    try:
        drop_fx = pygame.mixer.Sound(asset_path("img", "drop.mp3"))
    except:
        drop_fx = coin_fx
else:
    jump_fx = game_over_fx = coin_fx = level_complete_fx = stomp_fx = drop_fx = None

def set_sfx_volume(vol):
    if vol is None:
        return
    if jump_fx:
        jump_fx.set_volume(vol)
    if game_over_fx:
        game_over_fx.set_volume(vol)
    if coin_fx:
        coin_fx.set_volume(vol)
    if level_complete_fx:
        level_complete_fx.set_volume(vol)
    if stomp_fx:
        stomp_fx.set_volume(vol)
    if drop_fx:
        drop_fx.set_volume(vol)

# Fonts - pixel/game font throughout
def _pixel_font(size):
    for name in ["Press Start 2P", "VT323", "Silkscreen", "Pixelify Sans", "Courier"]:
        try:
            return pygame.font.SysFont(name, size)
        except:
            pass
    return pygame.font.SysFont("courier", size, bold=True)

try:
    PIXEL_FONT_PATH = asset_path("img", "advanced_pixel-7.ttf")
    if os.path.exists(PIXEL_FONT_PATH):
        FONT_BIG = pygame.font.Font(PIXEL_FONT_PATH, 48)
        FONT_MEDIUM = pygame.font.Font(PIXEL_FONT_PATH, 28)
        FONT_SMALL = pygame.font.Font(PIXEL_FONT_PATH, 20)
        FONT_TITLE = pygame.font.Font(PIXEL_FONT_PATH, 56)
        FONT_TYPEWRITER = pygame.font.Font(PIXEL_FONT_PATH, 24)
    else:
        raise FileNotFoundError
except:
    FONT_BIG = _pixel_font(36)
    FONT_MEDIUM = _pixel_font(24)
    FONT_SMALL = _pixel_font(18)
    FONT_TITLE = _pixel_font(42)
    FONT_TYPEWRITER = _pixel_font(20)

# Gamey arcade font for victory screen (Press Start 2P style)
try:
    FONT_VICTORY_BIG = pygame.font.SysFont("Press Start 2P", 32)
    FONT_VICTORY_SMALL = pygame.font.SysFont("Press Start 2P", 16)
except:
    FONT_VICTORY_BIG = FONT_BIG
    FONT_VICTORY_SMALL = FONT_MEDIUM

# Assets - Matches file names in your 'img' folder
# Note: load_btn.png, save_btn.png are unused but kept in img folder
_bg_raw = pygame.image.load(asset_path("img", "sky.png")).convert()
bg_img = pygame.transform.scale(_bg_raw, (SCREEN_WIDTH, SCREEN_HEIGHT))
_bg2_raw = pygame.image.load(asset_path("img", "sky.jpg")).convert()
bg2_img = pygame.transform.scale(_bg2_raw, (SCREEN_WIDTH, SCREEN_HEIGHT))
city_bg_raw = pygame.image.load(asset_path("img", "city.png")).convert()
city_bg_img = pygame.transform.scale(city_bg_raw, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Seamless loop version for city (level 3)
city_loop_bg = pygame.Surface((SCREEN_WIDTH * 2, SCREEN_HEIGHT))
city_loop_bg.blit(city_bg_img, (0, 0))
city_loop_bg.blit(city_bg_img, (SCREEN_WIDTH, 0))

# Level 1 background - seamless with blended seam
loop_bg = pygame.Surface((SCREEN_WIDTH * 2, SCREEN_HEIGHT))
loop_bg.blit(bg_img, (0, 0))
loop_bg.blit(bg_img, (SCREEN_WIDTH, 0))
def _smoothstep(t):
    return t * t * (3 - 2 * t)
_seam = 50
for x in range(_seam):
    t = x / max(_seam - 1, 1)
    blend = _smoothstep(t)
    for y in range(SCREEN_HEIGHT):
        left = loop_bg.get_at((SCREEN_WIDTH - _seam + x, y))
        right = loop_bg.get_at((SCREEN_WIDTH + x, y))
        r = int(left[0] * (1 - blend) + right[0] * blend)
        g = int(left[1] * (1 - blend) + right[1] * blend)
        b = int(left[2] * (1 - blend) + right[2] * blend)
        loop_bg.set_at((SCREEN_WIDTH - _seam + x, y), (r, g, b))
        loop_bg.set_at((SCREEN_WIDTH + x, y), (r, g, b))

# Level 2 background - seamless, no blend needed
loop_bg2 = pygame.Surface((SCREEN_WIDTH * 2, SCREEN_HEIGHT))
loop_bg2.blit(bg2_img, (0, 0))
loop_bg2.blit(bg2_img, (SCREEN_WIDTH, 0))

narration_bg_img = pygame.transform.scale(pygame.image.load(asset_path("img", "background.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

# UI / Titles - scale to fit 900x600 screen (images are 700-1100px native)
def scale_btn(img, max_w=220, max_h=130):
    w, h = img.get_size()
    scale = min(max_w / w, max_h / h, 1.0)
    if scale < 1:
        new_w, new_h = int(w * scale), int(h * scale)
        return pygame.transform.smoothscale(img, (new_w, new_h))
    return img

restart_img = scale_btn(pygame.image.load(asset_path("img", "restart_btn.png")).convert_alpha())
start_img = scale_btn(pygame.image.load(asset_path("img", "start_btn.png")).convert_alpha())
exit_btn_img = scale_btn(pygame.image.load(asset_path("img", "exit_btn.png")).convert_alpha())

# Heading scaled for narration (1024x687 -> fit width 500)
title_main_img = pygame.image.load(asset_path("img", "heading.png")).convert_alpha()
tw, th = title_main_img.get_size()
if tw > 500:
    title_main_img = pygame.transform.smoothscale(title_main_img, (500, int(500 * th / tw)))
title_sub_img = pygame.image.load(asset_path("img", "heading-title.png")).convert_alpha()
tw2, th2 = title_sub_img.get_size()
if tw2 > 500:
    title_sub_img = pygame.transform.smoothscale(title_sub_img, (500, int(500 * th2 / tw2)))

# Game Objects - scale oversized assets (exit 1085x1248, coin 1138x1248)
def scale_asset(img, max_w, max_h):
    w, h = img.get_size()
    scale = min(max_w / w, max_h / h, 1.0)
    if scale < 1:
        return pygame.transform.smoothscale(img, (int(w * scale), int(h * scale)))
    return img

platform_base_img = pygame.image.load(asset_path("img", "platform.png")).convert_alpha()
coin_img = scale_asset(pygame.image.load(asset_path("img", "coin.png")).convert_alpha(), 50, 50)
exit_game_img = scale_asset(pygame.image.load(asset_path("img", "exit.png")).convert_alpha(), 120, 140)
_ghost = pygame.image.load(asset_path("img", "ghost.png")).convert_alpha()
dead_img = pygame.transform.smoothscale(_ghost, (48, 80))
_grinch = pygame.image.load(asset_path("img", "grinch.png")).convert_alpha()
grinch_img = pygame.transform.smoothscale(_grinch, (65, 80))

# Player
player_frames_right = []
player_frames_left = []
for num in range(1, 7):
    img = pygame.image.load(asset_path("img", f"guys{num}.png")).convert_alpha()
    img = pygame.transform.scale(img, (48, 80))
    player_frames_right.append(img)
    player_frames_left.append(pygame.transform.flip(img, True, False))