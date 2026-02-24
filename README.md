# 🍷 La Cata — App de Cata a Ciegas

## 🚀 Uso local

```bash
pip install -r requirements.txt
streamlit run app.py --server.address 0.0.0.0
```

- Organizador: `http://localhost:8501`
- Participantes: escanean el QR → `http://<tu-ip>:8501/?modo=participante`

## ☁️ Deploy en Streamlit Cloud

1. Sube este directorio a un repo de GitHub
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta tu repo → selecciona `app.py`
4. En **Settings > Secrets** añade:
   ```
   OPENAI_API_KEY = "sk-..."
   ```
5. Deploy → tu URL será `https://tu-app.streamlit.app`
6. Participantes: `https://tu-app.streamlit.app/?modo=participante`

## 📚 Base de datos de vinos

Los vinos se guardan automáticamente en una base de datos SQLite (`wines.db`).
- Al añadir un vino (por IA, foto o manual) se guarda en la BD
- En la siguiente cata, puedes cargarlos desde **📚 Bodega**
- Los vinos de la BD se pueden buscar, editar y eliminar

## 🌍 Idiomas

Castellano · English · Valencià — seleccionable en la sidebar del organizador.

## 📊 Puntuación (100 pts/vino)

| Campo | Máx | Criterio |
|-------|-----|----------|
| Uva | 25 | Multi-select. Todas=25, proporcional |
| Origen (D.O.) | 25 | Select. Exacto=25, parcial=10 |
| Crianza | 20 | Select. Exacto=20 |
| Puntuación | 10 | Número 0-5. ±0.5=10, ±1=5 |
| Alcohol | 10 | ±0.5%=10, ±1%=6, ±2%=3 |
| Precio | 10 | ±3€=10, ±6€=6, ±12€=3 |

## 📁 Archivos

```
app.py           → App Streamlit principal
state.py         → Estado de sesión (JSON file)
db.py            → Base de datos SQLite
ai_helpers.py    → OpenAI (búsqueda + etiqueta)
i18n.py          → Traducciones (ES/EN/VA)
.streamlit/      → Config tema Streamlit
```
