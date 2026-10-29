"""Bundled catalog of common Spanish wines (lacata/data/vinos_comunes.csv) to seed the cellar.

Grape, D.O., aging and type are the scored answers and were chosen with care; price and
alcohol are typical values and vary by vintage and shop, so catalog wines are flagged for
review when added to a tasting. No rating is included: there is no reliable source for it.
"""

import csv
import os

CATALOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "vinos_comunes.csv")


def load() -> list:
    with open(CATALOG_FILE, encoding="utf-8", newline="") as f:
        return [{**row, "source": "catalog"} for row in csv.DictReader(f)]
