"""Shared UI pieces: CSS, language, cards, QR, live updates, celebration, wine form."""

import html
import io
import time
from urllib.parse import quote

import qrcode
import streamlit as st
import streamlit.components.v1 as components

from . import db
from .config import secret
from .i18n import LANGS, t
from .options import WINE_TYPES
from .scoring import FIELDS

ACCENT = "#8b2e38"

# Light theme is forced in .streamlit/config.toml. This CSS only touches our own classes and a
# few sizes: never set font-family/color on generic span/div, it breaks Streamlit's icon font.
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&display=swap');
h1, h2, h3 { font-family: 'Playfair Display', Georgia, serif !important; }
.block-container { padding-top: 2rem; padding-bottom: 4rem; }
@media (max-width: 640px) {
  .block-container { padding: 1rem 0.75rem 4rem 0.75rem; }
  h1 { font-size: 1.7rem !important; }
  h2 { font-size: 1.35rem !important; }
  h3 { font-size: 1.15rem !important; }
}
/* Comfortable touch targets; 16px inputs stop iOS from zooming in. */
.stButton > button, .stFormSubmitButton > button, .stDownloadButton > button { min-height: 2.9rem; font-weight: 600; }
input, textarea { font-size: 16px !important; }
.stTabs [data-baseweb="tab-list"] { gap: 2px; overflow-x: auto; scrollbar-width: none; }
.stTabs [data-baseweb="tab"] { padding: 0.4rem 0.7rem; }
details summary p { font-size: 1.02rem; font-weight: 600; }

.lc-hero { text-align: center; margin: 0.5rem 0 1rem; }
.lc-hero .lc-sub { color: #7a6b5e; font-style: italic; margin-top: -0.4rem; }
.lc-code { font-family: ui-monospace, monospace; font-size: 2.2rem; font-weight: 700; letter-spacing: 0.35rem;
  color: #8b2e38; text-align: center; }
.lc-card { background: #fff; border: 1.5px solid #e6dcd0; border-radius: 12px; padding: 0.75rem 1rem;
  margin-bottom: 0.5rem; color: #2c1518; }
.lc-card .lc-meta { color: #6b5b50; font-size: 0.9rem; margin-top: 0.15rem; }
.lc-card .lc-desc { color: #8b7b6e; font-size: 0.85rem; font-style: italic; margin-top: 0.2rem; }
.lc-num { display: inline-flex; align-items: center; justify-content: center; width: 1.7rem; height: 1.7rem;
  border-radius: 50%; background: #8b2e38; color: #fff; font-weight: 700; font-size: 0.85rem; margin-right: 0.5rem; }
.lc-rank { display: flex; align-items: center; gap: 0.75rem; }
.lc-rank.me { border: 2px solid #8b2e38; background: #fdf6f2; }
.lc-rank.first { border-color: #c9a96e; background: linear-gradient(135deg, #fffdf5, #fff6e6); }
.lc-medal { flex: none; width: 2.2rem; height: 2.2rem; border-radius: 50%; display: flex; align-items: center;
  justify-content: center; font-weight: 700; background: #ece4da; color: #6b5b50; }
.lc-medal.m1 { background: #c9a96e; color: #fff; } .lc-medal.m2 { background: #a0a0a0; color: #fff; }
.lc-medal.m3 { background: #b07840; color: #fff; }
.lc-rank .lc-who { flex: 1; min-width: 0; overflow-wrap: anywhere; font-weight: 600; }
.lc-rank .lc-detail { font-weight: 400; color: #7a6b5e; font-size: 0.8rem; }
.lc-rank .lc-pts { text-align: right; font-family: 'Playfair Display', Georgia, serif; font-size: 1.45rem;
  font-weight: 700; line-height: 1; }
.lc-rank .lc-of { font-size: 0.7rem; color: #7a6b5e; font-family: sans-serif; font-weight: 400; }
table.lc-bd { width: 100%; border-collapse: collapse; font-size: 0.92rem; color: #2c1518; }
table.lc-bd td, table.lc-bd th { padding: 0.35rem 0.3rem; border-bottom: 1px solid #eee4d8; text-align: left;
  vertical-align: top; overflow-wrap: anywhere; }
table.lc-bd th { color: #7a6b5e; font-weight: 600; font-size: 0.8rem; }
table.lc-bd td.pts { text-align: right; font-weight: 700; white-space: nowrap; }
.lc-ok { color: #2a7a2a; } .lc-mid { color: #9a6b20; } .lc-bad { color: #9a3535; }
.lc-total { font-size: 1.6rem; font-weight: 700; font-family: 'Playfair Display', Georgia, serif; color: #8b2e38; }
.lc-footer { text-align: center; color: #b5a595; font-style: italic; font-size: 0.8rem; margin-top: 2rem; }
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def esc(s) -> str:
    return html.escape(str(s if s is not None else ""))


def lang_for(tasting=None) -> str:
    return st.session_state.get("lang") or (tasting or {}).get("lang") or "es"


def lang_picker(L, key="lang_pick"):
    keys = list(LANGS)
    sel = st.selectbox(t("language", L), keys, index=keys.index(L), format_func=LANGS.get, key=key)
    if sel != L:
        st.session_state["lang"] = sel
        st.rerun()


def hero(title, subtitle=""):
    sub = f'<div class="lc-sub">{esc(subtitle)}</div>' if subtitle else ""
    st.markdown(f'<div class="lc-hero"><h1>🍷 {esc(title)}</h1>{sub}</div>', unsafe_allow_html=True)


def footer(L):
    st.markdown(f'<div class="lc-footer">{esc(t("footer", L))}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------- formatting

def fmt_num(v, suffix=""):
    if v is None or v == "":
        return "—"
    try:
        f = float(v)
    except (TypeError, ValueError):
        return esc(v)
    return (f"{f:g}" if f != int(f) else f"{int(f)}") + suffix


def fmt_field(field, v):
    if field == "alcohol":
        return fmt_num(v, " %")
    if field == "price":
        return fmt_num(v, " €")
    if field == "rating":
        return fmt_num(v, "/5")
    return v if v not in (None, "") else "—"


def wine_meta(w, L) -> str:
    parts = []
    if w.get("type"):
        parts.append(t("type_" + w["type"], L))
    for f, _ in FIELDS:
        if w.get(f) not in (None, ""):
            parts.append(fmt_field(f, w[f]))
    if w.get("year"):
        parts.append(w["year"])
    return " · ".join(esc(p) for p in parts)


def wine_card(w, L, number=None, show_desc=True):
    num = f'<span class="lc-num">{number}</span>' if number is not None else ""
    desc = (f'<div class="lc-desc">{esc(w["description"])}</div>'
            if show_desc and w.get("description") else "")
    st.markdown(f'<div class="lc-card">{num}<b>{esc(w["name"])}</b><div class="lc-meta">{wine_meta(w, L)}</div>'
                f'{desc}</div>', unsafe_allow_html=True)


def pct_class(pct):
    return "lc-ok" if pct >= 70 else "lc-mid" if pct >= 40 else "lc-bad"


def rank_card(r, L, me_id=None, positions=None):
    pct = round(100 * r["total"] / r["max_total"]) if r["max_total"] else 0
    is_me = r["participant_id"] == me_id
    cls = "lc-card lc-rank" + (" me" if is_me else "") + (" first" if r["rank"] == 1 and r["total"] > 0 else "")
    medal = f"m{r['rank']}" if r["rank"] <= 3 else ""
    detail = ""
    if is_me and r["per_wine"]:
        detail = '<div class="lc-detail">' + " · ".join(
            f"#{pw['position'] + 1}: {pw['score']['total']}" for pw in r["per_wine"]) + "</div>"
    you = f" ({esc(t('you', L))})" if is_me else ""
    st.markdown(
        f'<div class="{cls}"><div class="lc-medal {medal}">{r["rank"]}</div>'
        f'<div class="lc-who">{esc(r["participant"])}{you}{detail}</div>'
        f'<div class="lc-pts {pct_class(pct)}">{r["total"]}<div class="lc-of">{esc(t("of", L))} {r["max_total"]}</div>'
        f'</div></div>', unsafe_allow_html=True)


def breakdown_table(guess, wine, score, L):
    rows = []
    for f, mx in FIELDS:
        if f not in score["breakdown"]:
            continue
        pts = score["breakdown"][f]
        cls = "lc-ok" if pts == mx else "lc-mid" if pts > 0 else "lc-bad"
        dot = "●"
        rows.append(f'<tr><td><span class="{cls}">{dot}</span> {esc(t("score_" + f, L))}</td>'
                    f'<td>{esc(fmt_field(f, guess.get(f)))}</td><td>{esc(fmt_field(f, wine.get(f)))}</td>'
                    f'<td class="pts {cls}">+{pts}</td></tr>')
    st.markdown(
        f'<div class="lc-total">{score["total"]} <span style="font-size:0.9rem">/ {score["max_score"]}</span></div>'
        f'<table class="lc-bd"><tr><th></th><th>{esc(t("yours", L))}</th><th>{esc(t("real", L))}</th><th></th></tr>'
        + "".join(rows) + "</table>", unsafe_allow_html=True)


# ---------------------------------------------------------------- links & QR

def base_url() -> str:
    configured = secret("PUBLIC_URL")
    if configured:
        return configured.rstrip("/")
    try:
        url = st.context.url  # e.g. https://x.streamlit.app/?sala=...
        if url:
            return url.split("?")[0].rstrip("/")
    except Exception:
        pass
    host = st.context.headers.get("Host", "localhost:8501")
    scheme = "https" if "streamlit.app" in host else "http"
    return f"{scheme}://{host}"


def participant_url(code, token=None) -> str:
    url = f"{base_url()}/?sala={quote(code)}"
    return url + f"&p={quote(token)}" if token else url


def qr_png(data: str) -> bytes:
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=2)
    q.add_data(data)
    q.make(fit=True)
    buf = io.BytesIO()
    q.make_image(fill_color=ACCENT, back_color="white").save(buf, format="PNG")
    return buf.getvalue()


def show_qr(url, width=240):
    c = st.columns([1, 3, 1])[1] if width >= 200 else st.container()
    with c:
        st.image(qr_png(url), width=width)
    st.code(url, language=None, wrap_lines=True)


# ---------------------------------------------------------------- live updates

def sync_version(tasting_id):
    """Call once per full run: remembers the data version this page was drawn with."""
    st.session_state[f"_v_{tasting_id}"] = db.get_version(tasting_id)


@st.fragment(run_every=4)
def live_updates(tasting_id):
    """Polls the tasting version and redraws the whole page when someone changed something."""
    key = f"_v_{tasting_id}"
    v = db.get_version(tasting_id)
    if st.session_state.get(key) != v:
        st.session_state[key] = v
        st.rerun(scope="app")


CELEBRATION_JS = """
<script>
try {
  const ctx = new (window.AudioContext || window.webkitAudioContext)();
  [[523.25,0],[659.25,.15],[783.99,.3],[1046.5,.45],[783.99,.7],[1046.5,.85]].forEach(([f,t]) => {
    const o = ctx.createOscillator(), g = ctx.createGain();
    o.type = 'triangle'; o.frequency.value = f;
    g.gain.setValueAtTime(0.25, ctx.currentTime + t);
    g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + t + 0.3);
    o.connect(g); g.connect(ctx.destination);
    o.start(ctx.currentTime + t); o.stop(ctx.currentTime + t + 0.35);
  });
} catch (e) {}
</script>
"""


def celebrate(key):
    """Balloons + fanfare, once per browser session for each event key."""
    flag = f"_celebrated_{key}"
    if st.session_state.get(flag):
        return
    st.session_state[flag] = True
    st.balloons()
    components.html(CELEBRATION_JS, height=0)


# ---------------------------------------------------------------- forms

def _merge(options, extra):
    out = list(options)
    low = {o.lower() for o in out}
    for e in extra:
        if e and e.lower() not in low:
            out.append(e)
            low.add(e.lower())
    return out


def wine_form(key, L, opts, d=None, *, submit_label, review=False, cellar_choice=None):
    """Organizer form for a wine (inside st.form: nothing reruns until submitted).

    Returns (wine dict, verified, save_to_cellar) when submitted, else None.
    Unknown grapes/D.O.s from the defaults or typed by the organizer are kept, not dropped.
    """
    d = d or {}
    cur_grapes = [g.strip() for g in (d.get("grape") or "").split(",") if g.strip()]
    grapes = _merge(opts["grapes"], cur_grapes)
    origins = _merge(opts["origins"], [d.get("origin")])
    agings = _merge(opts["agings"], [d.get("aging")])

    def _idx(lst, v):
        return lst.index(v) if v in lst else None

    with st.form(key, border=True):
        name = st.text_input(t("f_name", L), value=d.get("name", ""))
        g = st.multiselect(t("f_grape", L), grapes, default=cur_grapes, accept_new_options=True,
                           placeholder=t("choose_or_type", L))
        c1, c2 = st.columns(2)
        o = c1.selectbox(t("f_origin", L), origins, index=_idx(origins, d.get("origin")),
                         accept_new_options=True, placeholder=t("choose_or_type", L))
        ag = c2.selectbox(t("f_aging", L), agings, index=_idx(agings, d.get("aging")),
                          placeholder=t("choose", L))
        c1, c2, c3 = st.columns(3)
        al = c1.number_input(t("f_alcohol", L), 0.0, 25.0, _f(d.get("alcohol")), 0.5, placeholder="13.5")
        pr = c2.number_input(t("f_price", L), 0.0, 5000.0, _f(d.get("price")), 0.5, placeholder="12")
        rt = c3.number_input(t("f_rating", L), 0.0, 5.0, _f(d.get("rating")), 0.1, placeholder="3.9")
        c1, c2 = st.columns(2)
        tp = c1.selectbox(t("f_type", L), WINE_TYPES, index=_idx(WINE_TYPES, d.get("type")),
                          format_func=lambda x: t("type_" + x, L), placeholder=t("choose", L))
        yr = c2.text_input(t("f_year", L), value=d.get("year", ""), max_chars=4)
        desc = st.text_area(t("f_description", L), value=d.get("description", ""), height=80,
                            placeholder=t("f_description_placeholder", L))
        verified = True
        if review:
            st.warning(t("ai_review_warning", L))
            verified = st.checkbox(t("verified_check", L), value=False)
        to_cellar = st.checkbox(cellar_choice, value=True) if cellar_choice else False
        if st.form_submit_button(submit_label, type="primary", width="stretch"):
            if not name.strip():
                st.error(t("name_required", L))
                return None
            wine = {"name": name, "winery": d.get("winery", ""), "grape": ", ".join(g), "origin": o or "",
                    "aging": ag or "", "alcohol": al, "price": pr, "rating": rt, "type": tp or "",
                    "year": yr, "description": desc, "source": d.get("source", "manual")}
            return wine, verified, to_cellar
    return None


def _f(v):
    try:
        return float(v) if v not in (None, "") else None
    except (TypeError, ValueError):
        return None


def confirm_button(label, confirm_text, key, L, *, danger_label=None, disabled=False, width="stretch"):
    """A popover asking for confirmation. Returns True when confirmed."""
    with st.popover(label, disabled=disabled, width=width):
        st.write(confirm_text)
        return st.button(danger_label or t("yes_do_it", L), key=key, type="primary", width="stretch")


def flash(msg, kind="success"):
    """Show a message after the next rerun."""
    st.session_state["_flash"] = (kind, msg)


def show_flash():
    f = st.session_state.pop("_flash", None)
    if f:
        getattr(st, f[0])(f[1])


def slow_down_failed_login():
    n = st.session_state.get("_failed_logins", 0) + 1
    st.session_state["_failed_logins"] = n
    time.sleep(min(n, 5))
