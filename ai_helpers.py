"""
OpenAI helpers — wine search + 2-step label recognition.
"""

import json, re, base64
from io import BytesIO


def openai_wine_search(wine_name: str, api_key: str) -> dict:
    if not api_key: return {"error": "API key no configurada."}
    if not wine_name.strip(): return {"error": "Escribe el nombre de un vino."}
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": (
                f'Datos del vino "{wine_name}". '
                'Devuelve SOLO JSON (sin markdown, sin backticks):\n'
                '{"name":"nombre completo","winery":"bodega",'
                '"grape":"variedad(es) separadas por coma (ej: Tempranillo, Garnacha)",'
                '"type":"Tinto/Blanco/Rosado/Espumoso/Dulce",'
                '"alcohol":"grado como número (ej: 14.5)",'
                '"origin":"denominación de origen (ej: Rioja)",'
                '"year":"año o vacío",'
                '"price":"precio medio euros número (ej: 12.50)",'
                '"rating":"puntuación 0-5 número (ej: 4.1) o vacío",'
                '"aging":"Joven/Crianza/Reserva/Gran Reserva",'
                '"description":"breve descripción español (1-2 frases)"}'
            )}],
            max_tokens=500, temperature=0.2,
        )
        text = resp.choices[0].message.content.strip()
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        return json.loads(text)
    except json.JSONDecodeError:
        return {"error": "Respuesta no válida de OpenAI. Inténtalo de nuevo."}
    except Exception as e:
        return _handle_openai_error(e)


def openai_label_recognize(image_bytes: bytes, api_key: str) -> dict:
    """Step 1: Vision reads wine name. Step 2: search fills data."""
    if not api_key: return {"error": "API key no configurada."}
    try:
        from openai import OpenAI
        from PIL import Image
        img = Image.open(BytesIO(image_bytes))
        if max(img.size) > 2048:
            r = 2048 / max(img.size)
            img = img.resize((int(img.size[0]*r), int(img.size[1]*r)), Image.LANCZOS)
        if img.mode in ("RGBA", "P"): img = img.convert("RGB")
        buf = BytesIO(); img.save(buf, format="JPEG", quality=92)
        b64 = base64.b64encode(buf.getvalue()).decode()

        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role":"user","content":[
                {"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}","detail":"high"}},
                {"type":"text","text":(
                    "Lee esta etiqueta de vino. Devuelve SOLO JSON:\n"
                    '{"wine_name":"nombre completo incluyendo bodega, año, clasificación y D.O. si se ven"}\n'
                    "Ejemplos:\n"
                    '{"wine_name":"Protos Reserva 2018 Ribera del Duero"}\n'
                    '{"wine_name":"Marqués de Riscal Reserva 2017 Rioja"}'
                )}
            ]}],
            max_tokens=150, temperature=0.1,
        )
        raw = resp.choices[0].message.content.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        wine_name = json.loads(raw).get("wine_name", "").strip()
        if not wine_name:
            return {"error": "No se pudo leer el nombre. Usa entrada manual."}

        result = openai_wine_search(wine_name, api_key)
        if result.get("error"): return result
        result["label_text"] = wine_name
        result["source"] = "label"
        return result
    except json.JSONDecodeError:
        return {"error": "No se pudo interpretar. Usa entrada manual."}
    except Exception as e:
        return _handle_openai_error(e)


def _handle_openai_error(e):
    err = str(e)
    if "api_key" in err.lower() or "401" in err: return {"error": "API key inválida."}
    if "429" in err: return {"error": "Rate limit. Espera un momento."}
    return {"error": f"Error OpenAI: {err}"}
