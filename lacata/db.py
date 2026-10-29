"""Persistent storage (SQLAlchemy Core).

Works with SQLite (local default) and PostgreSQL (set DATABASE_URL, e.g. Supabase/Neon,
so data survives Streamlit Cloud restarts). Every multi-step change runs inside one
transaction, so concurrent participants cannot overwrite each other.

Every mutation of a tasting bumps tastings.version; clients poll it to auto-refresh.
"""

import hashlib
import hmac
import json
import os
import secrets
from datetime import datetime, timezone

from sqlalchemy import (Boolean, Column, DateTime, Float, ForeignKey, Integer, MetaData, String, Table, Text,
                        UniqueConstraint, create_engine, event, func, select)
from sqlalchemy.exc import IntegrityError

from .options import default_options

metadata = MetaData()


def _now():
    return datetime.now(timezone.utc)


WINE_COLS = ["name", "winery", "grape", "origin", "aging", "rating", "alcohol", "price", "type", "year",
             "description", "source"]
NUMERIC = {"rating", "alcohol", "price"}


def _wine_columns():
    return [
        Column("name", String(200), nullable=False),
        Column("winery", String(200), default=""),
        Column("grape", String(300), default=""),
        Column("origin", String(120), default=""),
        Column("aging", String(60), default=""),
        Column("rating", Float, nullable=True),
        Column("alcohol", Float, nullable=True),
        Column("price", Float, nullable=True),
        Column("type", String(40), default=""),
        Column("year", String(10), default=""),
        Column("description", Text, default=""),
        Column("source", String(20), default="manual"),
    ]


cellar = Table(
    "cellar", metadata,
    Column("id", Integer, primary_key=True),
    *_wine_columns(),
    Column("created_at", DateTime(timezone=True), default=_now),
)

tastings = Table(
    "tastings", metadata,
    Column("id", Integer, primary_key=True),
    Column("code", String(8), unique=True, nullable=False),
    Column("name", String(120), default=""),
    Column("pin_hash", String(200), nullable=False),
    Column("lang", String(4), default="es"),
    Column("started", Boolean, default=False),
    Column("options", Text, nullable=False),
    Column("version", Integer, default=0, nullable=False),
    Column("created_at", DateTime(timezone=True), default=_now),
)

wines = Table(
    "wines", metadata,
    Column("id", Integer, primary_key=True),
    Column("tasting_id", Integer, ForeignKey("tastings.id", ondelete="CASCADE"), nullable=False, index=True),
    Column("position", Integer, nullable=False),
    *_wine_columns(),
    Column("cellar_id", Integer, nullable=True),
    Column("revealed", Boolean, default=False, nullable=False),
    Column("needs_review", Boolean, default=False, nullable=False),
)

participants = Table(
    "participants", metadata,
    Column("id", Integer, primary_key=True),
    Column("tasting_id", Integer, ForeignKey("tastings.id", ondelete="CASCADE"), nullable=False, index=True),
    Column("name", String(60), nullable=False),
    Column("token", String(40), unique=True, nullable=False),
    Column("created_at", DateTime(timezone=True), default=_now),
    UniqueConstraint("tasting_id", "name"),
)

guesses = Table(
    "guesses", metadata,
    Column("participant_id", Integer, ForeignKey("participants.id", ondelete="CASCADE"), primary_key=True),
    Column("wine_id", Integer, ForeignKey("wines.id", ondelete="CASCADE"), primary_key=True),
    Column("grape", String(300), default=""),
    Column("origin", String(120), default=""),
    Column("aging", String(60), default=""),
    Column("rating", Float, nullable=True),
    Column("alcohol", Float, nullable=True),
    Column("price", Float, nullable=True),
    Column("liking", Integer, nullable=True),
    Column("created_at", DateTime(timezone=True), default=_now),
)

GUESS_COLS = ["grape", "origin", "aging", "rating", "alcohol", "price", "liking"]


class TastingError(Exception):
    """Expected, user-facing failure. `code` is an i18n key."""

    def __init__(self, code):
        super().__init__(code)
        self.code = code


# ---------------------------------------------------------------- engine

_engine = None


def default_url():
    return os.environ.get("DATABASE_URL") or "sqlite:///" + os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lacata.db")


def get_engine(url=None):
    global _engine
    if _engine is None or url:
        url = url or default_url()
        if url.startswith("postgres://"):  # Heroku/Supabase style
            url = "postgresql+psycopg://" + url[len("postgres://"):]
        elif url.startswith("postgresql://"):
            url = "postgresql+psycopg://" + url[len("postgresql://"):]
        if url.startswith("sqlite"):
            eng = create_engine(url, connect_args={"check_same_thread": False, "timeout": 15})

            @event.listens_for(eng, "connect")
            def _pragmas(dbapi_conn, _):
                cur = dbapi_conn.cursor()
                cur.execute("PRAGMA journal_mode=WAL")
                cur.execute("PRAGMA foreign_keys=ON")
                cur.close()
        else:
            eng = create_engine(url, pool_pre_ping=True)
        metadata.create_all(eng)
        _engine = eng
    return _engine


def _bump(conn, tasting_id):
    conn.execute(tastings.update().where(tastings.c.id == tasting_id).values(version=tastings.c.version + 1))


# ---------------------------------------------------------------- helpers

def _hash_pin(pin: str) -> str:
    salt = secrets.token_hex(8)
    h = hashlib.pbkdf2_hmac("sha256", pin.encode(), salt.encode(), 100_000).hex()
    return f"{salt}${h}"


def _check_pin(pin: str, stored: str) -> bool:
    salt, h = stored.split("$", 1)
    return hmac.compare_digest(hashlib.pbkdf2_hmac("sha256", pin.encode(), salt.encode(), 100_000).hex(), h)


CODE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"


def _clean_wine(w: dict) -> dict:
    out = {}
    for k in WINE_COLS:
        v = w.get(k)
        if k in NUMERIC:
            try:
                out[k] = float(str(v).replace(",", ".")) if v not in (None, "") else None
            except ValueError:
                out[k] = None
        else:
            out[k] = (str(v) if v is not None else "").strip()
    out["source"] = out["source"] or "manual"
    return out


def _tasting_dict(row):
    d = dict(row._mapping)
    d["options"] = json.loads(d["options"])
    d.pop("pin_hash", None)
    return d


# ---------------------------------------------------------------- tastings

def create_tasting(name: str, pin: str, lang: str = "es") -> dict:
    if len(pin or "") < 4:
        raise TastingError("pin_too_short")
    eng = get_engine()
    for _ in range(20):
        code = "".join(secrets.choice(CODE_ALPHABET) for _ in range(5))
        try:
            with eng.begin() as conn:
                conn.execute(tastings.insert().values(
                    code=code, name=name.strip(), pin_hash=_hash_pin(pin), lang=lang,
                    options=json.dumps(default_options(), ensure_ascii=False)))
            return get_tasting(code)
        except IntegrityError:
            continue
    raise RuntimeError("could not allocate tasting code")


def get_tasting(code: str):
    if not code:
        return None
    with get_engine().connect() as conn:
        row = conn.execute(select(tastings).where(tastings.c.code == code.strip().upper())).first()
    return _tasting_dict(row) if row else None


def check_pin(code: str, pin: str) -> bool:
    with get_engine().connect() as conn:
        row = conn.execute(select(tastings.c.pin_hash).where(tastings.c.code == (code or "").strip().upper())).first()
    return bool(row) and _check_pin(pin or "", row[0])


def get_version(tasting_id: int) -> int:
    with get_engine().connect() as conn:
        return conn.execute(select(tastings.c.version).where(tastings.c.id == tasting_id)).scalar() or 0


def update_tasting(tasting_id: int, **values):
    if "options" in values:
        values["options"] = json.dumps(values["options"], ensure_ascii=False)
    with get_engine().begin() as conn:
        conn.execute(tastings.update().where(tastings.c.id == tasting_id).values(**values))
        _bump(conn, tasting_id)


def add_options(tasting_id: int, grapes=(), origins=()) -> list:
    """Add unknown grapes/origins to the tasting's option lists. Returns what was added."""
    added = []
    with get_engine().begin() as conn:
        raw = conn.execute(select(tastings.c.options).where(tastings.c.id == tasting_id)).scalar()
        opts = json.loads(raw)
        for key, vals in (("grapes", grapes), ("origins", origins)):
            known = {v.lower() for v in opts[key]}
            for v in vals:
                v = (v or "").strip()
                if v and v.lower() not in known:
                    opts[key].append(v)
                    known.add(v.lower())
                    added.append(v)
        if added:
            conn.execute(tastings.update().where(tastings.c.id == tasting_id).values(
                options=json.dumps(opts, ensure_ascii=False)))
            _bump(conn, tasting_id)
    return added


def delete_tasting(tasting_id: int):
    with get_engine().begin() as conn:
        pids = select(participants.c.id).where(participants.c.tasting_id == tasting_id)
        wids = select(wines.c.id).where(wines.c.tasting_id == tasting_id)
        conn.execute(guesses.delete().where(guesses.c.participant_id.in_(pids) | guesses.c.wine_id.in_(wids)))
        conn.execute(participants.delete().where(participants.c.tasting_id == tasting_id))
        conn.execute(wines.delete().where(wines.c.tasting_id == tasting_id))
        conn.execute(tastings.delete().where(tastings.c.id == tasting_id))


# ---------------------------------------------------------------- tasting wines

def list_wines(tasting_id: int) -> list:
    with get_engine().connect() as conn:
        rows = conn.execute(select(wines).where(wines.c.tasting_id == tasting_id).order_by(wines.c.position)).all()
    return [dict(r._mapping) for r in rows]


def add_wine(tasting_id: int, wine: dict, cellar_id=None, needs_review=False) -> int:
    data = _clean_wine(wine)
    with get_engine().begin() as conn:
        pos = conn.execute(select(func.coalesce(func.max(wines.c.position), -1))
                           .where(wines.c.tasting_id == tasting_id)).scalar() + 1
        wid = conn.execute(wines.insert().values(tasting_id=tasting_id, position=pos, cellar_id=cellar_id,
                                                 needs_review=needs_review, **data)).inserted_primary_key[0]
        _bump(conn, tasting_id)
    return wid


def update_wine(wine_id: int, wine: dict, needs_review=False):
    data = _clean_wine(wine)
    with get_engine().begin() as conn:
        row = conn.execute(select(wines.c.tasting_id, wines.c.source).where(wines.c.id == wine_id)).first()
        if not row:
            return
        data["source"] = row.source
        conn.execute(wines.update().where(wines.c.id == wine_id).values(needs_review=needs_review, **data))
        _bump(conn, row.tasting_id)


def delete_wine(wine_id: int):
    with get_engine().begin() as conn:
        tid = conn.execute(select(wines.c.tasting_id).where(wines.c.id == wine_id)).scalar()
        if tid is None:
            return
        conn.execute(guesses.delete().where(guesses.c.wine_id == wine_id))
        conn.execute(wines.delete().where(wines.c.id == wine_id))
        _bump(conn, tid)


def move_wine(wine_id: int, delta: int):
    with get_engine().begin() as conn:
        row = conn.execute(select(wines.c.tasting_id, wines.c.position).where(wines.c.id == wine_id)).first()
        if not row:
            return
        ordered = conn.execute(select(wines.c.id).where(wines.c.tasting_id == row.tasting_id)
                               .order_by(wines.c.position)).scalars().all()
        i = ordered.index(wine_id)
        j = i + delta
        if not 0 <= j < len(ordered):
            return
        ordered[i], ordered[j] = ordered[j], ordered[i]
        for pos, wid in enumerate(ordered):
            conn.execute(wines.update().where(wines.c.id == wid).values(position=pos))
        _bump(conn, row.tasting_id)


def reveal_wine(wine_id: int, revealed=True):
    with get_engine().begin() as conn:
        tid = conn.execute(select(wines.c.tasting_id).where(wines.c.id == wine_id)).scalar()
        conn.execute(wines.update().where(wines.c.id == wine_id).values(revealed=revealed))
        _bump(conn, tid)


# ---------------------------------------------------------------- participants

def join(tasting_id: int, name: str) -> dict:
    name = " ".join((name or "").split())[:60]
    if not name:
        raise TastingError("name_required")
    token = secrets.token_urlsafe(12)
    try:
        with get_engine().begin() as conn:
            pid = conn.execute(participants.insert().values(tasting_id=tasting_id, name=name, token=token)
                               ).inserted_primary_key[0]
            _bump(conn, tasting_id)
    except IntegrityError:
        raise TastingError("name_taken")
    return {"id": pid, "name": name, "token": token, "tasting_id": tasting_id}


def participant_by_token(token: str):
    if not token:
        return None
    with get_engine().connect() as conn:
        row = conn.execute(select(participants).where(participants.c.token == token)).first()
    return dict(row._mapping) if row else None


def list_participants(tasting_id: int) -> list:
    with get_engine().connect() as conn:
        rows = conn.execute(select(participants).where(participants.c.tasting_id == tasting_id)
                            .order_by(participants.c.created_at, participants.c.id)).all()
    return [dict(r._mapping) for r in rows]


def remove_participant(participant_id: int):
    with get_engine().begin() as conn:
        tid = conn.execute(select(participants.c.tasting_id).where(participants.c.id == participant_id)).scalar()
        if tid is None:
            return
        conn.execute(guesses.delete().where(guesses.c.participant_id == participant_id))
        conn.execute(participants.delete().where(participants.c.id == participant_id))
        _bump(conn, tid)


# ---------------------------------------------------------------- guesses

def list_guesses(tasting_id: int) -> dict:
    """{(participant_id, wine_id): guess dict}"""
    q = (select(guesses).join(wines, guesses.c.wine_id == wines.c.id).where(wines.c.tasting_id == tasting_id))
    with get_engine().connect() as conn:
        rows = conn.execute(q).all()
    return {(r.participant_id, r.wine_id): dict(r._mapping) for r in rows}


def submit_guess(participant_id: int, wine_id: int, guess: dict):
    """Atomic: refuses if the wine is revealed, belongs to another tasting, or a guess already exists."""
    data = {k: guess.get(k) for k in GUESS_COLS}
    for k in ("grape", "origin", "aging"):
        data[k] = data[k] or ""
    try:
        with get_engine().begin() as conn:
            p = conn.execute(select(participants.c.tasting_id).where(participants.c.id == participant_id)).first()
            w = conn.execute(select(wines.c.tasting_id, wines.c.revealed).where(wines.c.id == wine_id)).first()
            if not p or not w or p.tasting_id != w.tasting_id:
                raise TastingError("not_found")
            started = conn.execute(select(tastings.c.started).where(tastings.c.id == w.tasting_id)).scalar()
            if not started:
                raise TastingError("not_started")
            if w.revealed:
                raise TastingError("already_revealed")
            # The primary key (participant, wine) rejects a second guess, also under races.
            conn.execute(guesses.insert().values(participant_id=participant_id, wine_id=wine_id, **data))
            _bump(conn, w.tasting_id)
    except IntegrityError:
        raise TastingError("already_sent")


def cancel_guess(participant_id: int, wine_id: int):
    """Only allowed while the wine is still hidden — otherwise people could copy the answer."""
    with get_engine().begin() as conn:
        w = conn.execute(select(wines.c.tasting_id, wines.c.revealed).where(wines.c.id == wine_id)).first()
        if not w:
            raise TastingError("not_found")
        if w.revealed:
            raise TastingError("already_revealed")
        conn.execute(guesses.delete().where((guesses.c.participant_id == participant_id)
                                            & (guesses.c.wine_id == wine_id)))
        _bump(conn, w.tasting_id)


def set_liking(participant_id: int, wine_id: int, liking):
    """Liking is not scored, so it may change at any time."""
    with get_engine().begin() as conn:
        tid = conn.execute(select(wines.c.tasting_id).where(wines.c.id == wine_id)).scalar()
        conn.execute(guesses.update().where((guesses.c.participant_id == participant_id)
                                            & (guesses.c.wine_id == wine_id)).values(liking=liking))
        _bump(conn, tid)


# ---------------------------------------------------------------- cellar

def cellar_list(query: str = "") -> list:
    q = select(cellar).order_by(cellar.c.name)
    if query:
        like = f"%{query}%"
        q = q.where(cellar.c.name.ilike(like) | cellar.c.grape.ilike(like) | cellar.c.origin.ilike(like)
                    | cellar.c.winery.ilike(like))
    with get_engine().connect() as conn:
        return [dict(r._mapping) for r in conn.execute(q).all()]


def cellar_add(wine: dict) -> int:
    with get_engine().begin() as conn:
        return conn.execute(cellar.insert().values(**_clean_wine(wine))).inserted_primary_key[0]


def cellar_update(cellar_id: int, wine: dict):
    data = _clean_wine(wine)
    data.pop("source")
    with get_engine().begin() as conn:
        conn.execute(cellar.update().where(cellar.c.id == cellar_id).values(**data))


def cellar_delete(cellar_id: int):
    with get_engine().begin() as conn:
        conn.execute(cellar.delete().where(cellar.c.id == cellar_id))


def cellar_count() -> int:
    with get_engine().connect() as conn:
        return conn.execute(select(func.count()).select_from(cellar)).scalar()
