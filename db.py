"""
Wine database — SQLite persistent storage.
Wines are saved once and can be reused in any tasting.
"""

import sqlite3
import os
import json

DB_FILE = os.path.join(os.path.dirname(__file__), "wines.db")


def _conn():
    c = sqlite3.connect(DB_FILE)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    return c


def init_db():
    c = _conn()
    c.execute("""
        CREATE TABLE IF NOT EXISTS wines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            grape TEXT DEFAULT '',
            origin TEXT DEFAULT '',
            aging TEXT DEFAULT '',
            rating TEXT DEFAULT '',
            alcohol TEXT DEFAULT '',
            price TEXT DEFAULT '',
            type TEXT DEFAULT '',
            year TEXT DEFAULT '',
            source TEXT DEFAULT 'manual',
            winery TEXT DEFAULT '',
            description TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.commit()
    c.close()


def add_wine(wine: dict) -> int:
    c = _conn()
    cur = c.execute(
        """INSERT INTO wines (name, grape, origin, aging, rating, alcohol, price, type, year, source, winery, description)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (wine.get("name", ""), wine.get("grape", ""), wine.get("origin", ""),
         wine.get("aging", ""), wine.get("rating", ""), wine.get("alcohol", ""),
         wine.get("price", ""), wine.get("type", ""), wine.get("year", ""),
         wine.get("source", "manual"), wine.get("winery", ""), wine.get("description", ""))
    )
    c.commit()
    wid = cur.lastrowid
    c.close()
    return wid


def get_all_wines() -> list:
    c = _conn()
    rows = c.execute("SELECT * FROM wines ORDER BY name").fetchall()
    c.close()
    return [dict(r) for r in rows]


def search_wines(query: str) -> list:
    c = _conn()
    q = f"%{query}%"
    rows = c.execute(
        "SELECT * FROM wines WHERE name LIKE ? OR grape LIKE ? OR origin LIKE ? OR winery LIKE ? ORDER BY name",
        (q, q, q, q)
    ).fetchall()
    c.close()
    return [dict(r) for r in rows]


def update_wine(wine_id: int, wine: dict):
    c = _conn()
    c.execute(
        """UPDATE wines SET name=?, grape=?, origin=?, aging=?, rating=?, alcohol=?, price=?, type=?, year=?, winery=?, description=?
           WHERE id=?""",
        (wine.get("name", ""), wine.get("grape", ""), wine.get("origin", ""),
         wine.get("aging", ""), wine.get("rating", ""), wine.get("alcohol", ""),
         wine.get("price", ""), wine.get("type", ""), wine.get("year", ""),
         wine.get("winery", ""), wine.get("description", ""), wine_id)
    )
    c.commit()
    c.close()


def delete_wine(wine_id: int):
    c = _conn()
    c.execute("DELETE FROM wines WHERE id=?", (wine_id,))
    c.commit()
    c.close()


def wine_to_session(db_wine: dict) -> dict:
    """Convert a DB wine row to the session format."""
    return {
        "name": db_wine["name"],
        "grape": db_wine["grape"],
        "origin": db_wine["origin"],
        "aging": db_wine["aging"],
        "rating": db_wine["rating"],
        "alcohol": db_wine["alcohol"],
        "price": db_wine["price"],
        "type": db_wine["type"],
        "year": db_wine["year"],
        "description": db_wine.get("description", ""),
        "source": db_wine.get("source", "db"),
        "db_id": db_wine["id"],
    }


# Init on import
init_db()
