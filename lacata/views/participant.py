"""Participant view: join with a name, send a guess per wine, see scores and ranking."""

import streamlit as st

from .. import db, ui
from ..i18n import t
from ..scoring import calc_score, rankings
from . import common


def render(tasting):
    L = ui.lang_for(tasting)
    tid = tasting["id"]
    ui.sync_version(tid)
    me = db.participant_by_token(st.query_params.get("p"))
    if me and me["tasting_id"] != tid:
        me = None

    ui.hero(tasting["name"] or t("app_title", L), t("participant", L))
    ui.show_flash()

    if not me:
        _join(tasting, L)
        ui.live_updates(tid)
        _bottom(L)
        return

    st.markdown(f"### {t('hello', L)}, {ui.esc(me['name'])} 👋")
    if not tasting["started"]:
        st.info(t("not_started", L))
        ui.live_updates(tid)
        _bottom(L, me)
        return

    wines = db.list_wines(tid)
    people = db.list_participants(tid)
    guesses = db.list_guesses(tid)
    agings = tasting["options"]["agings"]
    ranks = rankings(people, wines, guesses, agings)

    done = sum(1 for w in wines if (me["id"], w["id"]) in guesses)
    st.progress(done / len(wines) if wines else 0.0, text=f"{done}/{len(wines)} {t('completed', L)}")
    if not wines:
        st.info(t("no_wines_yet", L))

    first_open = next((w["id"] for w in wines if (me["id"], w["id"]) not in guesses and not w["revealed"]), None)
    for pos, w in enumerate(wines):
        g = guesses.get((me["id"], w["id"]))
        _wine(tasting, me, pos, w, g, ranks, L, expanded=w["id"] == first_open)

    revealed = [w for w in wines if w["revealed"]]
    if revealed:
        st.divider()
        all_out = len(revealed) == len(wines)
        if all_out and ranks and ranks[0]["total"] > 0:
            winners = [r["participant"] for r in ranks if r["rank"] == 1]
            st.markdown(f"## 🏆 {ui.esc(', '.join(winners))}")
            ui.celebrate(f"final_{tid}")
        st.markdown(f"## {t('final_ranking' if all_out else 'partial_ranking', L)} ({len(revealed)}/{len(wines)})")
        for r in ranks:
            ui.rank_card(r, L, me["id"])
        if all_out:
            common.highlights(wines, people, guesses, agings, L)

    ui.live_updates(tid)
    _bottom(L, me)


def _join(tasting, L):
    st.markdown(f"## {t('who_are_you', L)}")
    with st.form("join"):
        name = st.text_input(t("your_name", L), max_chars=60, placeholder=t("your_name_placeholder", L))
        if st.form_submit_button(t("join_btn", L), type="primary", width="stretch"):
            try:
                p = db.join(tasting["id"], name)
            except db.TastingError as e:
                st.error(t(e.code, L))
            else:
                st.query_params["p"] = p["token"]
                st.rerun()
    st.caption(t("join_hint", L))


def _wine(tasting, me, pos, w, g, ranks, L, expanded):
    tid = tasting["id"]
    type_info = f" · {t('type_' + w['type'], L)}" if w.get("type") else ""
    if w["revealed"]:
        icon, state = "🔓", t("revealed", L)
    elif g:
        icon, state = "✅", t("sent", L)
    else:
        icon, state = "🍷", t("pending", L)
    title = f"{icon} {t('wine', L)} {pos + 1}{type_info} — {state}"
    if w["revealed"]:
        title = f"{icon} {t('wine', L)} {pos + 1} — {w['name']}"

    # The key changes with the state so a wine revealed while the page is open gets a fresh expander
    # (re-using the old one left it empty until a reload).
    state_key = "r" if w["revealed"] else "s" if g else "p"
    with st.expander(title, expanded=expanded, key=f"exp_{w['id']}_{state_key}"):
        if w["revealed"]:
            ui.wine_card(w, L)
            if g:
                sc = calc_score(g, w, tasting["options"]["agings"])
                if _best_on_wine(ranks, me["id"], w["id"], sc["total"]):
                    st.success(f"🎉 {t('best_on_wine', L)}")
                    ui.celebrate(f"wine_{w['id']}")
                ui.breakdown_table(g, w, sc, L)
                _liking(me, w, g, L)
            else:
                st.info(t("no_guess_sent", L))
            return

        if g:
            st.success(t("prediction_sent", L))
            summary = [f"**{t('score_' + f, L)}:** {ui.fmt_field(f, g.get(f))}"
                       for f in ("grape", "origin", "aging", "alcohol", "price", "rating")]
            st.markdown("  \n".join(summary))
            _liking(me, w, g, L)
            if ui.confirm_button(t("cancel_prediction", L), t("cancel_confirm_q", L), f"canc_{w['id']}", L):
                try:
                    db.cancel_guess(me["id"], w["id"])
                    ui.flash(t("cancel_done", L), "info")
                except db.TastingError as e:
                    ui.flash(t(e.code, L), "error")
                st.rerun()
            return

        _guess_form(tasting, me, w, L)


def _guess_form(tasting, me, w, L):
    opts = tasting["options"]
    with st.form(f"guess_{w['id']}"):
        grapes = st.multiselect(t("f_grape", L), opts["grapes"], placeholder=t("choose", L))
        origin = st.selectbox(t("f_origin", L), opts["origins"], index=None, placeholder=t("choose", L))
        aging = st.selectbox(t("f_aging", L), opts["agings"], index=None, placeholder=t("choose", L))
        c1, c2, c3 = st.columns(3)
        alcohol = c1.number_input(t("f_alcohol", L), 0.0, 25.0, None, 0.5, placeholder="13.5")
        price = c2.number_input(t("f_price", L), 0.0, 5000.0, None, 1.0, placeholder="12")
        rating = c3.number_input(t("f_rating", L), 0.0, 5.0, None, 0.1, placeholder="3.8")
        st.markdown(f"**{t('liking_q', L)}** <span style='color:#7a6b5e'>({t('liking_hint', L)})</span>",
                    unsafe_allow_html=True)
        liking = st.feedback("stars", key=f"lk_new_{w['id']}")
        if st.form_submit_button(t("send_prediction", L), type="primary", width="stretch"):
            guess = {"grape": ", ".join(grapes), "origin": origin, "aging": aging, "alcohol": alcohol,
                     "price": price, "rating": rating, "liking": None if liking is None else liking + 1}
            if not any(guess[k] not in (None, "") for k in ("grape", "origin", "aging", "alcohol", "price",
                                                             "rating")):
                st.error(t("fill_something", L))
                return
            try:
                db.submit_guess(me["id"], w["id"], guess)
                ui.flash(t("sent_ok", L))
            except db.TastingError as e:
                ui.flash(t(e.code, L), "error")
            st.rerun()


def _liking(me, w, g, L):
    current = g.get("liking")
    st.caption(t("liking_q", L))
    val = st.feedback("stars", key=f"lk_{w['id']}", default=current - 1 if current else None)
    if val is not None and val + 1 != current:
        db.set_liking(me["id"], w["id"], val + 1)
        st.rerun()


def _best_on_wine(ranks, me_id, wine_id, my_total):
    if my_total <= 0:
        return False
    best = max((pw["score"]["total"] for r in ranks for pw in r["per_wine"] if pw["wine_id"] == wine_id), default=0)
    return my_total >= best


def _bottom(L, me=None):
    st.divider()
    with st.expander(t("settings", L)):
        ui.lang_picker(L)
        if me:
            st.caption(t("personal_link_hint", L))
            st.code(ui.participant_url(st.query_params.get("sala", ""), me["token"]), language=None,
                    wrap_lines=True)
    ui.footer(L)
