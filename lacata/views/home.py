"""Landing page: join a tasting with its code, or create / manage one as organizer."""

import hmac

import streamlit as st

from .. import db, ui
from ..config import secret
from ..i18n import t


def render(bad_code=False):
    L = ui.lang_for()
    ui.hero(t("app_title", L), t("tagline", L))
    if bad_code:
        st.error(t("tasting_not_found", L))

    st.markdown(f"### {t('join_title', L)}")
    with st.form("join_code"):
        code = st.text_input(t("code", L), max_chars=5, placeholder="ABC23")
        if st.form_submit_button(t("join_btn", L), type="primary", width="stretch"):
            if db.get_tasting(code):
                st.query_params.clear()
                st.query_params["sala"] = code.strip().upper()
                st.rerun()
            st.error(t("tasting_not_found", L))

    st.divider()
    st.markdown(f"### {t('organize_title', L)}")
    tab_new, tab_login = st.tabs([t("new_tasting", L), t("manage_tasting", L)])
    with tab_new:
        app_pw = secret("APP_PASSWORD")
        with st.form("create"):
            name = st.text_input(t("tasting_name", L), placeholder=t("tasting_name_placeholder", L))
            pin = st.text_input(t("choose_pin", L), type="password", help=t("pin_help", L))
            pw = st.text_input(t("app_password", L), type="password") if app_pw else None
            if st.form_submit_button(t("create_btn", L), type="primary", width="stretch"):
                if app_pw and not hmac.compare_digest(pw or "", str(app_pw)):
                    ui.slow_down_failed_login()
                    st.error(t("wrong_app_password", L))
                else:
                    try:
                        tasting = db.create_tasting(name, pin, L)
                    except db.TastingError as e:
                        st.error(t(e.code, L))
                    else:
                        st.session_state.setdefault("auth", set()).add(tasting["code"])
                        st.query_params.clear()
                        st.query_params.update({"sala": tasting["code"], "org": "1"})
                        st.rerun()
    with tab_login:
        with st.form("login"):
            code = st.text_input(t("code", L), max_chars=5, key="login_code")
            pin = st.text_input(t("pin", L), type="password", key="login_pin")
            if st.form_submit_button(t("enter", L), type="primary", width="stretch"):
                if db.check_pin(code, pin):
                    code = code.strip().upper()
                    st.session_state.setdefault("auth", set()).add(code)
                    st.query_params.clear()
                    st.query_params.update({"sala": code, "org": "1"})
                    st.rerun()
                ui.slow_down_failed_login()
                st.error(t("wrong_pin", L))

    st.divider()
    ui.lang_picker(L)
    ui.footer(L)
