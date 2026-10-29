from lacata.scoring import (calc_score, rankings, score_aging, score_grape, score_origin, score_price,
                            split_grapes)


def test_grape_exact_and_order_insensitive():
    assert score_grape("Garnacha, Tempranillo", "tempranillo,garnacha") == 25


def test_grape_selecting_everything_is_not_rewarded():
    every = ", ".join(["Tempranillo", "Garnacha", "Monastrell", "Bobal", "Mencía", "Syrah", "Merlot", "Verdejo"])
    assert score_grape(every, "Tempranillo") <= 4


def test_grape_partial_and_accents():
    assert score_grape("Mencia", "Mencía") == 25
    assert score_grape("Tempranillo", "Tempranillo, Graciano") == 12  # 1/2 of 25, rounded
    assert score_grape("", "Tempranillo") == 0


def test_split_grapes_keeps_hyphenated_names():
    assert split_grapes("Utiel-Requena Bobal / Garnacha") == {"utiel-requena bobal", "garnacha"}


def test_origin_exact_region_and_miss():
    assert score_origin("Rioja", "rioja") == 25
    assert score_origin("Navarra", "Rioja") == 10
    assert score_origin("Priorat", "Rioja") == 0
    assert score_origin("Nueva DO", "Otra DO") == 0


def test_aging_neighbours():
    assert score_aging("Reserva", "Reserva") == 20
    assert score_aging("Crianza", "Reserva") == 8
    assert score_aging("Joven", "Reserva") == 0


def test_price_relative_for_expensive_wines():
    assert score_price(10, 12) == 10
    assert score_price(52, 60) == 10  # 8 € off but within 15 %
    assert score_price(100, 60) == 0


def test_empty_guess_scores_zero_but_counts_max():
    actual = {"grape": "Tempranillo", "origin": "Rioja", "aging": "Crianza", "rating": 4.0, "alcohol": 14.0,
              "price": 15.0}
    sc = calc_score({}, actual)
    assert sc["total"] == 0 and sc["max_score"] == 100


def test_unknown_real_fields_are_not_scored():
    sc = calc_score({"grape": "Tempranillo", "price": 10}, {"grape": "Tempranillo", "price": None, "rating": ""})
    assert sc["max_score"] == 25 and sc["total"] == 25


def test_rankings_ties_share_position_and_only_revealed_count():
    people = [{"id": 1, "name": "Ana"}, {"id": 2, "name": "Bea"}, {"id": 3, "name": "Carlos"}]
    wines = [{"id": 10, "revealed": True, "grape": "Tempranillo"},
             {"id": 11, "revealed": False, "grape": "Garnacha"}]
    guesses = {(1, 10): {"grape": "Tempranillo"}, (2, 10): {"grape": "Tempranillo"},
               (3, 10): {"grape": "Bobal"}, (3, 11): {"grape": "Garnacha"}}
    r = rankings(people, wines, guesses)
    assert [(x["participant"], x["rank"], x["total"]) for x in r] == [("Ana", 1, 25), ("Bea", 1, 25),
                                                                      ("Carlos", 3, 0)]
    assert all(x["max_total"] == 25 for x in r)
