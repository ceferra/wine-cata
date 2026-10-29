"""Projector screen (?sala=CODE&pantalla=1): QR, progress and ranking. Shows no hidden answers,
so it is safe to put on a TV instead of the organizer screen."""

import streamlit as st

from .. import db, ui
from ..i18n import t
from ..scoring import rankings
from . import common


def render(tasting):
    L = ui.lang_for(tasting)
    tid = tasting["id"]
    ui.sync_version(tid)
    wines = db.list_wines(tid)
    people = db.list_participants(tid)
    guesses = db.list_guesses(tid)
    agings = tasting["options"]["agings"]
    ranks = rankings(people, wines, guesses, agings)
    revealed = [w for w in wines if w["revealed"]]

    ui.hero(tasting["name"] or t("app_title", L))
    left, right = st.columns([2, 3], gap="large")
    with left:
        st.markdown(f'<div class="lc-code">{tasting["code"]}</div>', unsafe_allow_html=True)
        ui.show_qr(ui.participant_url(tasting["code"]), width=320)
        st.caption(t("qr_instructions", L))
    with right:
        if not tasting["started"]:
            st.markdown(f"### {t('waiting_room', L)} ({len(people)})")
            st.markdown(" · ".join(f"**{ui.esc(p['name'])}**" for p in people) or t("no_participants", L))
        else:
            st.markdown(f"### {t('progress', L)}")
            for pos, w in enumerate(wines):
                n_g = sum(1 for p in people if (p["id"], w["id"]) in guesses)
                name = f" — {w['name']}" if w["revealed"] else ""
                st.progress(n_g / len(people) if people else 0.0,
                            text=f"{'🔓' if w['revealed'] else '🍷'} {t('wine', L)} {pos + 1}{name} · {n_g}/{len(people)}")
        if revealed:
            all_out = len(revealed) == len(wines)
            if all_out and ranks and ranks[0]["total"] > 0:
                st.markdown(f"## 🏆 {ui.esc(', '.join(r['participant'] for r in ranks if r['rank'] == 1))}")
                ui.celebrate(f"screen_final_{tid}")
            st.markdown(f"### {t('final_ranking' if all_out else 'partial_ranking', L)}")
            for r in ranks:
                ui.rank_card(r, L)
            if all_out:
                common.highlights(wines, people, guesses, agings, L)
    ui.live_updates(tid)
