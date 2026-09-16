"""
P.I. Gallagher: The Missing Art

Data module for Minigame 1: Police Archive (Lauren).
All game data for Phase A (Filing Cabinet) and Phase B (Document Table).
"""

import pygame

# ── Noir Color Palette (1932) ──────────────────────────────────────────────

COLORS = {
    "background": (25, 20, 18),
    "panel": (45, 38, 32),
    "panel_light": (60, 52, 44),
    "paper": (215, 198, 168),
    "paper_dark": (185, 168, 138),
    "ink": (30, 25, 22),
    "ink_blue": (45, 55, 90),
    "highlight": (200, 140, 50),
    "danger": (160, 50, 40),
    "success": (80, 140, 70),
    "muted": (130, 120, 105),
    "brass": (175, 140, 65),
    "brass_dark": (130, 100, 45),
    "text": (218, 214, 198),
    "text_dark": (80, 75, 65),
}

# ── Phase A: Filing Cabinet ────────────────────────────────────────────────

CATEGORY_ORDER = ["Fecha", "Apellido", "Ubicación"]

CABINET = {
    "Fecha": {
        "label": "FECHA",
        "drawers": [
            {
                "label": "12/03/1932",
                "text": (
                    "Fecha: 12 de marzo de 1932.\n"
                    "Expediente abierto: robo en el\n"
                    "Museo Del Roscio.\n"
                    "Revisar personal nocturno asignado.\n"
                    "\n"
                    "Véase: Apellido > Del Roscio"
                ),
                "reference": "Apellido > Del Roscio",
                "is_goal": False,
            },
            {
                "label": "05/01/1932",
                "text": (
                    "Fecha: 5 de enero de 1932.\n"
                    "Informe de rutina: patrulla\n"
                    "nocturna. Sin novedades.\n"
                    "Caso archivado."
                ),
                "reference": None,
                "is_goal": False,
            },
            {
                "label": "28/02/1932",
                "text": (
                    "Fecha: 28 de febrero de 1932.\n"
                    "Denuncia por alteración del\n"
                    "orden público. Plaza San Marco.\n"
                    "Caso cerrado."
                ),
                "reference": None,
                "is_goal": False,
            },
            {
                "label": "15/04/1931",
                "text": (
                    "Fecha: 15 de abril de 1931.\n"
                    "Recibo de suministros de oficina.\n"
                    "Archivado sin seguimiento."
                ),
                "reference": None,
                "is_goal": False,
            },
        ],
    },
    "Apellido": {
        "label": "APELLIDO",
        "drawers": [
            {
                "label": "Del Roscio",
                "text": (
                    "EXPEDIENTE #12-03-MR\n"
                    "Del Roscio, Museo.\n"
                    "Robo de obra de arte.\n"
                    "Denuncia: 13/03/1932.\n"
                    "Asignado: Comisaría Central.\n"
                    "\n"
                    ">>> EXPEDIENTE LOCALIZADO <<<"
                ),
                "reference": None,
                "is_goal": True,
            },
            {
                "label": "Morales",
                "text": (
                    "Morales, Varios.\n"
                    "Registros de personal.\n"
                    "Historial de servicio:\n"
                    "ver archivos de RRHH.\n"
                    "No disponible en este fichero."
                ),
                "reference": None,
                "is_goal": False,
            },
            {
                "label": "Stieger",
                "text": (
                    "Stieger, N.\n"
                    "Ficha policial pendiente.\n"
                    "Remitir a investigaciones.\n"
                    "Sin expediente abierto."
                ),
                "reference": None,
                "is_goal": False,
            },
        ],
    },
    "Ubicación": {
        "label": "UBICACIÓN",
        "drawers": [
            {
                "label": "Museo Del Roscio",
                "text": (
                    "Museo Del Roscio.\n"
                    "Calle Vittoria, 24.\n"
                    "Denuncias registradas: 3\n"
                    "(1929-1932).\n"
                    "Último incidente:\n"
                    "\n"
                    "Véase: Fecha > 12/03/1932"
                ),
                "reference": "Fecha > 12/03/1932",
                "is_goal": False,
            },
            {
                "label": "Puerto Norte",
                "text": (
                    "Puerto Norte.\n"
                    "Zona de carga industrial.\n"
                    "Actividad portuaria regular.\n"
                    "Sin incidentes recientes."
                ),
                "reference": None,
                "is_goal": False,
            },
            {
                "label": "Hotel Excelsior",
                "text": (
                    "Hotel Excelsior.\n"
                    "Avenida Central, 8.\n"
                    "Registro de huéspedes\n"
                    "clasificado. Consultar\n"
                    "con recepción."
                ),
                "reference": None,
                "is_goal": False,
            },
        ],
    },
}

MAX_DRAWERS = 5

# ── Phase B: Documents ─────────────────────────────────────────────────────

PHASE_B_DOCUMENTS = [
    {
        "id": "C03",
        "title": "Registro de Turnos - Museo",
        "body": (
            "REGISTRO DE TURNOS\n"
            "MUSEO DEL ROSCIO\n"
            "\n"
            "Turno del 12/03/1932:\n"
            "Guardia asignado:\n"
            "  Oficial {Morales}, J.\n"
            "  Horario: 22:00 - 06:00\n"
            "  {turno de noche 12/03}\n"
            "\n"
            "Observaciones: Sin incidentes\n"
            "reportados por el guardia.\n"
            "Obra desaparecida detectada al\n"
            "cambio de turno matutino."
        ),
        "keywords": ["Morales", "turno de noche 12/03"],
        "is_relevant": True,
        "clue_id": "C03",
    },
    {
        "id": "C02",
        "title": "Informe Confidencial",
        "body": (
            "INFORME DEL SOPLÓN\n"
            "CONFIDENCIAL\n"
            "\n"
            "Fuente: Agente encubierto.\n"
            "\n"
            "Sujeto: {Morales}, J. (Guardia)\n"
            "Visto liquidando\n"
            "{deudas pagadas 13/03} en el bar\n"
            "El Ancla, un día después del robo.\n"
            "Cantidad estimada: considerable.\n"
            "Origen de fondos: desconocido."
        ),
        "keywords": ["Morales", "deudas pagadas 13/03"],
        "is_relevant": True,
        "clue_id": "C02",
    },
    {
        "id": "C12",
        "title": "Ficha Policial - Stieger",
        "body": (
            "FICHA POLICIAL\n"
            "STIEGER, Nikolaus\n"
            "\n"
            "Alias: \"{el Tigre}\"\n"
            "Nacionalidad: Austrohúngara\n"
            "Antecedentes: Contrabando.\n"
            "\n"
            "Señas: Cicatriz en mejilla izq.\n"
            "Porta un {encendedor} de plata\n"
            "con grabado de tigre.\n"
            "\n"
            "Última ubicación: Muelle 7."
        ),
        "keywords": ["el Tigre", "encendedor"],
        "is_relevant": True,
        "clue_id": "C12",
    },
    {
        "id": "D01",
        "title": "Denuncia - Orden Público",
        "body": (
            "DENUNCIA\n"
            "ALTERACIÓN DEL ORDEN\n"
            "\n"
            "Fecha: 10/03/1932\n"
            "Lugar: Plaza de San Marco\n"
            "\n"
            "Denunciante: Sr. Giordano.\n"
            "Ruidos excesivos del local\n"
            "\"La Paloma\" en horas nocturnas.\n"
            "\n"
            "Acción: Amonestación verbal.\n"
            "Caso cerrado."
        ),
        "keywords": [],
        "is_relevant": False,
        "clue_id": None,
    },
    {
        "id": "D02",
        "title": "Recibo - Suministros",
        "body": (
            "RECIBO DE SUMINISTROS\n"
            "Comisaría Central\n"
            "08/03/1932\n"
            "\n"
            "Artículos recibidos:\n"
            "- Papel de máquina (5 resmas)\n"
            "- Cintas de tinta (12 uds.)\n"
            "- Carpetas archivo (50 uds.)\n"
            "- Clips metálicos (3 cajas)\n"
            "\n"
            "Total: 47,50 liras\n"
            "Autorizado: Sgto. Bianchi"
        ),
        "keywords": [],
        "is_relevant": False,
        "clue_id": None,
    },
    {
        "id": "D03",
        "title": "Reporte - Puerto",
        "body": (
            "REPORTE DE TRÁFICO PORTUARIO\n"
            "Semana 7-13 marzo, 1932\n"
            "\n"
            "Embarcaciones registradas: 23\n"
            "Carga declarada: Textiles,\n"
            "maquinaria agrícola, vino.\n"
            "\n"
            "Incidentes: Ninguno.\n"
            "Inspecciones aduaneras: 4\n"
            "\n"
            "Firmado: Inspector Rosetti\n"
            "Aduana Marítima"
        ),
        "keywords": [],
        "is_relevant": False,
        "clue_id": None,
    },
    {
        "id": "D04",
        "title": "Memo - Horarios",
        "body": (
            "MEMORÁNDUM INTERNO\n"
            "\n"
            "De: Capitán Ferrara\n"
            "Para: Todo el personal\n"
            "Fecha: 01/03/1932\n"
            "\n"
            "Los turnos de guardia rotarán\n"
            "cada 48 horas a partir del 15/03.\n"
            "Medida temporal por recortes.\n"
            "Acuse de recibo obligatorio."
        ),
        "keywords": [],
        "is_relevant": False,
        "clue_id": None,
    },
    {
        "id": "D05",
        "title": "Informe - Accidente",
        "body": (
            "INFORME DE ACCIDENTE\n"
            "\n"
            "Fecha: 11/03/1932\n"
            "Lugar: Via Roma / Corso Vittorio\n"
            "\n"
            "Carruaje colisionó con automóvil\n"
            "Ford modelo A.\n"
            "Sin heridos graves.\n"
            "Daños materiales menores.\n"
            "\n"
            "Responsable: conductor del\n"
            "carruaje. Multa: 15 liras."
        ),
        "keywords": [],
        "is_relevant": False,
        "clue_id": None,
    },
]

CLUES = {
    "C02": {
        "id": "C02",
        "tipo": "pista",
        "titulo": "Informe del soplón",
        "claves": ["Morales", "deudas pagadas 13/03"],
        "opcional": False,
    },
    "C03": {
        "id": "C03",
        "tipo": "pista",
        "titulo": "Turnos del museo",
        "claves": ["Morales", "turno de noche 12/03"],
        "opcional": False,
    },
    "C12": {
        "id": "C12",
        "tipo": "pista",
        "titulo": "Ficha policial de Niko Stieger",
        "claves": ["el Tigre", "encendedor"],
        "opcional": False,
    },
}

REQUIRED_CLUES = ["C02", "C03", "C12"]

PHASE_B_TIME_LIMIT = 90
PHASE_B_TIME_PENALTY = 10

# ── Narrative Texts ────────────────────────────────────────────────────────

INTRO_TEXT = (
    "Mientras Gallagher examina el Museo Del Roscio,\n"
    "Lauren se infiltra en el sótano del archivo\n"
    "de la comisaría.\n"
    "\n"
    "Su misión: encontrar el expediente del robo\n"
    "y descubrir quién estaba de guardia esa noche.\n"
    "\n"
    "Solo puede abrir 5 cajones del fichero\n"
    "antes de que regrese el archivero."
)

PHASE_A_FAIL_TEXT = (
    "El archivero regresa.\n"
    "Lauren se esconde tras un estante\n"
    "y espera a que se marche de nuevo..."
)

PHASE_B_FAIL_TEXT = (
    "El archivero regresa.\n"
    "Lauren oculta los documentos y se\n"
    "esconde tras un estante..."
)

SUCCESS_TEXT = (
    "Lauren guarda las pruebas en su bolso\n"
    "y sale del sótano con aire inocente.\n"
    "\n"
    "Las pistas obtenidas serán cruciales\n"
    "para resolver el caso."
)


# ── Rendering Utilities ───────────────────────────────────────────────────

def render_keyword_line(surface, line, font, x, y, normal_color, keyword_color):
    """Render a single line of text with {keywords} highlighted."""
    cursor_x = x
    i = 0
    while i < len(line):
        brace_start = line.find("{", i)
        if brace_start == -1:
            # No more keywords — render the rest normally
            if i < len(line):
                text_surf = font.render(line[i:], True, normal_color)
                surface.blit(text_surf, (cursor_x, y))
            break
        # Render text before the keyword
        if brace_start > i:
            normal_text = line[i:brace_start]
            text_surf = font.render(normal_text, True, normal_color)
            surface.blit(text_surf, (cursor_x, y))
            cursor_x += text_surf.get_width()
        # Find end of keyword
        brace_end = line.find("}", brace_start)
        if brace_end == -1:
            # Malformed — render rest as normal
            text_surf = font.render(line[brace_start:], True, normal_color)
            surface.blit(text_surf, (cursor_x, y))
            break
        # Render keyword text highlighted
        keyword_text = line[brace_start + 1 : brace_end]
        text_surf = font.render(keyword_text, True, keyword_color)
        surface.blit(text_surf, (cursor_x, y))
        cursor_x += text_surf.get_width()
        i = brace_end + 1
