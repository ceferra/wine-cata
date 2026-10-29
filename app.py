"""La Cata — blind wine tasting with automatic scoring.

  streamlit run app.py

URLs:  /                          home: join or create a tasting
       /?sala=CODE                participant (gets &p=<personal token> after joining)
       /?sala=CODE&org=1          organizer (asks for the tasting PIN)
       /?sala=CODE&pantalla=1     projector screen (QR + ranking, no hidden answers)
"""

import streamlit as st

from lacata.config import export_database_url

export_database_url()

from lacata import catalog, db, ui  # noqa: E402  (DATABASE_URL must be set first)
from lacata.views import home, organizer, participant, screen  # noqa: E402


@st.cache_resource
def _seed_catalog():
    """Once per server start: an empty cellar (new install, or SQLite wiped by a Streamlit Cloud
    restart) gets the bundled catalog of common wines back."""
    if db.cellar_count() == 0:
        db.cellar_seed(catalog.load())


_seed_catalog()

qp = st.query_params
code = (qp.get("sala") or "").strip().upper()
is_org = qp.get("org") == "1"
is_screen = qp.get("pantalla") == "1"

st.set_page_config(page_title="La Cata", page_icon="🍷", layout="wide" if (is_org or is_screen) else "centered",
                   initial_sidebar_state="collapsed")
ui.inject_css()

tasting = db.get_tasting(code) if code else None
if not tasting:
    home.render(bad_code=bool(code))
elif is_org:
    organizer.render(tasting)
elif is_screen:
    screen.render(tasting)
else:
    participant.render(tasting)
