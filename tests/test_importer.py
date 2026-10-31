import io

import pandas as pd
import pytest

from lacata import importer
from lacata.options import default_options

OPTS = default_options()


def _wines(text):
    return importer.rows_to_wines(importer.parse_text_table(text), OPTS)


def test_templates_round_trip():
    for lang in ("es", "en", "va"):
        wines, warnings, ignored = importer.rows_to_wines(
            importer.read_table(importer.template_xlsx(OPTS, lang), "t.xlsx"), OPTS)
        assert wines[0]["name"] == "Protos Roble" and wines[0]["price"] == 11.0 and not warnings and not ignored
        wines, _, _ = importer.rows_to_wines(importer.read_table(importer.template_csv(lang), "t.csv"), OPTS)
        assert wines[0]["origin"] == "Ribera del Duero" and wines[0]["alcohol"] == 14.0


def test_normalises_chatgpt_style_values():
    wines, warnings, _ = _wines(
        "Nombre;Uvas;Denominación de origen;Crianza;Tipo;Año;Alcohol;Precio (EUR);Puntuacion\n"
        "Viña Pomal;tempranillo y graciano;D.O.Ca. Rioja;reserva;red;2019;14,5%;15,90 €;4,0\n"
        "Douro Tinto;Touriga Nacional;Douro;;tinto;;13;8;\n")
    pomal, douro = wines
    assert pomal["grape"] == "Tempranillo, Graciano"
    assert (pomal["origin"], pomal["aging"], pomal["type"], pomal["year"]) == ("Rioja", "Reserva", "Tinto", "2019")
    assert (pomal["alcohol"], pomal["price"], pomal["rating"]) == (14.5, 15.9, 4.0)
    assert douro["origin"] == "Douro"  # not mangled by the "D.O." prefix stripper
    assert [w[0] for w in warnings] == ["origin"]


def test_markdown_table_and_problems_are_reported():
    wines, warnings, ignored = _wines(
        "```\n| Name | Grape | Aging | Price | Notes |\n|---|---|---|---|---|\n"
        "| A | Verdejo | Viejísimo | caro | x |\n| a | Verdejo | | | |\n|  | Godello | | | |\n```")
    assert [w["name"] for w in wines] == ["A"]
    assert wines[0]["aging"] == "" and wines[0]["price"] is None
    assert sorted(k for k, _, _ in warnings) == ["aging", "dup", "number"]
    assert ignored == ["Notes"]


def test_missing_name_column_and_bad_file():
    with pytest.raises(importer.ImportFailed, match="no_name_column"):
        _wines("Uva,Precio\nVerdejo,5\n")
    with pytest.raises(importer.ImportFailed):
        importer.read_table(b"not an excel file", "x.xlsx")


def test_excel_with_numeric_cells():
    buf = io.BytesIO()
    pd.DataFrame([{"Nombre": "Marqués de Riscal Reserva", "Añada": 2018, "Precio": 19.5, "Alcohol": 14}]).to_excel(
        buf, index=False)
    (w,), warnings, _ = importer.rows_to_wines(importer.read_table(buf.getvalue(), "v.xlsx"), OPTS)
    assert (w["year"], w["price"], w["alcohol"]) == ("2018", 19.5, 14.0) and not warnings
