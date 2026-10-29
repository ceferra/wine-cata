import threading

import pytest

from lacata import db


@pytest.fixture(autouse=True)
def fresh_db(tmp_path):
    db.get_engine(f"sqlite:///{tmp_path / 'test.db'}")
    yield


def _setup(n_people=2):
    tasting = db.create_tasting("Test", "1234")
    w1 = db.add_wine(tasting["id"], {"name": "A", "grape": "Tempranillo", "origin": "Rioja"})
    w2 = db.add_wine(tasting["id"], {"name": "B", "grape": "Garnacha"})
    people = [db.join(tasting["id"], f"P{i}") for i in range(n_people)]
    db.update_tasting(tasting["id"], started=True)
    return tasting, [w1, w2], people


def test_pin_is_checked_and_hashed():
    t = db.create_tasting("x", "secret")
    assert db.check_pin(t["code"], "secret")
    assert not db.check_pin(t["code"], "wrong")
    assert "pin_hash" not in t
    with pytest.raises(db.TastingError):
        db.create_tasting("x", "12")


def test_names_are_unique_per_tasting_and_tokens_identify():
    t = db.create_tasting("x", "1234")
    p = db.join(t["id"], "Ana")
    with pytest.raises(db.TastingError, match="name_taken"):
        db.join(t["id"], "Ana")
    assert db.participant_by_token(p["token"])["name"] == "Ana"
    other = db.create_tasting("y", "1234")
    db.join(other["id"], "Ana")  # same name in another tasting is fine


def test_no_guess_before_start():
    t = db.create_tasting("x", "1234")
    w = db.add_wine(t["id"], {"name": "A"})
    p = db.join(t["id"], "Ana")
    with pytest.raises(db.TastingError, match="not_started"):
        db.submit_guess(p["id"], w, {"grape": "x"})


def test_cannot_cancel_or_resubmit_after_reveal():
    t, (w1, _), (p, _) = _setup()
    db.submit_guess(p["id"], w1, {"grape": "Bobal"})
    with pytest.raises(db.TastingError, match="already_sent"):
        db.submit_guess(p["id"], w1, {"grape": "Tempranillo"})
    db.reveal_wine(w1)
    with pytest.raises(db.TastingError, match="already_revealed"):
        db.cancel_guess(p["id"], w1)
    assert db.list_guesses(t["id"])[(p["id"], w1)]["grape"] == "Bobal"


def test_no_guess_after_reveal():
    t, (w1, _), (_, q) = _setup()
    db.reveal_wine(w1)
    with pytest.raises(db.TastingError, match="already_revealed"):
        db.submit_guess(q["id"], w1, {"grape": "Tempranillo"})


def test_cannot_guess_wine_of_other_tasting():
    _, (w1, _), _ = _setup()
    other = db.create_tasting("y", "1234")
    stranger = db.join(other["id"], "X")
    with pytest.raises(db.TastingError, match="not_found"):
        db.submit_guess(stranger["id"], w1, {"grape": "x"})


def test_removing_participant_keeps_similar_names():
    t, (w1, _), _ = _setup(0)
    ana = db.join(t["id"], "Ana")
    ana_m = db.join(t["id"], "Ana_M")
    db.submit_guess(ana["id"], w1, {"grape": "x"})
    db.submit_guess(ana_m["id"], w1, {"grape": "y"})
    db.remove_participant(ana["id"])
    assert list(db.list_guesses(t["id"])) == [(ana_m["id"], w1)]


def test_concurrent_submissions_are_not_lost():
    t, (w1, w2), _ = _setup(0)
    people = [db.join(t["id"], f"P{i}") for i in range(20)]
    errors = []

    def go(p):
        try:
            db.submit_guess(p["id"], w1, {"grape": "Tempranillo"})
            db.submit_guess(p["id"], w2, {"grape": "Garnacha"})
        except Exception as e:  # pragma: no cover
            errors.append(e)

    threads = [threading.Thread(target=go, args=(p,)) for p in people]
    for th in threads:
        th.start()
    for th in threads:
        th.join()
    assert not errors
    assert len(db.list_guesses(t["id"])) == 40


def test_delete_and_move_wine():
    t, (w1, w2), (p, _) = _setup()
    db.move_wine(w2, -1)
    assert [w["id"] for w in db.list_wines(t["id"])] == [w2, w1]
    db.submit_guess(p["id"], w1, {"grape": "x"})
    db.delete_wine(w1)
    assert [w["id"] for w in db.list_wines(t["id"])] == [w2]
    assert db.list_guesses(t["id"]) == {}


def test_add_options_reports_only_new_ones():
    t = db.create_tasting("x", "1234")
    added = db.add_options(t["id"], ["Tempranillo", "Tinta de Toro"], ["Rioja", "Arribes"])
    assert added == ["Tinta de Toro", "Arribes"]
    opts = db.get_tasting(t["code"])["options"]
    assert "Tinta de Toro" in opts["grapes"] and "Arribes" in opts["origins"]


def test_version_bumps_on_changes():
    t, (w1, _), (p, _) = _setup()
    v = db.get_version(t["id"])
    db.submit_guess(p["id"], w1, {"grape": "x"})
    assert db.get_version(t["id"]) > v


def test_cellar_roundtrip():
    cid = db.cellar_add({"name": "Viña X", "grape": "Bobal", "price": "9,5"})
    assert db.cellar_list("bobal")[0]["price"] == 9.5
    db.cellar_update(cid, {"name": "Viña Y"})
    assert db.cellar_list()[0]["name"] == "Viña Y"
    db.cellar_delete(cid)
    assert db.cellar_count() == 0
