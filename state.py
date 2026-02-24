"""
Shared state via JSON file + scoring.
"""

import json
import os
import re
import threading

STATE_FILE = os.path.join(os.path.dirname(__file__), ".cata_state.json")
_lock = threading.Lock()

DEFAULT_GRAPES = [
    "Tempranillo", "Garnacha", "Monastrell", "Bobal", "Mencía",
    "Cabernet Sauvignon", "Merlot", "Syrah", "Pinot Noir",
    "Verdejo", "Albariño", "Godello", "Viura", "Macabeo",
    "Chardonnay", "Sauvignon Blanc", "Riesling", "Moscatel",
    "Palomino Fino", "Pedro Ximénez", "Cariñena", "Graciano",
]

DEFAULT_ORIGINS = [
    "Rioja", "Ribera del Duero", "Priorat", "Rías Baixas",
    "Rueda", "Penedès", "Somontano", "Toro", "Jumilla",
    "Bierzo", "Valdepeñas", "La Mancha", "Utiel-Requena",
    "Cava", "Jerez", "Navarra", "Campo de Borja",
    "Montsant", "Terra Alta", "Empordà", "Yecla",
    "Valencia", "Alicante", "Cariñena", "Calatayud",
    "Txakoli", "Manchuela", "Méntrida", "Vinos de Madrid",
    "Ribeiro", "Monterrei", "Bullas",
]

DEFAULT_AGINGS = [
    "Joven", "Crianza", "Reserva", "Gran Reserva",
]

DEFAULT_STATE = {
    "wines": [],
    "participants": [],
    "guesses": {},
    "revealed": [],
    "started": False,
    "options": {
        "grapes": DEFAULT_GRAPES,
        "origins": DEFAULT_ORIGINS,
        "agings": DEFAULT_AGINGS,
    },
    "lang": "es",
}


def load_state() -> dict:
    with _lock:
        try:
            if os.path.exists(STATE_FILE):
                with open(STATE_FILE, "r") as f:
                    s = json.load(f)
                # Ensure options exist
                if "options" not in s:
                    s["options"] = DEFAULT_STATE["options"].copy()
                for k in ("grapes", "origins", "agings"):
                    if k not in s["options"]:
                        s["options"][k] = DEFAULT_STATE["options"][k][:]
                if "lang" not in s:
                    s["lang"] = "es"
                return s
        except (json.JSONDecodeError, IOError):
            pass
    return json.loads(json.dumps(DEFAULT_STATE))


def save_state(state: dict):
    with _lock:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)


def reset_state():
    save_state(json.loads(json.dumps(DEFAULT_STATE)))


# ============================================================
# Scoring
# ============================================================
# Grape (25): exact match any grape = 25, partial overlap = proportional
# Origin (25): exact = 25, contains = 10
# Aging (20): exact = 20
# Rating (10): diff <=0.5 = 10, <=1 = 5
# Alcohol (10): diff <=0.5 = 10, <=1 = 6, <=2 = 3
# Price (10): diff <=3€ = 10, <=6€ = 6, <=12€ = 3

def calc_score(guess: dict, actual: dict) -> dict:
    total = 0; max_s = 0; bd = {}

    # --- Grape (25 pts) ---
    if actual.get("grape"):
        max_s += 25
        g_set = _split_grapes(guess.get("grape", ""))
        a_set = _split_grapes(actual["grape"])
        if g_set and a_set:
            overlap = len(g_set & a_set)
            if overlap == len(a_set):
                bd["grape"] = 25
            elif overlap > 0:
                bd["grape"] = int(25 * overlap / len(a_set))
            else:
                # Check partial matches
                partial = sum(1 for g in g_set for a in a_set if g in a or a in g)
                bd["grape"] = min(12, int(25 * partial / len(a_set))) if partial else 0
        else:
            bd["grape"] = 0
        total += bd["grape"]

    # --- Origin (25 pts) ---
    if actual.get("origin"):
        max_s += 25
        g = (guess.get("origin") or "").lower().strip()
        a = actual["origin"].lower().strip()
        if g and a:
            if g == a: bd["origin"] = 25
            elif g in a or a in g: bd["origin"] = 10
            else: bd["origin"] = 0
        else: bd["origin"] = 0
        total += bd["origin"]

    # --- Aging (20 pts) ---
    if actual.get("aging"):
        max_s += 20
        g = (guess.get("aging") or "").lower().strip()
        a = actual["aging"].lower().strip()
        bd["aging"] = 20 if g == a else 0
        total += bd["aging"]

    # --- Rating (10 pts) ---
    if actual.get("rating"):
        max_s += 10
        try:
            d = abs(float(guess.get("rating") or 0) - float(actual["rating"]))
            bd["rating"] = 10 if d <= 0.5 else 5 if d <= 1 else 0
        except (ValueError, TypeError):
            bd["rating"] = 0
        total += bd["rating"]

    # --- Alcohol (10 pts) ---
    if actual.get("alcohol"):
        max_s += 10
        try:
            d = abs(float(guess.get("alcohol") or 0) - float(actual["alcohol"]))
            bd["alcohol"] = 10 if d <= 0.5 else 6 if d <= 1 else 3 if d <= 2 else 0
        except (ValueError, TypeError):
            bd["alcohol"] = 0
        total += bd["alcohol"]

    # --- Price (10 pts) ---
    if actual.get("price"):
        max_s += 10
        try:
            d = abs(float(guess.get("price") or 0) - float(actual["price"]))
            bd["price"] = 10 if d <= 3 else 6 if d <= 6 else 3 if d <= 12 else 0
        except (ValueError, TypeError):
            bd["price"] = 0
        total += bd["price"]

    ms = max_s or 100
    return {"total": total, "max_score": ms, "pct": round(total / ms * 100, 1), "breakdown": bd}


def _split_grapes(s):
    if not s: return set()
    return {x.strip().lower() for x in re.split(r"[,/&+\-]", s) if x.strip()}


def get_rankings(state: dict) -> list:
    rankings = {}
    for p in state["participants"]:
        rankings[p] = {"total": 0, "max_total": 0, "per_wine": []}
        for i, wine in enumerate(state["wines"]):
            guess = state["guesses"].get(f"{p}_{i}")
            if guess and i in state["revealed"]:
                sc = calc_score(guess, wine)
                rankings[p]["total"] += sc["total"]
                rankings[p]["max_total"] += sc["max_score"]
                rankings[p]["per_wine"].append({
                    "wine_index": i,
                    "wine_name": wine.get("name", f"#{i+1}"),
                    "guess": guess, "score": sc,
                })
    sr = sorted(rankings.items(), key=lambda x: x[1]["total"], reverse=True)
    return [{"rank": i+1, "participant": n, **d} for i, (n, d) in enumerate(sr)]
