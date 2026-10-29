import pathlib
import re

from lacata.i18n import LANGS, T
from lacata.options import WINE_TYPES
from lacata.scoring import FIELDS

ROOT = pathlib.Path(__file__).resolve().parents[1]

# Keys built at runtime: t("score_" + f), t("type_" + x), t(cat + "_config"), t(e.code) for error codes.
DYNAMIC = ([f"score_{f}" for f, _ in FIELDS] + [f"type_{x}" for x in WINE_TYPES]
           + ["grapes_config", "origins_config", "agings_config"]
           + ["pin_too_short", "name_required", "name_taken", "not_found", "not_started", "already_revealed",
              "already_sent", "ai_bad_key", "ai_rate_limit", "ai_error", "ai_not_found", "key_needed", "bad_image"])


def test_every_key_used_exists_in_all_languages():
    used = set(DYNAMIC)
    for path in [ROOT / "app.py", *(ROOT / "lacata").rglob("*.py")]:
        used |= set(re.findall(r"""\bt\(\s*["']([a-z_0-9]+)["'](?!\s*\+)""", path.read_text()))
    missing = sorted(k for k in used if k not in T)
    assert not missing, missing
    for k, v in T.items():
        assert len(v) == len(LANGS) and all(v), k
