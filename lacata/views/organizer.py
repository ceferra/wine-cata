"""Organizer view (PIN protected): wines, room control, results, cellar and settings."""

import pandas as pd
import streamlit as st

from .. import ai, catalog, db, importer, ui
from ..config import secret
from ..i18n import LANGS, t
from ..scoring import rankings
from . import common


def render(tasting):
    L = ui.lang_for(tasting)
    tid = tasting["id"]
    if tasting["code"] not in st.session_state.setdefault("auth", set()):
        _login(tasting, L)
        return
    ui.sync_version(tid)

    wines = db.list_wines(tid)
    people = db.list_participants(tid)
    guesses = db.list_guesses(tid)
    agings = tasting["options"]["agings"]
    ranks = rankings(people, wines, guesses, agings)
    n_rev = sum(w["revealed"] for w in wines)

    ui.hero(tasting["name"] or t("app_title", L), f"{t('organizer', L)} · {t('code', L)} {tasting['code']}")
    st.caption(f"🍷 {len(wines)} {t('wines', L).lower()} · 👥 {len(people)} {t('participants_label', L).lower()}"
               f" · ✍️ {len(guesses)} {t('predictions', L).lower()} · 🔓 {n_rev}/{len(wines)}")
    ui.show_flash()

    tabs = st.tabs([t("tab_wines", L), t("tab_room", L), t("tab_results", L), t("tab_db", L), t("tab_settings", L)])
    with tabs[0]:
        _wines_tab(tasting, wines, guesses, L)
    with tabs[1]:
        _room_tab(tasting, wines, people, guesses, ranks, L)
    with tabs[2]:
        _results_tab(tasting, wines, people, guesses, ranks, L)
    with tabs[3]:
        _cellar_tab(tasting, L)
    with tabs[4]:
        _settings_tab(tasting, L)
    ui.live_updates(tid)
    ui.footer(L)


def _login(tasting, L):
    ui.hero(tasting["name"] or t("app_title", L), f"{t('organizer', L)} · {t('code', L)} {tasting['code']}")
    with st.form("org_login"):
        pin = st.text_input(t("pin", L), type="password")
        if st.form_submit_button(t("enter", L), type="primary", width="stretch"):
            if db.check_pin(tasting["code"], pin):
                st.session_state.setdefault("auth", set()).add(tasting["code"])
                st.rerun()
            ui.slow_down_failed_login()
            st.error(t("wrong_pin", L))
    st.link_button(t("go_participant", L), f"?sala={tasting['code']}", width="stretch")


def ai_key():
    return secret("OPENAI_API_KEY") or st.session_state.get("openai_key", "")


# ---------------------------------------------------------------- wines

def _add_wine(tasting, wine, L, *, review, verified, to_cellar, cellar_id=None):
    tid = tasting["id"]
    added = db.add_options(tid, [g.strip() for g in wine["grape"].split(",")], [wine["origin"]])
    if to_cellar and cellar_id is None:
        cellar_id = db.cellar_add(wine)
    db.add_wine(tid, wine, cellar_id=cellar_id, needs_review=review and not verified)
    msg = t("wine_added", L)
    if added:
        msg += " " + t("options_added", L) + ": " + ", ".join(added)
    ui.flash(msg)


def _wines_tab(tasting, wines, guesses, L):
    tid = tasting["id"]
    if tasting["started"]:
        st.info(t("started_edit_warning", L))

    st.markdown(f"#### {t('add_wine', L)}")
    methods = {"db": t("method_db", L), "ai": t("method_ai", L), "photo": t("method_photo", L),
               "file": t("method_file", L), "manual": t("method_manual", L)}
    method = st.segmented_control("method", list(methods), format_func=methods.get, default="manual",
                                  label_visibility="collapsed", key="add_method", width="stretch")

    if method == "db":
        q = st.text_input("q", placeholder=t("db_search", L), label_visibility="collapsed", key="cellar_q_add")
        in_tasting = {w["cellar_id"] for w in wines if w["cellar_id"]}
        found = db.cellar_list(q)
        if not found:
            st.info(t("db_no_results" if q else "db_empty", L))
        if not q:
            _catalog_button(L, "seed_add")
        for cw in found[:40]:
            ui.wine_card(cw, L, show_desc=False)
            if st.button(t("db_add_to_tasting", L), key=f"cadd_{cw['id']}", width="stretch",
                         disabled=cw["id"] in in_tasting):
                _add_wine(tasting, cw, L, review=cw["source"] == "catalog", verified=False, to_cellar=False,
                          cellar_id=cw["id"])
                st.rerun()

    elif method in ("ai", "photo"):
        if not ai_key():
            st.warning(t("key_needed_settings", L))
        elif method == "ai":
            with st.form("ai_search"):
                q = st.text_input(t("f_name", L), placeholder=t("search_placeholder", L))
                if st.form_submit_button(f"🔍 {t('search', L)}", type="primary", width="stretch") and q:
                    with st.spinner(t("searching_ai", L)):
                        _run_ai(lambda: ai.search_wine(q, ai_key(), L, tasting["options"], secret("OPENAI_MODEL")), L)
        else:
            up = st.file_uploader(t("photo_caption", L), type=["jpg", "jpeg", "png", "webp", "heic"])
            if up and st.button(f"📷 {t('analyze_label', L)}", type="primary", width="stretch"):
                with st.spinner(t("analyzing", L)):
                    _run_ai(lambda: ai.recognize_label(up.getvalue(), ai_key(), L, tasting["options"],
                                                       secret("OPENAI_MODEL")), L)

    elif method == "file":
        _import_section(tasting, wines, L)

    elif method == "manual":
        res = ui.wine_form("new_manual", L, tasting["options"], submit_label=t("add_wine_btn", L),
                           cellar_choice=t("also_cellar", L))
        if res:
            wine, _, to_cellar = res
            wine["source"] = "manual"
            _add_wine(tasting, wine, L, review=False, verified=True, to_cellar=to_cellar)
            st.rerun()

    draft = st.session_state.get("ai_draft")
    if draft and method in ("ai", "photo"):
        st.success(t("info_found", L))
        if draft.get("label_text"):
            st.caption(f"{t('label_read', L)}: **{draft['label_text']}**")
        res = ui.wine_form(f"draft_{draft['_n']}", L, tasting["options"], draft, submit_label=t("add_this_wine", L),
                           review=True, cellar_choice=t("also_cellar", L))
        if res:
            wine, verified, to_cellar = res
            _add_wine(tasting, wine, L, review=True, verified=verified, to_cellar=to_cellar)
            st.session_state.pop("ai_draft")
            st.rerun()
        if st.button(t("discard", L), width="stretch"):
            st.session_state.pop("ai_draft")
            st.rerun()

    st.divider()
    st.markdown(f"#### {t('wines_added', L)} ({len(wines)})")
    if not wines:
        st.caption(t("no_wines_yet", L))
    editing = st.session_state.get("edit_wine")
    for pos, w in enumerate(wines):
        n_g = sum(1 for (pid, wid) in guesses if wid == w["id"])
        flag = f" ⚠️ {t('needs_review', L)}" if w["needs_review"] else ""
        ui.wine_card(w, L, number=pos + 1)
        if flag or w["revealed"]:
            st.caption((f"🔓 {t('revealed', L)} " if w["revealed"] else "") + flag)
        with st.popover(f"⚙️ {t('actions', L)}", width="stretch"):
            if st.button(f"✏️ {t('edit', L)}", key=f"ed_{w['id']}", width="stretch"):
                st.session_state["edit_wine"] = None if editing == w["id"] else w["id"]
                st.rerun()
            c1, c2 = st.columns(2)
            if c1.button("⬆️", key=f"up_{w['id']}", width="stretch", disabled=pos == 0):
                db.move_wine(w["id"], -1)
                st.rerun()
            if c2.button("⬇️", key=f"dn_{w['id']}", width="stretch", disabled=pos == len(wines) - 1):
                db.move_wine(w["id"], 1)
                st.rerun()
            warn = t("delete_wine_q", L) + (f" {t('delete_wine_guesses', L).format(n=n_g)}" if n_g else "")
            st.caption(warn)
            if st.button(f"🗑️ {t('delete', L)}", key=f"dl_{w['id']}", type="primary", width="stretch"):
                db.delete_wine(w["id"])
                st.rerun()
        if editing == w["id"]:
            res = ui.wine_form(f"edit_{w['id']}", L, tasting["options"], w, submit_label=f"💾 {t('save', L)}",
                               review=w["needs_review"],
                               cellar_choice=t("also_update_cellar", L) if w["cellar_id"] else None)
            if res:
                wine, verified, to_cellar = res
                db.add_options(tasting["id"], [g.strip() for g in wine["grape"].split(",")], [wine["origin"]])
                db.update_wine(w["id"], wine, needs_review=w["needs_review"] and not verified)
                if to_cellar and w["cellar_id"]:
                    db.cellar_update(w["cellar_id"], wine, verified=not w["needs_review"] or verified)
                st.session_state["edit_wine"] = None
                ui.flash(t("saved", L))
                st.rerun()


def _import_section(tasting, wines, L):
    """Bulk add from a CSV/Excel file, e.g. the template filled in by ChatGPT."""
    opts = tasting["options"]
    st.caption(t("import_steps", L))
    c1, c2 = st.columns(2)
    c1.download_button(f"⬇️ {t('template_xlsx', L)}", importer.template_xlsx(opts, L), "plantilla_vinos.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", width="stretch")
    c2.download_button(f"⬇️ {t('template_csv', L)}", importer.template_csv(L), "plantilla_vinos.csv",
                       mime="text/csv", width="stretch")
    with st.expander(f"🤖 {t('chatgpt_prompt', L)}"):
        st.caption(t("chatgpt_prompt_hint", L))
        st.code(importer.chatgpt_prompt(opts, L) + "- …", language=None, wrap_lines=True)

    n = st.session_state.get("imp_n", 0)
    up = st.file_uploader(t("import_upload", L), type=["xlsx", "csv", "txt"], key=f"imp_file_{n}")
    pasted = st.text_area(t("import_paste", L), key=f"imp_text_{n}", height=100,
                          placeholder=t("import_paste_placeholder", L))
    if not up and not pasted.strip():
        return
    try:
        df = importer.read_table(up.getvalue(), up.name) if up else importer.parse_text_table(pasted)
        found, warnings, ignored = importer.rows_to_wines(df, opts)
    except importer.ImportFailed as e:
        st.error(t("import_no_name", L) if str(e) == "no_name_column" else f"{t('import_bad_file', L)} ({e})")
        return

    in_tasting = {w["name"].strip().lower() for w in wines}
    new = [w for w in found if w["name"].strip().lower() not in in_tasting]
    if len(new) < len(found):
        st.info(t("import_already", L).format(n=len(found) - len(new)))
    if not new:
        st.warning(t("import_nothing", L))
        return
    if ignored:
        st.caption(f"{t('import_ignored_cols', L)}: {', '.join(ignored)}")
    if warnings:
        with st.expander(f"⚠️ {t('import_warnings', L)} ({len(warnings)})", expanded=True):
            st.markdown("\n".join(f"- {t('import_row', L)} {row}: {t('import_w_' + kind, L)} {detail}".rstrip()
                                   for kind, row, detail in warnings))
    show = ["name", "grape", "origin", "aging", "type", "year", "alcohol", "price", "rating"]
    st.dataframe(pd.DataFrame(new)[show].rename(columns=dict(zip(importer.COLUMNS, importer.headers(L)))),
                 hide_index=True, width="stretch")
    to_cellar = st.checkbox(t("also_cellar", L), value=True, key=f"imp_cellar_{n}")
    if st.button(f"➕ {t('import_add', L).format(n=len(new))}", type="primary", width="stretch"):
        _import_wines(tasting, new, to_cellar, L)
        st.session_state["imp_n"] = n + 1  # fresh uploader and text box
        st.rerun()


def _import_wines(tasting, new, to_cellar, L):
    tid = tasting["id"]
    added = db.add_options(tid, [g.strip() for w in new for g in w["grape"].split(",")], [w["origin"] for w in new])
    known = {cw["name"].strip().lower(): cw["id"] for cw in db.cellar_list()} if to_cellar else {}
    for w in new:
        cellar_id = None
        if to_cellar:
            cellar_id = known.get(w["name"].strip().lower()) or db.cellar_add(w)
        db.add_wine(tid, w, cellar_id=cellar_id)
    msg = t("import_done", L).format(n=len(new))
    if added:
        msg += " " + t("options_added", L) + ": " + ", ".join(added)
    ui.flash(msg)


def _run_ai(call, L):
    try:
        draft = call()
    except ai.AIError as e:
        st.error(t(e.code, L) + (f" ({e.detail})" if e.detail else ""))
        return
    draft["_n"] = st.session_state.get("_draft_n", 0) + 1
    st.session_state["_draft_n"] = draft["_n"]
    st.session_state["ai_draft"] = draft
    st.rerun()


# ---------------------------------------------------------------- room

def _room_tab(tasting, wines, people, guesses, ranks, L):
    tid, code = tasting["id"], tasting["code"]
    url = ui.participant_url(code)
    c1, c2 = st.columns([1, 1], gap="large")
    with c1:
        st.markdown(f"#### {t('qr_title', L)}")
        st.markdown(f'<div class="lc-code">{code}</div>', unsafe_allow_html=True)
        ui.show_qr(url)
        st.caption(t("qr_instructions", L))
        st.link_button(f"📺 {t('open_screen', L)}", f"{url}&pantalla=1", width="stretch")
        st.caption(t("screen_hint", L))

    with c2:
        if not tasting["started"]:
            st.markdown(f"#### {t('start_tasting', L)}")
            unreviewed = [p + 1 for p, w in enumerate(wines) if w["needs_review"]]
            if unreviewed:
                st.warning(t("unreviewed_warning", L).format(wines=", ".join(map(str, unreviewed))))
            if not wines:
                st.info(t("add_wines_first", L))
            if st.button(f"▶️ {t('start_btn', L)}", type="primary", width="stretch", disabled=not wines):
                db.update_tasting(tid, started=True)
                st.rerun()

        st.markdown(f"#### {t('participants_label', L)} ({len(people)})")
        if not people:
            st.caption(t("no_participants", L))
        for p in people:
            mine = [w for w in wines if (p["id"], w["id"]) in guesses]
            with st.popover(f"👤 {p['name']} · {len(mine)}/{len(wines)}", width="stretch"):
                st.caption(t("personal_link_org", L))
                ui.show_qr(ui.participant_url(code, p["token"]), width=180)
                pending = [w for w in mine if not w["revealed"]]
                if pending:
                    st.markdown(f"**{t('admin_cancel', L)}**")
                    for w in pending:
                        pos = wines.index(w) + 1
                        if st.button(f"✕ {t('wine', L)} {pos}", key=f"ac_{p['id']}_{w['id']}", width="stretch"):
                            db.cancel_guess(p["id"], w["id"])
                            st.rerun()
                st.divider()
                if st.button(f"🗑️ {t('remove_participant', L)}", key=f"rmp_{p['id']}", type="primary",
                             width="stretch"):
                    db.remove_participant(p["id"])
                    st.rerun()

    if tasting["started"] and wines:
        st.divider()
        st.markdown(f"#### {t('reveal_wines', L)}")
        for pos, w in enumerate(wines):
            n_g = sum(1 for p in people if (p["id"], w["id"]) in guesses)
            missing = len(people) - n_g
            label = f"{t('wine', L)} {pos + 1} — {w['name']}"
            if w["revealed"]:
                st.markdown(f"🔓 **{ui.esc(label)}** · {n_g}/{len(people)}")
                continue
            color = "green" if missing == 0 and people else "orange"
            st.markdown(f"🍷 **{ui.esc(label)}** · :{color}[{n_g}/{len(people)}]")
            if missing == 0:
                if st.button(f"🔓 {t('reveal', L)}", key=f"rv_{w['id']}", width="stretch"):
                    db.reveal_wine(w["id"])
                    st.rerun()
            elif ui.confirm_button(f"🔓 {t('reveal', L)}", t("reveal_anyway_q", L).format(n=missing),
                                   f"rvf_{w['id']}", L, danger_label=t("reveal_anyway", L)):
                db.reveal_wine(w["id"])
                st.rerun()

    if any(w["revealed"] for w in wines):
        st.divider()
        n_rev = sum(w["revealed"] for w in wines)
        st.markdown(f"#### {t('partial_ranking', L)} ({n_rev}/{len(wines)})")
        for r in ranks:
            ui.rank_card(r, L)


# ---------------------------------------------------------------- results

def _results_tab(tasting, wines, people, guesses, ranks, L):
    revealed = [w for w in wines if w["revealed"]]
    if not revealed:
        st.info(t("no_revealed", L))
        return
    agings = tasting["options"]["agings"]
    if len(revealed) == len(wines) and ranks and ranks[0]["total"] > 0:
        winners = [r["participant"] for r in ranks if r["rank"] == 1]
        st.markdown(f"## 🏆 {ui.esc(', '.join(winners))}")
        ui.celebrate(f"org_final_{tasting['id']}")
    st.markdown(f"### {t('ranking', L)}")
    for r in ranks:
        ui.rank_card(r, L)
    common.highlights(wines, people, guesses, agings, L)
    st.divider()
    st.markdown(f"### {t('detail', L)}")
    for pos, w in enumerate(wines):
        if not w["revealed"]:
            continue
        st.markdown(f"**{t('wine', L)} {pos + 1} — {ui.esc(w['name'])}**")
        st.caption(ui.wine_meta(w, L))
        common.wine_detail_table(w, ranks, L)
    st.download_button(f"⬇️ {t('export_csv', L)}", common.export_csv(wines, people, guesses, agings, L),
                       file_name=f"cata_{tasting['code']}.csv", mime="text/csv", width="stretch")


# ---------------------------------------------------------------- cellar

def _catalog_button(L, key):
    """Offer to load the bundled catalog of common Spanish wines, while some are missing."""
    names = {w["name"].strip().lower() for w in db.cellar_list()}
    missing = [w for w in catalog.load() if w["name"].strip().lower() not in names]
    if not missing:
        return
    if st.button(f"📥 {t('load_catalog', L).format(n=len(missing))}", key=key, width="stretch",
                 help=t("load_catalog_help", L)):
        n = db.cellar_seed(missing)
        ui.flash(t("catalog_loaded", L).format(n=n))
        st.rerun()


def _cellar_tab(tasting, L):
    st.markdown(f"#### {t('db_title', L)}")
    q = st.text_input("q", placeholder=t("db_search", L), label_visibility="collapsed", key="cellar_q")
    found = db.cellar_list(q)
    st.caption(f"{len(found)} {t('db_wine_count', L)}")
    _catalog_button(L, "seed_cellar")
    editing = st.session_state.get("edit_cellar")
    for cw in found:
        ui.wine_card(cw, L)
        if cw["source"] == "catalog":
            st.caption(f"📖 {t('catalog_wine', L)}")
        with st.popover(f"⚙️ {t('actions', L)}", width="stretch"):
            if st.button(f"✏️ {t('edit', L)}", key=f"ced_{cw['id']}", width="stretch"):
                st.session_state["edit_cellar"] = None if editing == cw["id"] else cw["id"]
                st.rerun()
            st.caption(t("db_delete_q", L))
            if st.button(f"🗑️ {t('delete', L)}", key=f"cdl_{cw['id']}", type="primary", width="stretch"):
                db.cellar_delete(cw["id"])
                st.rerun()
        if editing == cw["id"]:
            res = ui.wine_form(f"cedit_{cw['id']}", L, tasting["options"], cw, submit_label=f"💾 {t('save', L)}")
            if res:
                db.cellar_update(cw["id"], res[0], verified=True)
                st.session_state["edit_cellar"] = None
                st.rerun()


# ---------------------------------------------------------------- settings

def _settings_tab(tasting, L):
    tid = tasting["id"]
    st.markdown(f"#### {t('general', L)}")
    with st.form("general"):
        name = st.text_input(t("tasting_name", L), value=tasting["name"])
        keys = list(LANGS)
        lang = st.selectbox(t("tasting_language", L), keys, index=keys.index(tasting["lang"]),
                            format_func=LANGS.get, help=t("tasting_language_help", L))
        if st.form_submit_button(f"💾 {t('save', L)}", width="stretch"):
            db.update_tasting(tid, name=name.strip(), lang=lang)
            st.session_state["lang"] = lang
            st.rerun()

    st.markdown(f"#### {t('openai_key', L)}")
    if secret("OPENAI_API_KEY"):
        st.success(t("key_from_secrets", L))
    else:
        k = st.text_input(t("openai_key", L), value=st.session_state.get("openai_key", ""), type="password",
                          placeholder="sk-...", label_visibility="collapsed", help=t("key_session_help", L))
        if k != st.session_state.get("openai_key", ""):
            st.session_state["openai_key"] = k.strip()
            st.rerun()

    st.markdown(f"#### {t('config_options', L)}")
    st.caption(t("options_help", L))
    opts = tasting["options"]
    with st.form("options"):
        new = {}
        for cat in ("grapes", "origins", "agings"):
            txt = st.text_area(t(cat + "_config", L), "\n".join(opts[cat]), height=160)
            new[cat] = list(dict.fromkeys(x.strip() for x in txt.splitlines() if x.strip()))
        if st.form_submit_button(f"💾 {t('save', L)}", width="stretch"):
            db.update_tasting(tid, options=new)
            ui.flash(t("saved", L))
            st.rerun()

    st.markdown(f"#### {t('session', L)}")
    if st.button(f"🚪 {t('logout', L)}", width="stretch"):
        st.session_state["auth"].discard(tasting["code"])
        st.rerun()
    if ui.confirm_button(f"🗑️ {t('delete_tasting', L)}", t("delete_tasting_q", L), "del_tasting", L):
        db.delete_tasting(tid)
        st.session_state["auth"].discard(tasting["code"])
        st.query_params.clear()
        st.rerun()

    with st.expander(t("tab_about", L)):
        st.markdown(t("about_md", L))
