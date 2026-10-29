"""Pieces shared by several views: end-of-tasting highlights and result tables."""

import pandas as pd
import streamlit as st

from .. import ui
from ..i18n import t
from ..scoring import FIELDS, calc_score


def wine_stats(wines, people, guesses, agings):
    """Per revealed wine: mean score %, mean liking (1-5), number of guesses."""
    out = []
    for pos, w in enumerate(wines):
        if not w["revealed"]:
            continue
        scores, likes = [], []
        for p in people:
            g = guesses.get((p["id"], w["id"]))
            if not g:
                continue
            scores.append(calc_score(g, w, agings)["pct"])
            if g.get("liking"):
                likes.append(g["liking"])
        out.append({"wine": w, "position": pos, "n": len(scores),
                    "score": sum(scores) / len(scores) if scores else None,
                    "liking": sum(likes) / len(likes) if likes else None})
    return out


def highlights(wines, people, guesses, agings, L):
    stats = [s for s in wine_stats(wines, people, guesses, agings) if s["n"]]
    if not stats:
        return
    st.markdown(f"### {t('highlights', L)}")
    liked = [s for s in stats if s["liking"] is not None]
    cols = st.columns(3)
    if liked:
        fav = max(liked, key=lambda s: s["liking"])
        cols[0].metric(f"❤️ {t('crowd_favourite', L)}", f"#{fav['position'] + 1} · {fav['liking']:.1f}★",
                       help=fav["wine"]["name"])
        cols[0].caption(fav["wine"]["name"])
        valued = [s for s in liked if s["wine"].get("price")]
        if valued:
            best = max(valued, key=lambda s: s["liking"] / max(s["wine"]["price"], 1))
            cols[2].metric(f"💶 {t('best_value', L)}", f"#{best['position'] + 1} · {ui.fmt_num(best['wine']['price'], ' €')}")
            cols[2].caption(best["wine"]["name"])
    hard = min(stats, key=lambda s: s["score"])
    cols[1].metric(f"🧩 {t('hardest', L)}", f"#{hard['position'] + 1} · {hard['score']:.0f}%")
    cols[1].caption(hard["wine"]["name"])


def wine_detail_table(w, ranks, L):
    labels = {f: t("score_" + f, L) for f, _ in FIELDS}
    rows = []
    for r in ranks:
        pw = next((x for x in r["per_wine"] if x["wine_id"] == w["id"]), None)
        if not pw:
            continue
        bd = pw["score"]["breakdown"]
        row = {t("participant", L): r["participant"]}
        for f, label in labels.items():
            if f in bd:
                row[label] = f"{ui.fmt_field(f, pw['guess'].get(f))} (+{bd[f]})"
        row[t("total", L)] = pw["score"]["total"]
        lk = pw["guess"].get("liking")
        row["★"] = lk if lk else None
        rows.append(row)
    if rows:
        df = pd.DataFrame(rows).sort_values(t("total", L), ascending=False)
        st.dataframe(df, width="stretch", hide_index=True)
    else:
        st.caption(t("no_guesses", L))


def export_csv(wines, people, guesses, agings, L) -> bytes:
    rows = []
    for pos, w in enumerate(wines):
        for p in people:
            g = guesses.get((p["id"], w["id"]))
            if not g:
                continue
            sc = calc_score(g, w, agings) if w["revealed"] else None
            row = {"wine_no": pos + 1, "wine": w["name"], "participant": p["name"]}
            for f, _ in FIELDS:
                row[f"guess_{f}"] = g.get(f)
                row[f"real_{f}"] = w.get(f)
                row[f"pts_{f}"] = sc["breakdown"].get(f) if sc else None
            row["liking"] = g.get("liking")
            row["total"] = sc["total"] if sc else None
            rows.append(row)
    return pd.DataFrame(rows).to_csv(index=False).encode("utf-8-sig")
