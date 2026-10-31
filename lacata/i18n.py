"""Translations: Castellano, English, Valencià."""

LANGS = {"es": "Castellano", "en": "English", "va": "Valencià"}

T = {
    # ---- General
    "app_title": ("La Cata", "Blind Tasting", "El Tast"),
    "tagline": ("Cata de vinos a ciegas", "Blind wine tasting", "Tast de vins a cegues"),
    "organizer": ("Organizador", "Organizer", "Organitzador"),
    "participant": ("Participante", "Participant", "Participant"),
    "participants_label": ("Participantes", "Participants", "Participants"),
    "language": ("Idioma", "Language", "Idioma"),
    "wine": ("Vino", "Wine", "Vi"),
    "wines": ("Vinos", "Wines", "Vins"),
    "predictions": ("Predicciones", "Guesses", "Prediccions"),
    "code": ("Código", "Code", "Codi"),
    "save": ("Guardar", "Save", "Guardar"),
    "saved": ("Guardado.", "Saved.", "Guardat."),
    "edit": ("Editar", "Edit", "Editar"),
    "delete": ("Borrar", "Delete", "Esborrar"),
    "discard": ("Descartar", "Discard", "Descartar"),
    "actions": ("Opciones", "Options", "Opcions"),
    "yes_do_it": ("Sí, hazlo", "Yes, do it", "Sí, fes-ho"),
    "choose": ("Elige…", "Choose…", "Tria…"),
    "choose_or_type": ("Elige o escribe…", "Choose or type…", "Tria o escriu…"),
    "settings": ("⚙️ Ajustes", "⚙️ Settings", "⚙️ Ajustos"),
    "you": ("tú", "you", "tu"),
    "of": ("de", "of", "de"),
    "total": ("Total", "Total", "Total"),
    "footer": ("El arte de descubrir el vino", "The art of discovering wine", "L'art de descobrir el vi"),

    # ---- Home
    "join_title": ("Unirse a una cata", "Join a tasting", "Unir-se a un tast"),
    "join_btn": ("Entrar", "Join", "Entrar"),
    "organize_title": ("Organizar", "Organize", "Organitzar"),
    "new_tasting": ("Nueva cata", "New tasting", "Nou tast"),
    "manage_tasting": ("Ya tengo una", "I have one", "Ja en tinc un"),
    "tasting_name": ("Nombre de la cata", "Tasting name", "Nom del tast"),
    "tasting_name_placeholder": ("Cata de otoño", "Autumn tasting", "Tast de tardor"),
    "choose_pin": ("PIN de organizador", "Organizer PIN", "PIN d'organitzador"),
    "pin_help": ("Mínimo 4 caracteres. Lo necesitarás para volver a entrar como organizador.",
                 "At least 4 characters. You will need it to log back in as organizer.",
                 "Mínim 4 caràcters. El necessitaràs per a tornar a entrar com a organitzador."),
    "pin": ("PIN", "PIN", "PIN"),
    "app_password": ("Contraseña de la app", "App password", "Contrasenya de l'app"),
    "wrong_app_password": ("Contraseña de la app incorrecta.", "Wrong app password.", "Contrasenya de l'app incorrecta."),
    "create_btn": ("Crear cata", "Create tasting", "Crear tast"),
    "enter": ("Entrar", "Log in", "Entrar"),
    "wrong_pin": ("Código o PIN incorrecto.", "Wrong code or PIN.", "Codi o PIN incorrecte."),
    "tasting_not_found": ("No existe ninguna cata con ese código.", "No tasting with that code.",
                          "No hi ha cap tast amb eixe codi."),
    "pin_too_short": ("El PIN debe tener al menos 4 caracteres.", "The PIN must have at least 4 characters.",
                      "El PIN ha de tindre almenys 4 caràcters."),
    "go_participant": ("Soy participante", "I'm a participant", "Sóc participant"),

    # ---- Participant
    "who_are_you": ("¿Cómo te llamas?", "What's your name?", "Com et dius?"),
    "your_name": ("Tu nombre", "Your name", "El teu nom"),
    "your_name_placeholder": ("Ana", "Anna", "Anna"),
    "join_hint": ("Si ya te habías unido desde este móvil y perdiste la página, pide tu enlace personal al organizador.",
                  "If you already joined and lost the page, ask the organizer for your personal link.",
                  "Si ja t'havies unit i has perdut la pàgina, demana el teu enllaç personal a l'organitzador."),
    "name_required": ("Escribe un nombre.", "Enter a name.", "Escriu un nom."),
    "name_taken": ("Ese nombre ya está en la cata. Usa otro, o pide tu enlace al organizador si eres tú.",
                   "That name is already taken. Pick another, or ask the organizer for your link if it's you.",
                   "Eixe nom ja està en el tast. Usa'n un altre, o demana el teu enllaç a l'organitzador si eres tu."),
    "hello": ("Hola", "Hi", "Hola"),
    "not_started": ("La cata aún no ha empezado. Esta página se actualizará sola.",
                    "The tasting hasn't started yet. This page will update by itself.",
                    "El tast encara no ha començat. Esta pàgina s'actualitzarà sola."),
    "no_wines_yet": ("Aún no hay vinos.", "No wines yet.", "Encara no hi ha vins."),
    "completed": ("enviadas", "sent", "enviades"),
    "pending": ("pendiente", "to do", "pendent"),
    "sent": ("enviado", "sent", "enviat"),
    "revealed": ("revelado", "revealed", "revelat"),
    "send_prediction": ("Enviar predicción", "Send guess", "Enviar predicció"),
    "fill_something": ("Rellena al menos un campo.", "Fill in at least one field.", "Ompli almenys un camp."),
    "sent_ok": ("¡Predicción enviada!", "Guess sent!", "Predicció enviada!"),
    "prediction_sent": ("Predicción enviada. Espera a que el organizador revele el vino.",
                        "Guess sent. Wait for the organizer to reveal the wine.",
                        "Predicció enviada. Espera que l'organitzador revele el vi."),
    "cancel_prediction": ("Cambiar mi predicción", "Change my guess", "Canviar la meua predicció"),
    "cancel_confirm_q": ("Se borrará tu predicción para que puedas enviar otra.",
                         "Your guess will be deleted so you can send a new one.",
                         "S'esborrarà la teua predicció perquè en pugues enviar una altra."),
    "cancel_done": ("Predicción borrada. Ya puedes enviar otra.", "Guess deleted. You can send a new one.",
                    "Predicció esborrada. Ja pots enviar-ne una altra."),
    "already_sent": ("Ya habías enviado una predicción para este vino.", "You already sent a guess for this wine.",
                     "Ja havies enviat una predicció per a este vi."),
    "already_revealed": ("Este vino ya está revelado.", "This wine has already been revealed.",
                         "Este vi ja està revelat."),
    "not_found": ("No encontrado.", "Not found.", "No trobat."),
    "no_guess_sent": ("No enviaste predicción para este vino.", "You didn't send a guess for this wine.",
                      "No vas enviar predicció per a este vi."),
    "best_on_wine": ("¡Mejor puntuación en este vino!", "Top score on this wine!", "Millor puntuació en este vi!"),
    "liking_q": ("¿Cuánto te gusta?", "How much do you like it?", "Quant t'agrada?"),
    "liking_hint": ("no puntúa", "not scored", "no puntua"),
    "yours": ("Tú", "You", "Tu"),
    "real": ("Real", "Actual", "Real"),
    "personal_link_hint": ("Tu enlace personal (guárdalo para volver a entrar):",
                           "Your personal link (keep it to get back in):",
                           "El teu enllaç personal (guarda'l per a tornar a entrar):"),
    "partial_ranking": ("Clasificación", "Standings", "Classificació"),
    "final_ranking": ("Clasificación final", "Final standings", "Classificació final"),

    # ---- Organizer: tabs
    "tab_wines": ("🍷 Vinos", "🍷 Wines", "🍷 Vins"),
    "tab_room": ("🎮 Sala", "🎮 Room", "🎮 Sala"),
    "tab_results": ("🏆 Resultados", "🏆 Results", "🏆 Resultats"),
    "tab_db": ("📚 Bodega", "📚 Cellar", "📚 Celler"),
    "tab_settings": ("⚙️ Ajustes", "⚙️ Settings", "⚙️ Ajustos"),
    "tab_about": ("Acerca de", "About", "Quant a"),

    # ---- Organizer: wines
    "add_wine": ("Añadir vino", "Add wine", "Afegir vi"),
    "method_db": ("📚 Bodega", "📚 Cellar", "📚 Celler"),
    "method_ai": ("🤖 IA", "🤖 AI", "🤖 IA"),
    "method_photo": ("📷 Foto", "📷 Photo", "📷 Foto"),
    "missing_people": ("Faltan", "Waiting for", "Falten"),
    "method_file": ("📄 Excel", "📄 Excel", "📄 Excel"),
    "import_steps": ("1) Descarga la plantilla. 2) Pásasela a ChatGPT con el texto de abajo y la lista de vinos. "
                     "3) Sube aquí el Excel o CSV que te devuelva, o pega la tabla.",
                     "1) Download the template. 2) Give it to ChatGPT with the text below and your list of wines. "
                     "3) Upload the Excel or CSV it returns, or paste the table.",
                     "1) Descarrega la plantilla. 2) Passa-la a ChatGPT amb el text de baix i la llista de vins. "
                     "3) Puja ací l'Excel o CSV que et retorne, o apega la taula."),
    "template_xlsx": ("Plantilla Excel", "Excel template", "Plantilla Excel"),
    "template_csv": ("Plantilla CSV", "CSV template", "Plantilla CSV"),
    "chatgpt_prompt": ("Texto para ChatGPT", "Text for ChatGPT", "Text per a ChatGPT"),
    "chatgpt_prompt_hint": ("Cópialo (botón de la esquina), añade al final los vinos de tu cata y adjunta la "
                            "plantilla.",
                            "Copy it (corner button), add your tasting's wines at the end and attach the template.",
                            "Copia'l (botó de la cantonada), afig al final els vins del teu tast i adjunta la "
                            "plantilla."),
    "import_upload": ("Sube el Excel o CSV", "Upload the Excel or CSV", "Puja l'Excel o CSV"),
    "import_paste": ("…o pega aquí la tabla", "…or paste the table here", "…o apega ací la taula"),
    "import_paste_placeholder": ("Nombre;Uva;D.O.;Crianza;…", "Name,Grape,Region,Aging,…",
                                 "Nom;Raïm;D.O.;Criança;…"),
    "import_no_name": ("No encuentro la columna «Nombre». Usa la plantilla.",
                       "There is no 'Name' column. Use the template.",
                       "No trobe la columna «Nom». Usa la plantilla."),
    "import_bad_file": ("No se ha podido leer el archivo", "The file could not be read",
                        "No s'ha pogut llegir el fitxer"),
    "import_already": ("{n} vinos ya están en la cata y se omiten.", "{n} wines are already in the tasting and are "
                       "skipped.", "{n} vins ja estan en el tast i s'ometen."),
    "import_nothing": ("No hay vinos nuevos que añadir.", "No new wines to add.", "No hi ha vins nous per afegir."),
    "import_ignored_cols": ("Columnas que no se usan", "Unused columns", "Columnes que no s'usen"),
    "import_warnings": ("Revisa", "Check", "Revisa"),
    "import_row": ("Fila", "Row", "Fila"),
    "import_w_dup": ("nombre repetido, se omite", "duplicate name, skipped", "nom repetit, s'omet"),
    "import_w_origin": ("D.O. sin región conocida (no dará puntos parciales):",
                        "region not in the list (no partial points):", "D.O. sense regió coneguda (no donarà "
                        "punts parcials):"),
    "import_w_aging": ("crianza no reconocida, se deja vacía:", "unknown aging, left empty:",
                       "criança no reconeguda, es deixa buida:"),
    "import_w_type": ("tipo no reconocido, se deja vacío:", "unknown type, left empty:",
                      "tipus no reconegut, es deixa buit:"),
    "import_w_number": ("número no válido, se deja vacío:", "invalid number, left empty:",
                        "número no vàlid, es deixa buit:"),
    "import_add": ("Añadir {n} vinos a la cata", "Add {n} wines to the tasting", "Afegir {n} vins al tast"),
    "import_done": ("{n} vinos añadidos.", "{n} wines added.", "{n} vins afegits."),
    "method_manual": ("✍️ Manual", "✍️ Manual", "✍️ Manual"),
    "started_edit_warning": ("La cata ya ha empezado: si cambias los datos de un vino cambian las puntuaciones.",
                             "The tasting has started: changing a wine's data changes the scores.",
                             "El tast ja ha començat: si canvies les dades d'un vi canvien les puntuacions."),
    "db_search": ("Buscar por nombre, uva, D.O. o bodega…", "Search by name, grape, region or winery…",
                  "Cercar per nom, raïm, D.O. o celler…"),
    "db_empty": ("La bodega está vacía. Los vinos que añadas se guardarán aquí.",
                 "The cellar is empty. Wines you add will be saved here.",
                 "El celler està buit. Els vins que afegisques es guardaran ací."),
    "db_no_results": ("Sin resultados.", "No results.", "Sense resultats."),
    "db_add_to_tasting": ("➕ Añadir a la cata", "➕ Add to tasting", "➕ Afegir al tast"),
    "search": ("Buscar", "Search", "Cercar"),
    "search_placeholder": ("Ej.: Protos Reserva 2018", "e.g. Protos Reserva 2018", "Ex.: Protos Reserva 2018"),
    "searching_ai": ("Buscando…", "Searching…", "Cercant…"),
    "photo_caption": ("Haz o sube una foto de la etiqueta", "Take or upload a photo of the label",
                      "Fes o puja una foto de l'etiqueta"),
    "analyze_label": ("Analizar etiqueta", "Analyse label", "Analitzar etiqueta"),
    "analyzing": ("Leyendo la etiqueta…", "Reading the label…", "Llegint l'etiqueta…"),
    "info_found": ("Datos encontrados. Revísalos antes de añadir el vino.",
                   "Data found. Check it before adding the wine.",
                   "Dades trobades. Revisa-les abans d'afegir el vi."),
    "label_read": ("Etiqueta leída", "Label read", "Etiqueta llegida"),
    "add_this_wine": ("Añadir este vino", "Add this wine", "Afegir este vi"),
    "add_wine_btn": ("Añadir vino", "Add wine", "Afegir vi"),
    "also_cellar": ("Guardar también en la bodega", "Also save to the cellar", "Guardar també al celler"),
    "also_update_cellar": ("Actualizar también en la bodega", "Also update in the cellar",
                           "Actualitzar també al celler"),
    "ai_review_warning": ("El precio, la puntuación y el alcohol son estimaciones (de la IA o del catálogo) y pueden "
                          "no ser exactos. Compruébalos en la botella: son la respuesta con la que se puntúa.",
                          "Price, rating and alcohol are estimates (from the AI or the catalog) and may be wrong. "
                          "Check them on the bottle: they are the answer people are scored against.",
                          "El preu, la puntuació i l'alcohol són estimacions (de la IA o del catàleg) i poden no "
                          "ser exactes. Comprova'ls en la botella: són la resposta amb què es puntua."),
    "verified_check": ("He comprobado los datos", "I have checked the data", "He comprovat les dades"),
    "needs_review": ("datos sin comprobar", "data not checked", "dades sense comprovar"),
    "wine_added": ("Vino añadido.", "Wine added.", "Vi afegit."),
    "options_added": ("Nuevas opciones añadidas", "New options added", "Noves opcions afegides"),
    "wines_added": ("Vinos de esta cata", "Wines in this tasting", "Vins d'este tast"),
    "delete_wine_q": ("¿Borrar este vino de la cata?", "Remove this wine from the tasting?",
                      "Esborrar este vi del tast?"),
    "delete_wine_guesses": ("Se perderán {n} predicciones.", "{n} guesses will be lost.",
                            "Es perdran {n} prediccions."),
    "key_needed_settings": ("Falta la API key de OpenAI: añádela en ⚙️ Ajustes o en los Secrets de la app.",
                            "OpenAI API key missing: add it in ⚙️ Settings or in the app Secrets.",
                            "Falta l'API key d'OpenAI: afig-la en ⚙️ Ajustos o en els Secrets de l'app."),
    "key_needed": ("Falta la API key de OpenAI.", "OpenAI API key missing.", "Falta l'API key d'OpenAI."),
    "ai_bad_key": ("La API key de OpenAI no es válida.", "Invalid OpenAI API key.", "L'API key d'OpenAI no és vàlida."),
    "ai_rate_limit": ("OpenAI está limitando las peticiones. Espera un momento.",
                      "OpenAI rate limit reached. Wait a moment.",
                      "OpenAI està limitant les peticions. Espera un moment."),
    "ai_error": ("Error al consultar OpenAI.", "Error calling OpenAI.", "Error en consultar OpenAI."),
    "ai_not_found": ("La IA no ha identificado el vino. Prueba con otro nombre o usa la entrada manual.",
                     "The AI couldn't identify the wine. Try another name or add it manually.",
                     "La IA no ha identificat el vi. Prova amb un altre nom o usa l'entrada manual."),
    "bad_image": ("No se puede leer la imagen.", "Cannot read the image.", "No es pot llegir la imatge."),

    # ---- Wine form
    "f_name": ("Nombre del vino", "Wine name", "Nom del vi"),
    "f_grape": ("Uva(s)", "Grape(s)", "Raïm(s)"),
    "f_origin": ("Origen (D.O.)", "Region (D.O.)", "Origen (D.O.)"),
    "f_aging": ("Crianza", "Aging", "Criança"),
    "f_rating": ("Puntuación (0-5)", "Rating (0-5)", "Puntuació (0-5)"),
    "f_alcohol": ("Alcohol (%)", "Alcohol (%)", "Alcohol (%)"),
    "f_price": ("Precio (€)", "Price (€)", "Preu (€)"),
    "f_type": ("Tipo", "Type", "Tipus"),
    "f_year": ("Añada", "Vintage", "Anyada"),
    "f_description": ("Notas", "Notes", "Notes"),
    "f_description_placeholder": ("Notas de cata, maridaje…", "Tasting notes, pairing…", "Notes de tast, maridatge…"),
    "type_Tinto": ("Tinto", "Red", "Negre"),
    "type_Blanco": ("Blanco", "White", "Blanc"),
    "type_Rosado": ("Rosado", "Rosé", "Rosat"),
    "type_Espumoso": ("Espumoso", "Sparkling", "Escumós"),
    "type_Dulce": ("Dulce", "Sweet", "Dolç"),
    "type_Generoso": ("Generoso", "Fortified", "Generós"),
    "score_grape": ("Uva", "Grape", "Raïm"),
    "score_origin": ("Origen", "Region", "Origen"),
    "score_aging": ("Crianza", "Aging", "Criança"),
    "score_rating": ("Puntuación", "Rating", "Puntuació"),
    "score_alcohol": ("Alcohol", "Alcohol", "Alcohol"),
    "score_price": ("Precio", "Price", "Preu"),

    # ---- Organizer: room
    "qr_title": ("Escanea para jugar", "Scan to play", "Escaneja per a jugar"),
    "qr_instructions": ("Escanea el QR con la cámara del móvil o entra en la web y escribe el código.",
                        "Scan the QR with your phone camera, or open the website and type the code.",
                        "Escaneja el QR amb la càmera del mòbil o entra en la web i escriu el codi."),
    "open_screen": ("Abrir pantalla para proyectar", "Open screen for the projector", "Obrir pantalla per a projectar"),
    "screen_hint": ("Muestra el QR y la clasificación sin enseñar los vinos ocultos. Úsala en la tele en vez de "
                    "esta página.",
                    "Shows the QR and the standings without the hidden wines. Put it on the TV instead of this page.",
                    "Mostra el QR i la classificació sense ensenyar els vins ocults. Usa-la en la tele en lloc "
                    "d'esta pàgina."),
    "start_tasting": ("Empezar la cata", "Start the tasting", "Començar el tast"),
    "start_btn": ("Empezar", "Start", "Començar"),
    "add_wines_first": ("Añade al menos un vino para empezar.", "Add at least one wine to start.",
                        "Afig almenys un vi per a començar."),
    "unreviewed_warning": ("Vinos con datos sin comprobar: {wines}.", "Wines with unchecked data: {wines}.",
                           "Vins amb dades sense comprovar: {wines}."),
    "no_participants": ("Aún no se ha unido nadie.", "Nobody has joined yet.", "Encara no s'ha unit ningú."),
    "personal_link_org": ("Enlace personal (por si pierde la página):", "Personal link (in case they lose the page):",
                          "Enllaç personal (per si perd la pàgina):"),
    "admin_cancel": ("Borrar predicción", "Delete guess", "Esborrar predicció"),
    "remove_participant": ("Expulsar de la cata", "Remove from tasting", "Expulsar del tast"),
    "reveal_wines": ("Revelar vinos", "Reveal wines", "Revelar vins"),
    "reveal": ("Revelar", "Reveal", "Revelar"),
    "reveal_anyway_q": ("Faltan {n} por responder. Si lo revelas ya no podrán enviar su predicción.",
                        "{n} still haven't answered. Once revealed they can't send their guess.",
                        "Falten {n} per respondre. Si el reveles ja no podran enviar la predicció."),
    "reveal_anyway": ("Revelar igualmente", "Reveal anyway", "Revelar igualment"),
    "waiting_room": ("En la sala", "In the room", "A la sala"),
    "progress": ("Progreso", "Progress", "Progrés"),

    # ---- Results
    "no_revealed": ("Aún no se ha revelado ningún vino.", "No wine has been revealed yet.",
                    "Encara no s'ha revelat cap vi."),
    "ranking": ("Clasificación", "Standings", "Classificació"),
    "detail": ("Detalle por vino", "Detail per wine", "Detall per vi"),
    "no_guesses": ("Sin predicciones.", "No guesses.", "Sense prediccions."),
    "highlights": ("Lo más destacado", "Highlights", "El més destacat"),
    "crowd_favourite": ("Favorito", "Favourite", "Favorit"),
    "hardest": ("Más difícil", "Hardest", "Més difícil"),
    "best_value": ("Mejor calidad-precio", "Best value", "Millor qualitat-preu"),
    "export_csv": ("Descargar resultados (CSV)", "Download results (CSV)", "Descarregar resultats (CSV)"),

    # ---- Cellar
    "db_title": ("Bodega", "Cellar", "Celler"),
    "db_wine_count": ("vinos", "wines", "vins"),
    "load_catalog": ("Cargar {n} vinos españoles habituales", "Load {n} common Spanish wines",
                     "Carregar {n} vins espanyols habituals"),
    "load_catalog_help": ("Catálogo incluido en la app: uva, D.O., crianza y tipo. El precio y el alcohol son "
                          "aproximados y no incluye puntuación.",
                          "Catalog bundled with the app: grape, region, aging and type. Price and alcohol are "
                          "approximate and there is no rating.",
                          "Catàleg inclòs en l'app: raïm, D.O., criança i tipus. El preu i l'alcohol són "
                          "aproximats i no inclou puntuació."),
    "catalog_loaded": ("{n} vinos añadidos a la bodega.", "{n} wines added to the cellar.",
                       "{n} vins afegits al celler."),
    "catalog_wine": ("Del catálogo: precio y alcohol aproximados", "From the catalog: approximate price and alcohol",
                     "Del catàleg: preu i alcohol aproximats"),
    "db_delete_q": ("Se borrará de la bodega (no de las catas).", "It will be removed from the cellar (not from tastings).",
                    "S'esborrarà del celler (no dels tasts)."),

    # ---- Settings
    "general": ("General", "General", "General"),
    "tasting_language": ("Idioma de la cata", "Tasting language", "Idioma del tast"),
    "tasting_language_help": ("Idioma por defecto para todos. Cada participante puede cambiarlo en su móvil.",
                              "Default language for everyone. Each participant can change it on their phone.",
                              "Idioma per defecte per a tots. Cada participant pot canviar-lo en el seu mòbil."),
    "openai_key": ("API key de OpenAI", "OpenAI API key", "API key d'OpenAI"),
    "key_from_secrets": ("Configurada en los Secrets de la app.", "Configured in the app Secrets.",
                         "Configurada en els Secrets de l'app."),
    "key_session_help": ("Solo se guarda en esta sesión del navegador.", "Only kept in this browser session.",
                         "Només es guarda en esta sessió del navegador."),
    "config_options": ("Opciones de respuesta", "Answer options", "Opcions de resposta"),
    "options_help": ("Una opción por línea. Las uvas y D.O.s de los vinos que añadas se incorporan solas.",
                     "One option per line. Grapes and regions of wines you add are included automatically.",
                     "Una opció per línia. Els raïms i D.O. dels vins que afegisques s'incorporen sols."),
    "grapes_config": ("Uvas", "Grapes", "Raïms"),
    "origins_config": ("Denominaciones de origen", "Regions (D.O.)", "Denominacions d'origen"),
    "agings_config": ("Crianzas (de más joven a más vieja)", "Agings (youngest to oldest)",
                      "Criances (de més jove a més vella)"),
    "session": ("Sesión", "Session", "Sessió"),
    "logout": ("Salir del modo organizador", "Log out of organizer mode", "Eixir del mode organitzador"),
    "delete_tasting": ("Borrar esta cata", "Delete this tasting", "Esborrar este tast"),
    "delete_tasting_q": ("Se borrarán la cata, sus participantes y predicciones. La bodega no se toca.",
                         "The tasting, its participants and guesses will be deleted. The cellar is kept.",
                         "S'esborraran el tast, els participants i les prediccions. El celler no es toca."),
    "about_md": (
        "**La Cata** sirve para organizar catas de vino a ciegas con puntuación automática.\n\n"
        "| Campo | Máx. | Criterio |\n|---|---|---|\n"
        "| Uva | 25 | Proporcional a uvas acertadas sobre todas las mencionadas (marcar de más resta) |\n"
        "| Origen | 25 | Exacto 25 · misma región 10 |\n"
        "| Crianza | 20 | Exacta 20 · contigua 8 |\n"
        "| Puntuación | 10 | ±0,5 → 10 · ±1 → 5 |\n"
        "| Alcohol | 10 | ±0,5 → 10 · ±1 → 6 · ±2 → 3 |\n"
        "| Precio | 10 | ±3 € o 15 % → 10 · ±6 € o 30 % → 6 · ±12 € o 50 % → 3 |\n\n"
        "Desarrollada por **César Ferri** con la ayuda de **Claude** (Anthropic).",
        "**La Cata** runs blind wine tastings with automatic scoring.\n\n"
        "| Field | Max | Rule |\n|---|---|---|\n"
        "| Grape | 25 | Share of correct grapes over all grapes named (extra guesses cost points) |\n"
        "| Region | 25 | Exact 25 · same wider region 10 |\n"
        "| Aging | 20 | Exact 20 · neighbouring 8 |\n"
        "| Rating | 10 | ±0.5 → 10 · ±1 → 5 |\n"
        "| Alcohol | 10 | ±0.5 → 10 · ±1 → 6 · ±2 → 3 |\n"
        "| Price | 10 | ±3 € or 15 % → 10 · ±6 € or 30 % → 6 · ±12 € or 50 % → 3 |\n\n"
        "Developed by **César Ferri** with the help of **Claude** (Anthropic).",
        "**El Tast** servix per a organitzar tasts de vi a cegues amb puntuació automàtica.\n\n"
        "| Camp | Màx. | Criteri |\n|---|---|---|\n"
        "| Raïm | 25 | Proporcional als raïms encertats sobre tots els mencionats (marcar-ne de més resta) |\n"
        "| Origen | 25 | Exacte 25 · mateixa regió 10 |\n"
        "| Criança | 20 | Exacta 20 · contigua 8 |\n"
        "| Puntuació | 10 | ±0,5 → 10 · ±1 → 5 |\n"
        "| Alcohol | 10 | ±0,5 → 10 · ±1 → 6 · ±2 → 3 |\n"
        "| Preu | 10 | ±3 € o 15 % → 10 · ±6 € o 30 % → 6 · ±12 € o 50 % → 3 |\n\n"
        "Desenvolupada per **César Ferri** amb l'ajuda de **Claude** (Anthropic).",
    ),
}

_IDX = {"es": 0, "en": 1, "va": 2}


def t(key: str, lang: str = "es") -> str:
    entry = T.get(key)
    if entry is None:
        return key
    return entry[_IDX.get(lang, 0)]
