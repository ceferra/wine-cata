"""Scoring of guesses against the real wine. Pure functions, no I/O.

Per wine (100 points when every field of the real wine is known):
  grape    25  Jaccard overlap between guessed and real grapes (extra grapes cost points)
  origin   25  exact D.O. = 25, another D.O. of the same region = 10
  aging    20  exact = 20, neighbouring aging (Crianza vs Reserva) = 8
  rating   10  |diff| <= 0.5 -> 10, <= 1 -> 5
  alcohol  10  |diff| <= 0.5 -> 10, <= 1 -> 6, <= 2 -> 3
  price    10  within max(3 EUR, 15%) -> 10, max(6 EUR, 30%) -> 6, max(12 EUR, 50%) -> 3
Fields that are empty in the real wine are not scored; empty guesses score 0.
"""

import re
import unicodedata

from .options import DEFAULT_AGINGS, ORIGIN_REGIONS

FIELDS = [("grape", 25), ("origin", 25), ("aging", 20), ("rating", 10), ("alcohol", 10), ("price", 10)]
FIELD_MAX = dict(FIELDS)


def norm(s) -> str:
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s).strip().lower()


def split_grapes(s) -> set:
    if isinstance(s, (list, tuple, set)):
        items = s
    else:
        items = re.split(r"[,/&+;]", s or "")
    return {norm(x) for x in items if norm(x)}


def _num(x):
    if x is None or x == "":
        return None
    try:
        return float(str(x).replace(",", "."))
    except ValueError:
        return None


def score_grape(guess, actual) -> int:
    g, a = split_grapes(guess), split_grapes(actual)
    if not g or not a:
        return 0
    return round(25 * len(g & a) / len(g | a))


def score_origin(guess, actual, regions=None) -> int:
    g, a = norm(guess), norm(actual)
    if not g or not a:
        return 0
    if g == a:
        return 25
    regions = {norm(k): v for k, v in (regions or ORIGIN_REGIONS).items()}
    if regions.get(g) and regions.get(g) == regions.get(a):
        return 10
    return 0


def score_aging(guess, actual, order=None) -> int:
    g, a = norm(guess), norm(actual)
    if not g or not a:
        return 0
    if g == a:
        return 20
    order = [norm(x) for x in (order or DEFAULT_AGINGS)]
    if g in order and a in order and abs(order.index(g) - order.index(a)) == 1:
        return 8
    return 0


def score_rating(guess, actual) -> int:
    g, a = _num(guess), _num(actual)
    if g is None or a is None:
        return 0
    d = abs(g - a)
    return 10 if d <= 0.5 else 5 if d <= 1 else 0


def score_alcohol(guess, actual) -> int:
    g, a = _num(guess), _num(actual)
    if g is None or a is None:
        return 0
    d = abs(g - a)
    return 10 if d <= 0.5 else 6 if d <= 1 else 3 if d <= 2 else 0


def score_price(guess, actual) -> int:
    g, a = _num(guess), _num(actual)
    if g is None or a is None:
        return 0
    d = abs(g - a)
    if d <= max(3, 0.15 * a):
        return 10
    if d <= max(6, 0.30 * a):
        return 6
    if d <= max(12, 0.50 * a):
        return 3
    return 0


def _has_value(v) -> bool:
    return v not in (None, "") and not (isinstance(v, float) and v != v)


def calc_score(guess: dict, actual: dict, agings=None) -> dict:
    scorers = {
        "grape": score_grape,
        "origin": score_origin,
        "aging": lambda g, a: score_aging(g, a, agings),
        "rating": score_rating,
        "alcohol": score_alcohol,
        "price": score_price,
    }
    bd, total, max_s = {}, 0, 0
    for field, mx in FIELDS:
        if not _has_value(actual.get(field)):
            continue
        pts = scorers[field](guess.get(field), actual.get(field))
        bd[field] = pts
        total += pts
        max_s += mx
    return {"total": total, "max_score": max_s, "pct": round(100 * total / max_s, 1) if max_s else 0.0,
            "breakdown": bd}


def rankings(participants: list, wines: list, guesses: dict, agings=None) -> list:
    """participants: [{id, name}]; wines: [{id, revealed, ...}];
    guesses: {(participant_id, wine_id): guess}. Only revealed wines count.
    Ties share a position (1, 1, 3...)."""
    rows = []
    for p in participants:
        r = {"participant_id": p["id"], "participant": p["name"], "total": 0, "max_total": 0, "per_wine": []}
        for pos, w in enumerate(wines):
            if not w["revealed"]:
                continue
            g = guesses.get((p["id"], w["id"]))
            sc = calc_score(g or {}, w, agings)
            r["max_total"] += sc["max_score"]
            if g:
                r["total"] += sc["total"]
                r["per_wine"].append({"wine_id": w["id"], "position": pos, "guess": g, "score": sc})
        rows.append(r)
    rows.sort(key=lambda r: (-r["total"], norm(r["participant"])))
    for i, r in enumerate(rows):
        r["rank"] = rows[i - 1]["rank"] if i and r["total"] == rows[i - 1]["total"] else i + 1
    return rows
