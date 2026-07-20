import random
from platforms import Platform, MovingPlatform, Coin, Exit, Checkpoint
from enemies import Enemy, FlyingEnemy

LEVEL_DATA = {
    1: {"coins": 3, "start": (70, 340), "platforms": [
            (40, 420, 140),
            (240, 385, 120, 50, 1.0),
            (430, 330, 140, 55, 1.1),
            (610, 250, 150),
        ],
        "coin_pos": [(280, 350), (500, 290), (665, 215)], "exit": (790, 250), "enemies": [("ground", 130, 1.1)], "checkpoints": [(350, 385)], "secret": (100, 300)},
    2: {"coins": 5, "start": (70, 350), "platforms": [
            (30, 430, 120),
            (170, 390, 100, 55, 1.1),
            (310, 350, 100, 50, 1.2),
            (450, 310, 110, 60, 1.0),
            (600, 260, 100),
            (740, 220, 120),
        ],
        "coin_pos": [(200, 350), (340, 310), (480, 270), (630, 220), (755, 185)], "exit": (805, 220), "enemies": [("ground", 140, 1.0), ("ground", 120, 1.1)],
        "checkpoints": [(400, 310)]},
    3: {"coins": 4, "start": (70, 150), "platforms": [],
    "coin_pos": [],
    "exit": (9999, 9999),
    "enemies": [],
    "checkpoints": [],
    "secret": None},
    
}

def get_target_score(level_number):
    return LEVEL_DATA.get(level_number, {}).get("coins", 3)

def get_player_start(level_number):
    d = LEVEL_DATA.get(level_number, {})
    return d.get("start", (70, 340))

def get_checkpoints(level_number):
    return LEVEL_DATA.get(level_number, {}).get("checkpoints", [])

def get_secret_coin(level_number):
    return LEVEL_DATA.get(level_number, {}).get("secret")

def build_level(level_number, platform_group, coin_group, exit_group, enemy_group, checkpoint_group=None, difficulty="normal"):
    platform_group.empty()
    coin_group.empty()
    exit_group.empty()
    enemy_group.empty()
    if checkpoint_group:
        checkpoint_group.empty()

    d = LEVEL_DATA.get(level_number, {})
    if not d:
        return

    speed_mult = 0.8 if difficulty == "easy" else (1.2 if difficulty == "hard" else 1.0)
    enemy_count = len(d.get("enemies", []))
    if difficulty == "easy":
        enemy_count = max(0, enemy_count - 1)

    for p in d.get("platforms", []):
        if len(p) >= 5:
            platform_group.add(MovingPlatform(p[0], p[1], p[2], move_range=p[3], speed=p[4]))
        else:
            platform_group.add(Platform(p[0], p[1], p[2]))

    for c in d.get("coin_pos", []):
        coin_group.add(Coin(c[0], c[1]))

    secret = get_secret_coin(level_number)
    if secret:
        coin_group.add(Coin(secret[0], secret[1]))

    for cp in d.get("checkpoints", []):
        if checkpoint_group is not None:
            checkpoint_group.add(Checkpoint(cp[0], cp[1]))

    static_platforms = [p for p in platform_group.sprites() if not isinstance(p, MovingPlatform)]
    static_platforms = static_platforms[1:]  # skip first platform (player spawn)
    exit_pos = d.get("exit", (790, 250))
    exit_x = exit_pos[0]
    # Exclude platforms near the exit so Grinch doesn't clash with bag
    def _far_from_exit(plat):
        return plat.rect.centerx < exit_x - 100
    enemy_platforms = [p for p in static_platforms if _far_from_exit(p)] if static_platforms else []
    if not enemy_platforms:
        enemy_platforms = static_platforms
    used_platforms = set()
    for i, e in enumerate(d.get("enemies", [])):
        if difficulty == "easy" and i >= 1:
            continue
        etype, move_range, speed = e[0], e[1], e[2]
        if etype == "flying":
            platforms = [p for p in platform_group.sprites() if _far_from_exit(p)]
        else:
            platforms = enemy_platforms
        available = [p for p in platforms if id(p) not in used_platforms]
        if not available:
            continue
        p = random.choice(available)
        used_platforms.add(id(p))
        if etype == "flying":
            x = (p.rect.left + p.rect.right) // 2
            y = p.rect.top - 70
            enemy_group.add(FlyingEnemy(x, y, move_range, speed * speed_mult))
        else:
            x = random.randint(p.rect.left, p.rect.right - 65)
            y = p.rect.top - 80
            enemy_group.add(Enemy(x, y, move_range, speed * speed_mult))

    if level_number != 3:
        exit_group.add(Exit(exit_pos[0], exit_pos[1]))
