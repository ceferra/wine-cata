import pytest

from lacata import catalog, db
from lacata.options import DEFAULT_AGINGS, ORIGIN_REGIONS, WINE_TYPES


def test_catalog_rows_are_valid():
    wines = catalog.load()
    assert len(wines) >= 90
    names = [w["name"].lower() for w in wines]
    assert len(names) == len(set(names)), "duplicate names"
    for w in wines:
        assert w["name"] and w["grape"], w
        assert w["type"] in WINE_TYPES, w
        assert w["aging"] in DEFAULT_AGINGS + [""], w
        assert w["origin"] in ORIGIN_REGIONS, w  # every D.O. gets regional partial credit
        assert 5 <= float(w["alcohol"]) <= 22, w
        assert 0 < float(w["price"]) < 500, w


@pytest.fixture
def fresh_db(tmp_path):
    db.get_engine(f"sqlite:///{tmp_path / 'test.db'}")


def test_seed_is_idempotent_and_keeps_existing(fresh_db):
    db.cellar_add({"name": "Protos Roble", "price": 99})
    wines = catalog.load()
    assert db.cellar_seed(wines) == len(wines) - 1
    assert db.cellar_seed(wines) == 0
    protos = [w for w in db.cellar_list("Protos Roble") if w["name"] == "Protos Roble"]
    assert len(protos) == 1 and protos[0]["price"] == 99


def test_editing_a_catalog_wine_marks_it_checked(fresh_db):
    db.cellar_seed(catalog.load()[:1])
    w = db.cellar_list()[0]
    assert w["source"] == "catalog"
    db.cellar_update(w["id"], w)
    assert db.cellar_list()[0]["source"] == "catalog"
    db.cellar_update(w["id"], w, verified=True)
    assert db.cellar_list()[0]["source"] == "manual"
