# 🍷 La Cata — cata de vinos a ciegas

Aplicación Streamlit para organizar catas a ciegas con puntuación automática, pensada para jugarse desde el móvil.

## Cómo funciona

1. El organizador entra en la web y crea una cata con un **PIN**. La app le da un **código de sala** (p. ej. `R8XCJ`).
2. Añade los vinos: desde la bodega, con IA (por nombre o foto de la etiqueta) o a mano.
3. Los participantes escanean el QR (o escriben el código) y se apuntan con su nombre. Cada uno recibe un **enlace personal**.
4. El organizador pulsa **Empezar** y, cuando todos han respondido, va **revelando** los vinos. Las pantallas se actualizan solas.

| URL | Quién |
|---|---|
| `/` | portada: unirse o crear una cata |
| `/?sala=CODIGO` | participante |
| `/?sala=CODIGO&org=1` | organizador (pide el PIN) |
| `/?sala=CODIGO&pantalla=1` | pantalla para proyectar: QR, progreso y clasificación, sin desvelar nada |

## Puntuación (100 puntos por vino)

| Campo | Máx. | Criterio |
|---|---|---|
| Uva | 25 | Uvas acertadas / todas las mencionadas (Jaccard): marcar todas no sirve |
| Origen | 25 | D.O. exacta 25 · otra D.O. de la misma región 10 |
| Crianza | 20 | Exacta 20 · contigua (Crianza↔Reserva) 8 |
| Puntuación | 10 | ±0,5 → 10 · ±1 → 5 |
| Alcohol | 10 | ±0,5 → 10 · ±1 → 6 · ±2 → 3 |
| Precio | 10 | ±max(3 €, 15 %) → 10 · ±max(6 €, 30 %) → 6 · ±max(12 €, 50 %) → 3 |

Los campos que el vino real no tiene no puntúan; los que el participante deja vacíos valen 0.
Además, cada uno puede decir **cuánto le gusta** cada vino (★, no puntúa). Al final salen el favorito,
el más difícil y el de mejor calidad-precio, y se pueden descargar los resultados en CSV.

## Catálogo de vinos habituales

La app incluye ~100 vinos españoles conocidos ([`lacata/data/vinos_comunes.csv`](lacata/data/vinos_comunes.csv)):
Rioja, Ribera, Rueda, Rías Baixas, Priorat, Cava, Jerez… Si la bodega está vacía al arrancar, se cargan solos;
si faltan algunos, la pestaña **📚 Bodega** ofrece un botón para añadirlos.

- Uva, D.O., crianza y tipo son la respuesta con la que se puntúa y están elegidos con cuidado.
- El precio y el alcohol son **aproximados** (varían por añada y tienda) y **no hay puntuación**: al añadir uno de
  estos vinos a una cata queda marcado como «datos sin comprobar» hasta que lo revisas con la botella delante.
- Al editar un vino del catálogo en la Bodega se da por comprobado.
- Para añadir o corregir vinos basta con editar el CSV.

## Uso local

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/streamlit run app.py --server.address 0.0.0.0
```

Los móviles de la misma red entran con el QR (usa la IP del ordenador). Los datos se guardan en `lacata.db` (SQLite).

## Despliegue en Streamlit Cloud

1. Sube el repositorio a GitHub y créalo en [share.streamlit.io](https://share.streamlit.io) con `app.py`.
2. En **Settings → Secrets** pega lo que necesites de [`.streamlit/secrets.toml.example`](.streamlit/secrets.toml.example):
   - `OPENAI_API_KEY`: activa la búsqueda con IA y la lectura de etiquetas.
   - `DATABASE_URL`: **muy recomendable**. Streamlit Cloud borra el disco en cada reinicio, así que sin una base de datos
     externa se pierden las catas y los vinos que hayas añadido (el catálogo sí vuelve solo). Ver abajo.
   - `APP_PASSWORD`: si la pones, hace falta para crear catas. Así nadie gasta tu API key de OpenAI.
   - `PUBLIC_URL`: solo si el QR sale con una dirección incorrecta.

### Que no se borren los datos (Postgres gratuito)

1. Crea una cuenta en [neon.tech](https://neon.tech) (o [supabase.com](https://supabase.com)) y un proyecto nuevo.
2. Copia la *connection string* (`postgresql://usuario:contraseña@host/basedatos?sslmode=require`).
   En Supabase usa la del *Session pooler*.
3. Pégala en Streamlit Cloud → **Settings → Secrets** como `DATABASE_URL = "postgresql://..."` y guarda.
   La app se reinicia, crea las tablas sola y carga el catálogo.

## Tests

```bash
.venv/bin/python -m pytest
```

## Estructura

```
app.py                  enrutado según la URL
lacata/db.py            almacenamiento (SQLAlchemy: SQLite o Postgres), transacciones atómicas
lacata/scoring.py       puntuación y clasificación (funciones puras)
lacata/ai.py            OpenAI con salida estructurada (JSON schema)
lacata/i18n.py          Castellano · English · Valencià
lacata/ui.py            CSS, tarjetas, QR, refresco automático, formulario de vino
lacata/views/           home, participant, organizer, screen
.streamlit/config.toml  tema claro forzado (evita el texto ilegible con el móvil en modo oscuro)
tests/                  pytest
```

Desarrollada por **César Ferri** con la ayuda de **Claude** (Anthropic).
