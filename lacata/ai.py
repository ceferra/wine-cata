"""OpenAI helpers: fill wine data from a name or from a label photo.

Uses structured outputs (JSON schema), so the answer always parses. Price and rating
are estimates the model may invent: wines added this way are flagged for review.
"""

import base64
import json
from io import BytesIO

from .options import DEFAULT_AGINGS, WINE_TYPES

DEFAULT_MODEL = "gpt-4o"

LANG_NAMES = {"es": "Spanish", "en": "English", "va": "Valencian (Catalan)"}

SCHEMA = {
    "name": "wine",
    "strict": True,
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "found": {"type": "boolean", "description": "false if the wine cannot be identified"},
            "label_text": {"type": "string", "description": "wine name as read on the label, or empty"},
            "name": {"type": "string"},
            "winery": {"type": "string"},
            "grapes": {"type": "array", "items": {"type": "string"}},
            "type": {"type": "string", "enum": WINE_TYPES + [""]},
            "origin": {"type": "string", "description": "denominación de origen, e.g. Rioja"},
            "aging": {"type": "string", "enum": DEFAULT_AGINGS + [""]},
            "year": {"type": "string"},
            "alcohol": {"type": ["number", "null"]},
            "price": {"type": ["number", "null"], "description": "typical retail price in EUR"},
            "rating": {"type": ["number", "null"], "description": "average consumer rating 0-5, Vivino style"},
            "description": {"type": "string"},
        },
        "required": ["found", "label_text", "name", "winery", "grapes", "type", "origin", "aging", "year",
                     "alcohol", "price", "rating", "description"],
    },
}


class AIError(Exception):
    """`code` is an i18n key."""

    def __init__(self, code, detail=""):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


def _instructions(lang, options):
    return (
        "You are a sommelier assistant. Return data about the wine. "
        f"Prefer these exact spellings when they apply. Grapes: {', '.join(options['grapes'])}. "
        f"D.O.s: {', '.join(options['origins'])}. "
        "Use null for numbers you do not know and empty strings for unknown text. "
        "Do not invent a vintage. "
        f"Write the description (1-2 sentences) in {LANG_NAMES.get(lang, 'Spanish')}."
    )


def _call(api_key, model, content, lang, options):
    try:
        from openai import APIConnectionError, AuthenticationError, OpenAI, RateLimitError
    except ImportError:
        raise AIError("ai_error", "openai package not installed")
    client = OpenAI(api_key=api_key, timeout=60)
    try:
        resp = client.chat.completions.create(
            model=model or DEFAULT_MODEL,
            messages=[{"role": "system", "content": _instructions(lang, options)},
                      {"role": "user", "content": content}],
            response_format={"type": "json_schema", "json_schema": SCHEMA},
            temperature=0.2,
        )
    except AuthenticationError:
        raise AIError("ai_bad_key")
    except RateLimitError:
        raise AIError("ai_rate_limit")
    except APIConnectionError as e:
        raise AIError("ai_error", str(e))
    except Exception as e:
        raise AIError("ai_error", str(e))
    msg = resp.choices[0].message
    if getattr(msg, "refusal", None):
        raise AIError("ai_not_found")
    data = json.loads(msg.content)
    if not data.get("found") or not data.get("name"):
        raise AIError("ai_not_found")
    return _to_wine(data)


def _to_wine(d):
    name = d["name"].strip()
    winery = d.get("winery", "").strip()
    if winery and winery.lower() not in name.lower():
        name = f"{name} ({winery})"
    return {
        "name": name, "winery": winery, "grape": ", ".join(g.strip() for g in d["grapes"] if g.strip()),
        "grapes": [g.strip() for g in d["grapes"] if g.strip()],
        "type": d.get("type", ""), "origin": d.get("origin", "").strip(), "aging": d.get("aging", ""),
        "year": d.get("year", "").strip(), "alcohol": d.get("alcohol"), "price": d.get("price"),
        "rating": d.get("rating"), "description": d.get("description", "").strip(),
        "label_text": d.get("label_text", "").strip(),
    }


def search_wine(name, api_key, lang="es", options=None, model=None) -> dict:
    if not api_key:
        raise AIError("key_needed")
    if not (name or "").strip():
        raise AIError("name_required")
    from .options import default_options
    w = _call(api_key, model, f'Wine: "{name.strip()}"', lang, options or default_options())
    w["source"] = "ai"
    return w


def recognize_label(image_bytes, api_key, lang="es", options=None, model=None) -> dict:
    if not api_key:
        raise AIError("key_needed")
    from PIL import Image, ImageOps

    from .options import default_options
    try:
        img = ImageOps.exif_transpose(Image.open(BytesIO(image_bytes)))
    except Exception:
        raise AIError("bad_image")
    img.thumbnail((1600, 1600))
    if img.mode != "RGB":
        img = img.convert("RGB")
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=88)
    b64 = base64.b64encode(buf.getvalue()).decode()
    content = [
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}", "detail": "high"}},
        {"type": "text", "text": "Read this wine label (put what you read in label_text) and identify the wine."},
    ]
    w = _call(api_key, model, content, lang, options or default_options())
    w["source"] = "label"
    return w
