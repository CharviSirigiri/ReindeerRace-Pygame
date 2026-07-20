"""Save/load high scores, stars, unlocked levels, achievements."""
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_PATH = os.path.join(BASE_DIR, "save_data.json")

DEFAULT = {
    "high_score": 0,
    "best_time": 999999,
    "stars": {},  # level_num -> 1/2/3
    "unlocked_levels": 1,
    "achievements": [],  # ["first_coin", "no_deaths", ...]
}

def load():
    try:
        with open(SAVE_PATH, "r") as f:
            data = json.load(f)
            for k, v in DEFAULT.items():
                if k not in data:
                    data[k] = v
            return data
    except:
        return DEFAULT.copy()

def save(data):
    try:
        with open(SAVE_PATH, "w") as f:
            json.dump(data, f, indent=2)
    except:
        pass

def get_high_score():
    return load().get("high_score", 0)

def set_high_score(score):
    d = load()
    if score > d.get("high_score", 0):
        d["high_score"] = score
        save(d)

def get_stars(level):
    return load().get("stars", {}).get(str(level), 0)

def set_stars(level, stars):
    d = load()
    if "stars" not in d:
        d["stars"] = {}
    old = d["stars"].get(str(level), 0)
    if stars > old:
        d["stars"][str(level)] = stars
        save(d)

def get_unlocked_levels():
    return load().get("unlocked_levels", 1)

def unlock_level(level):
    d = load()
    if level > d.get("unlocked_levels", 1):
        d["unlocked_levels"] = level
        save(d)

def has_achievement(name):
    return name in load().get("achievements", [])

def add_achievement(name):
    d = load()
    if "achievements" not in d:
        d["achievements"] = []
    if name not in d["achievements"]:
        d["achievements"].append(name)
        save(d)
        return True
    return False
