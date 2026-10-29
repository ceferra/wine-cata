"""Settings from Streamlit secrets, falling back to environment variables."""

import os


def secret(name: str, default=None):
    try:
        import streamlit as st
        if name in st.secrets:
            return st.secrets[name]
    except Exception:  # no secrets.toml, or not running under Streamlit
        pass
    return os.environ.get(name, default)


def export_database_url():
    """db.py reads DATABASE_URL from the environment; copy it over from secrets."""
    url = secret("DATABASE_URL")
    if url:
        os.environ["DATABASE_URL"] = url
