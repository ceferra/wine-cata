"""Internationalization — Castellano, English, Valencià"""

LANGS = {"es": "Castellano", "en": "English", "va": "Valencià"}

T = {
    # ---- General ----
    "app_title": {"es": "🍷 La Cata", "en": "🍷 Wine Tasting", "va": "🍷 La Tast"},
    "organizer": {"es": "Organizador", "en": "Organizer", "va": "Organitzador"},
    "participant": {"es": "Participante", "en": "Participant", "va": "Participant"},
    "refresh": {"es": "🔄 Actualizar", "en": "🔄 Refresh", "va": "🔄 Actualitzar"},
    "language": {"es": "Idioma", "en": "Language", "va": "Idioma"},

    # ---- Sidebar ----
    "wines": {"es": "Vinos", "en": "Wines", "va": "Vins"},
    "participants_label": {"es": "Participantes", "en": "Participants", "va": "Participants"},
    "predictions": {"es": "Predicciones", "en": "Predictions", "va": "Prediccions"},
    "revealed_count": {"es": "Revelados", "en": "Revealed", "va": "Revelats"},
    "openai_key": {"es": "OpenAI API Key", "en": "OpenAI API Key", "va": "OpenAI API Key"},
    "key_ok": {"es": "✅ Configurada", "en": "✅ Configured", "va": "✅ Configurada"},
    "key_needed": {"es": "Necesaria para IA", "en": "Needed for AI", "va": "Necessària per a IA"},
    "reset_session": {"es": "🗑️ Reiniciar sesión", "en": "🗑️ Reset session", "va": "🗑️ Reiniciar sessió"},

    # ---- Tabs ----
    "tab_wines": {"es": "🍷 Vinos", "en": "🍷 Wines", "va": "🍷 Vins"},
    "tab_participants": {"es": "👥 Participantes", "en": "👥 Participants", "va": "👥 Participants"},
    "tab_control": {"es": "🎮 Control", "en": "🎮 Control", "va": "🎮 Control"},
    "tab_results": {"es": "🏆 Resultados", "en": "🏆 Results", "va": "🏆 Resultats"},
    "tab_options": {"es": "⚙️ Opciones", "en": "⚙️ Options", "va": "⚙️ Opcions"},

    # ---- Add wine ----
    "add_wine": {"es": "Añadir vino", "en": "Add wine", "va": "Afegir vi"},
    "method_ai": {"es": "🤖 Buscar con IA", "en": "🤖 AI Search", "va": "🤖 Cercar amb IA"},
    "method_photo": {"es": "📷 Foto etiqueta", "en": "📷 Label photo", "va": "📷 Foto etiqueta"},
    "method_manual": {"es": "✏️ Manual", "en": "✏️ Manual", "va": "✏️ Manual"},
    "search_placeholder": {"es": "Ej: Protos Reserva 2018", "en": "E.g.: Protos Reserva 2018", "va": "Ex: Protos Reserva 2018"},
    "ai_caption": {"es": "Escribe el nombre del vino y OpenAI rellenará los campos.", "en": "Type the wine name and OpenAI will fill the fields.", "va": "Escriu el nom del vi i OpenAI omplirà els camps."},
    "photo_caption": {"es": "Sube una foto → la IA lee el nombre → rellena los datos.", "en": "Upload a photo → AI reads the name → fills the data.", "va": "Puja una foto → la IA llig el nom → omple les dades."},
    "manual_caption": {"es": "ℹ️ Datos reales del vino — se usan para puntuar", "en": "ℹ️ Real wine data — used for scoring", "va": "ℹ️ Dades reals del vi — s'utilitzen per a puntuar"},
    "analyze_label": {"es": "🔬 Analizar etiqueta", "en": "🔬 Analyze label", "va": "🔬 Analitzar etiqueta"},
    "analyzing": {"es": "Leyendo nombre de la etiqueta...", "en": "Reading label name...", "va": "Llegint nom de l'etiqueta..."},
    "searching_ai": {"es": "Buscando con IA...", "en": "Searching with AI...", "va": "Cercant amb IA..."},
    "info_found": {"es": "✅ Información encontrada", "en": "✅ Information found", "va": "✅ Informació trobada"},
    "label_read": {"es": "🏷️ Nombre leído de la etiqueta", "en": "🏷️ Name read from label", "va": "🏷️ Nom llegit de l'etiqueta"},
    "add_this_wine": {"es": "✅ Añadir este vino", "en": "✅ Add this wine", "va": "✅ Afegir este vi"},
    "discard": {"es": "❌ Descartar", "en": "❌ Discard", "va": "❌ Descartar"},
    "add_wine_btn": {"es": "🍷 Añadir vino", "en": "🍷 Add wine", "va": "🍷 Afegir vi"},
    "name_required": {"es": "Nombre obligatorio", "en": "Name required", "va": "Nom obligatori"},
    "wines_added": {"es": "📋 Vinos añadidos", "en": "📋 Added wines", "va": "📋 Vins afegits"},
    "save": {"es": "💾 Guardar", "en": "💾 Save", "va": "💾 Guardar"},
    "delete": {"es": "🗑️ Eliminar", "en": "🗑️ Delete", "va": "🗑️ Eliminar"},

    # ---- Wine fields ----
    "f_name": {"es": "Nombre", "en": "Name", "va": "Nom"},
    "f_grape": {"es": "Uva", "en": "Grape", "va": "Raïm"},
    "f_origin": {"es": "Origen (D.O.)", "en": "Origin (D.O.)", "va": "Origen (D.O.)"},
    "f_aging": {"es": "Crianza", "en": "Aging", "va": "Criança"},
    "f_rating": {"es": "Puntuación (0-5)", "en": "Rating (0-5)", "va": "Puntuació (0-5)"},
    "f_alcohol": {"es": "Alcohol (%)", "en": "Alcohol (%)", "va": "Alcohol (%)"},
    "f_price": {"es": "Precio (€)", "en": "Price (€)", "va": "Preu (€)"},
    "f_type": {"es": "Tipo", "en": "Type", "va": "Tipus"},
    "f_year": {"es": "Año", "en": "Year", "va": "Any"},

    # ---- Participants ----
    "who_are_you": {"es": "👤 ¿Quién eres?", "en": "👤 Who are you?", "va": "👤 Qui eres?"},
    "change": {"es": "Cambiar", "en": "Change", "va": "Canviar"},
    "hello": {"es": "Hola", "en": "Hello", "va": "Hola"},
    "completed": {"es": "completados", "en": "completed", "va": "completats"},
    "sent": {"es": "enviado", "en": "sent", "va": "enviat"},
    "prediction_sent": {"es": "✅ Predicción enviada", "en": "✅ Prediction sent", "va": "✅ Predicció enviada"},
    "fill_prediction": {"es": "📝 Rellenar predicción", "en": "📝 Fill prediction", "va": "📝 Omplir predicció"},
    "send_prediction": {"es": "📤 Enviar predicción", "en": "📤 Send prediction", "va": "📤 Enviar predicció"},
    "already_sent": {"es": "Ya has enviado para este vino.", "en": "Already sent for this wine.", "va": "Ja has enviat per a este vi."},
    "sent_ok": {"es": "✅ ¡Enviado!", "en": "✅ Sent!", "va": "✅ Enviat!"},
    "participant_name": {"es": "Nombre del participante...", "en": "Participant name...", "va": "Nom del participant..."},
    "add_participant": {"es": "➕ Añadir", "en": "➕ Add", "va": "➕ Afegir"},
    "already_exists": {"es": "Ya existe", "en": "Already exists", "va": "Ja existeix"},

    # ---- Control ----
    "start_tasting": {"es": "🚀 Iniciar la cata", "en": "🚀 Start tasting", "va": "🚀 Iniciar la tast"},
    "start_btn": {"es": "🚀 ¡Comenzar!", "en": "🚀 Start!", "va": "🚀 Començar!"},
    "add_wines_participants": {"es": "Añade vinos y participantes primero.", "en": "Add wines and participants first.", "va": "Afig vins i participants primer."},
    "qr_title": {"es": "📱 QR para participantes", "en": "📱 QR for participants", "va": "📱 QR per a participants"},
    "qr_instructions": {"es": "Los participantes escanean → eligen nombre → rellenan", "en": "Participants scan → choose name → fill in", "va": "Els participants escanegen → trien nom → omplin"},
    "reveal_wines": {"es": "🎭 Revelar vinos", "en": "🎭 Reveal wines", "va": "🎭 Revelar vins"},
    "reveal": {"es": "Revelar", "en": "Reveal", "va": "Revelar"},
    "not_started": {"es": "⏳ La cata aún no ha comenzado.", "en": "⏳ Tasting hasn't started yet.", "va": "⏳ La tast encara no ha començat."},
    "wait_organizer": {"es": "Espera al organizador.", "en": "Wait for the organizer.", "va": "Espera a l'organitzador."},
    "partial_ranking": {"es": "📊 Clasificación parcial", "en": "📊 Partial ranking", "va": "📊 Classificació parcial"},
    "pts_per_wine": {"es": "Puntos por vino", "en": "Points per wine", "va": "Punts per vi"},

    # ---- Results ----
    "ranking": {"es": "🏆 Clasificación", "en": "🏆 Ranking", "va": "🏆 Classificació"},
    "no_revealed": {"es": "Aún no se han revelado vinos.", "en": "No wines revealed yet.", "va": "Encara no s'han revelat vins."},
    "detail": {"es": "📊 Detalle", "en": "📊 Detail", "va": "📊 Detall"},
    "total": {"es": "TOTAL", "en": "TOTAL", "va": "TOTAL"},
    "of": {"es": "de", "en": "of", "va": "de"},
    "you": {"es": "(tú)", "en": "(you)", "va": "(tu)"},
    "wines_revealed": {"es": "vinos revelados", "en": "wines revealed", "va": "vins revelats"},

    # ---- Options tab ----
    "config_options": {"es": "⚙️ Opciones de categorías", "en": "⚙️ Category options", "va": "⚙️ Opcions de categories"},
    "grapes_config": {"es": "🍇 Variedades de uva", "en": "🍇 Grape varieties", "va": "🍇 Varietats de raïm"},
    "origins_config": {"es": "📍 Denominaciones de origen", "en": "📍 Denominations of origin", "va": "📍 Denominacions d'origen"},
    "aging_config": {"es": "🏷️ Tipos de crianza", "en": "🏷️ Aging types", "va": "🏷️ Tipus de criança"},
    "add_option": {"es": "Añadir", "en": "Add", "va": "Afegir"},
    "new_option_placeholder": {"es": "Nueva opción...", "en": "New option...", "va": "Nova opció..."},
    "saved": {"es": "Guardado", "en": "Saved", "va": "Guardat"},

    # ---- Scoring ----
    "score_grape": {"es": "Uva", "en": "Grape", "va": "Raïm"},
    "score_origin": {"es": "Origen", "en": "Origin", "va": "Origen"},
    "score_aging": {"es": "Crianza", "en": "Aging", "va": "Criança"},
    "score_rating": {"es": "Puntuación", "en": "Rating", "va": "Puntuació"},
    "score_alcohol": {"es": "Alcohol", "en": "Alcohol", "va": "Alcohol"},
    "score_price": {"es": "Precio", "en": "Price", "va": "Preu"},

    # Footer
    "footer": {"es": "La Cata · El arte de descubrir el vino 🍷", "en": "Wine Tasting · The art of discovering wine 🍷", "va": "La Tast · L'art de descobrir el vi 🍷"},

    # Select
    "select_grape": {"es": "Selecciona uva(s)...", "en": "Select grape(s)...", "va": "Selecciona raïm(s)..."},
    "select_origin": {"es": "Selecciona D.O.", "en": "Select D.O.", "va": "Selecciona D.O."},
    "select_aging": {"es": "Selecciona crianza", "en": "Select aging", "va": "Selecciona criança"},

    # Database
    "method_db": {"es": "📚 Base de datos", "en": "📚 Database", "va": "📚 Base de dades"},
    "db_caption": {"es": "Selecciona vinos guardados de catas anteriores.", "en": "Select saved wines from previous tastings.", "va": "Selecciona vins guardats de tasts anteriors."},
    "db_search": {"es": "Buscar en base de datos...", "en": "Search database...", "va": "Cercar en base de dades..."},
    "db_add_to_tasting": {"es": "➕ Añadir a la cata", "en": "➕ Add to tasting", "va": "➕ Afegir a la tast"},
    "db_wine_count": {"es": "vinos en base de datos", "en": "wines in database", "va": "vins en base de dades"},
    "db_no_results": {"es": "No se encontraron vinos.", "en": "No wines found.", "va": "No s'han trobat vins."},
    "db_empty": {"es": "La base de datos está vacía. Añade vinos por IA, foto o manual y se guardarán automáticamente.", "en": "Database is empty. Add wines via AI, photo or manual and they'll be saved automatically.", "va": "La base de dades està buida. Afig vins per IA, foto o manual i es guardaran automàticament."},
    "save_to_db": {"es": "💾 Guardar en BD", "en": "💾 Save to DB", "va": "💾 Guardar en BD"},
    "saved_to_db": {"es": "✅ Guardado en la base de datos", "en": "✅ Saved to database", "va": "✅ Guardat en la base de dades"},
    "db_delete": {"es": "Eliminar de BD", "en": "Delete from DB", "va": "Eliminar de BD"},
    "tab_db": {"es": "📚 Bodega", "en": "📚 Cellar", "va": "📚 Celler"},
    "db_title": {"es": "📚 Bodega de vinos", "en": "📚 Wine cellar", "va": "📚 Celler de vins"},
    "db_all_wines": {"es": "Todos los vinos guardados", "en": "All saved wines", "va": "Tots els vins guardats"},

    # Description / Comments
    "f_description": {"es": "Comentarios", "en": "Comments", "va": "Comentaris"},
    "f_description_placeholder": {"es": "Notas, maridaje, impresiones...", "en": "Notes, pairing, impressions...", "va": "Notes, maridatge, impressions..."},

    # About
    "tab_about": {"es": "ℹ️ About", "en": "ℹ️ About", "va": "ℹ️ About"},
}


def t(key: str, lang: str) -> str:
    entry = T.get(key, {})
    return entry.get(lang, entry.get("es", key))
