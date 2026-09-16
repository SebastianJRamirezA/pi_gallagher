"""
P.I. Gallagher: The Missing Art

Data module for all cards (pistas, deducciones, sospechas, ruido),
deduction rules, open questions, and failure feedback for the Corkboard.
Based strictly on GDD v1.1 specifications.
"""

from typing import Any, Dict, List, Optional

# ── Catálogo de Tarjetas (C01 a C18) ───────────────────────────────────────

CARDS: Dict[str, Dict[str, Any]] = {
    "C01": {
        "id": "C01",
        "tipo": "pista",
        "titulo": "Informe policial",
        "claves": ["sin forzar", "alarma desactivada"],
        "visita": 1,
        "opcional": False,
        "descripcion": "El museo no muestra signos de entrada forzada. La alarma fue apagada desde dentro.",
        "origen": "Museo Del Roscio",
    },
    "C02": {
        "id": "C02",
        "tipo": "pista",
        "titulo": "Informe del soplón",
        "claves": ["Morales", "deudas pagadas 13/03"],
        "visita": 1,
        "opcional": False,
        "descripcion": "El guardia Morales liquidó deudas sustanciales en 'El Ancla' al día siguiente del robo.",
        "origen": "Archivo Comisaría (Lauren)",
    },
    "C03": {
        "id": "C03",
        "tipo": "pista",
        "titulo": "Turnos del museo",
        "claves": ["Morales", "turno de noche 12/03"],
        "visita": 1,
        "opcional": False,
        "descripcion": "Oficial Morales asignado al turno de 22:00 a 06:00 la noche en que desapareció la obra.",
        "origen": "Archivo Comisaría (Lauren)",
    },
    "C04": {
        "id": "C04",
        "tipo": "pista",
        "titulo": "Caja de cerillas",
        "claves": ["Club Velvet", "contraseña"],
        "visita": 2,
        "opcional": False,
        "descripcion": "Cerillas con el logo del Club Velvet y una contraseña manuscrita en el reverso.",
        "origen": "Callejón (soltada por Morales)",
    },
    "C05": {
        "id": "C05",
        "tipo": "pista",
        "titulo": "Testimonio de Morales",
        "claves": ["hombre de Blackwood", "el Tigre"],
        "visita": 2,
        "opcional": False,
        "descripcion": "Morales confiesa que un emisario de Blackwood pagó el soborno y menciona a 'el Tigre'.",
        "origen": "Careo en Callejón",
    },
    "C06": {
        "id": "C06",
        "tipo": "ruido",
        "titulo": "Recibo del prestamista",
        "claves": ["deuda", "Morales"],
        "visita": 2,
        "opcional": False,
        "descripcion": "Un recibo arrugado de un prestamista local fechado el mes pasado.",
        "origen": "Callejón",
    },
    "C07": {
        "id": "C07",
        "tipo": "pista",
        "titulo": "Recorte de periódico",
        "claves": ["Del Roscio recuperan pieza", "fecha"],
        "visita": 2,
        "opcional": True,
        "descripcion": "Noticia de 1930: La familia Del Roscio recuperó una obra dada por robada tras cobrar el seguro.",
        "origen": "Canillita en la calle",
    },
    "C08": {
        "id": "C08",
        "tipo": "pista",
        "titulo": "Llave de Sofia",
        "claves": ["sótano", "puerta de servicio"],
        "visita": 3,
        "opcional": False,
        "descripcion": "Llave de latón pesada entregada por Sofia. Abre la puerta de servicio hacia el sótano.",
        "origen": "Club Velvet (Sofia)",
    },
    "C09": {
        "id": "C09",
        "tipo": "pista",
        "titulo": "Planos del club",
        "claves": ["bóveda", "puerta de servicio"],
        "visita": 3,
        "opcional": False,
        "descripcion": "Plano arquitectónico que muestra una bóveda blindada oculta tras la puerta de servicio.",
        "origen": "Oficinas Club Velvet",
    },
    "C10": {
        "id": "C10",
        "tipo": "pista",
        "titulo": "Saludo del personal",
        "claves": ["Buenas noches, señorita Del Roscio", "Club Velvet"],
        "visita": 3,
        "opcional": False,
        "descripcion": "El personal del Club Velvet reconoció a Sofia de inmediato al entrar.",
        "origen": "Salón Club Velvet",
    },
    "C11": {
        "id": "C11",
        "tipo": "pista",
        "titulo": "Grabación de alambre",
        "claves": ["la socia", "que busque"],
        "visita": 3,
        "opcional": False,
        "descripcion": "Grabación secreta: Blackwood dice 'La socia sigue buscando su cuadro. Que busque.'",
        "origen": "Oficinas Club Velvet (escucha)",
    },
    "C12": {
        "id": "C12",
        "tipo": "pista",
        "titulo": "Ficha policial de Stieger",
        "claves": ["el Tigre", "encendedor"],
        "visita": 2,
        "opcional": False,
        "descripcion": "Nikolaus Stieger, alias 'el Tigre'. Contrabandista con cicatriz y encendedor grabado.",
        "origen": "Archivo Comisaría (Lauren)",
    },
    "C13": {
        "id": "C13",
        "tipo": "pista",
        "titulo": "Recuerdo de Sofia",
        "claves": ["Lirio", "abuela", "La Dama del Lirio"],
        "visita": 3,
        "opcional": False,
        "descripcion": "Sofia reveló en confianza que su abuela solía llamarla cariñosamente 'Lirio'.",
        "origen": "Cita Club Velvet (Sofia)",
    },
    "C14": {
        "id": "C14",
        "tipo": "pista",
        "titulo": "Declaración de Sofia",
        "claves": ["casi no vengo al club", "Club Velvet"],
        "visita": 3,
        "opcional": False,
        "descripcion": "Sofia afirmó tajantemente que apenas había pisado el Club Velvet en su vida.",
        "origen": "Cita Club Velvet (Sofia)",
    },
    "C15": {
        "id": "C15",
        "tipo": "pista",
        "titulo": "Libro de contabilidad",
        "claves": ["Lirio: 40%", "fechas de pago"],
        "visita": 4,
        "opcional": False,
        "descripcion": "Registro contable de Blackwood con pagos asignados a 'Lirio: 40%' con fechas coincidentes.",
        "origen": "Bóveda (Caja Fuerte)",
    },
    "C16": {
        "id": "C16",
        "tipo": "pista",
        "titulo": "El cuadro",
        "claves": ["La Dama del Lirio", "bóveda"],
        "visita": 4,
        "opcional": False,
        "descripcion": "La obra maestra renacentista 'La Dama del Lirio', guardada intacta en la caja fuerte.",
        "origen": "Bóveda (Caja Fuerte)",
    },
    "C17": {
        "id": "C17",
        "tipo": "ruido",
        "titulo": "Nota de reventa",
        "claves": ["comprador", "Blackwood"],
        "visita": 4,
        "opcional": False,
        "descripcion": "Borrador de una venta de licor y antigüedades menores firmado por Blackwood.",
        "origen": "Bóveda (Caja Fuerte)",
    },
    "C18": {
        "id": "C18",
        "tipo": "pista",
        "titulo": "Frase de Stieger",
        "claves": ["Blackwood dijo que vendrías", "el Tigre"],
        "visita": 4,
        "opcional": False,
        "descripcion": "Stieger esperaba al detective: 'Blackwood dijo que vendrías.'",
        "origen": "Sótano de Blackwood",
    },
}

# ── Deducciones y Sospechas ────────────────────────────────────────────────

DEDUCTIONS: Dict[str, Dict[str, Any]] = {
    "D01": {
        "id": "D01",
        "tipo": "deduccion",
        "titulo": "Morales dejó entrar a los ladrones y cobró por ello",
        "required_cards": {"C01", "C02", "C03"},
        "visita": 1,
        "texto": (
            "El guardia Morales estaba de turno la noche del robo sin forcejeos, "
            "y misteriosamente saldó todas sus deudas al día siguiente. Morales "
            "fue el cómplice interno."
        ),
        "unlocks": "callejón",
        "unlock_text": "Deducción D01 resuelta: El callejón del guardia Morales ha sido desbloqueado.",
    },
    "DX1": {
        "id": "DX1",
        "tipo": "deduccion",
        "titulo": "Morales aceptó el soborno por deudas",
        "required_cards": {"C05", "C06"},
        "visita": 2,
        "texto": "Las deudas asfixiaban a Morales, haciéndolo blanco fácil para los hombres de Blackwood.",
        "unlocks": None,
        "unlock_text": "Confirmación secundaria anotada en el cuaderno.",
    },
    "DX2": {
        "id": "DX2",
        "tipo": "deduccion",
        "titulo": "El Tigre es Niko Stieger",
        "required_cards": {"C05", "C12"},
        "visita": 2,
        "texto": "El matón mencionado por Morales es Niko Stieger, contrabandista peligroso al servicio de Blackwood.",
        "unlocks": None,
        "unlock_text": "Identidad confirmada: Niko Stieger es 'el Tigre'.",
    },
    "D02": {
        "id": "D02",
        "tipo": "deduccion",
        "titulo": "El dinero sale del club de Blackwood",
        "required_cards": {"C04", "C05"},
        "visita": 2,
        "texto": (
            "La caja de cerillas con la contraseña y el testimonio de Morales "
            "conectan directamente el soborno con el Club Velvet de Cornelius Blackwood."
        ),
        "unlocks": "nightclub",
        "unlock_text": "Deducción D02 resuelta: El acceso al Club Velvet ha sido desbloqueado.",
    },
    "D03": {
        "id": "D03",
        "tipo": "deduccion",
        "titulo": "La llave abre la bóveda",
        "required_cards": {"C08", "C09"},
        "visita": 3,
        "texto": (
            "La llave de servicio que entregó Sofia coincide exactamente con la "
            "cerradura de la bóveda subterránea mostrada en los planos de Blackwood."
        ),
        "unlocks": "boveda",
        "unlock_text": "Deducción D03 resuelta: La bóveda subterránea de Blackwood ha sido desbloqueada.",
    },
    "S01": {
        "id": "S01",
        "tipo": "sospecha",
        "titulo": "Sofia conoce el club mejor de lo que dice",
        "required_cards": {"C10", "C14"},
        "visita": 3,
        "texto": (
            "Contradicción clara: Sofia aseguró apenas pisar el club, pero el portero "
            "y los camareros la saludaron de inmediato por su nombre."
        ),
        "unlocks": None,
        "unlock_text": "Sospecha fijada en el corcho: Sofia mintió sobre el club.",
    },
    "S02": {
        "id": "S02",
        "tipo": "sospecha",
        "titulo": "Alguien avisó a Blackwood",
        "required_cards": {"C12", "C18"},
        "visita": 4,
        "texto": "Stieger esperaba a Gallagher en la bóveda. Alguien le filtró los movimientos del detective.",
        "unlocks": None,
        "unlock_text": "Sospecha fijada en el corcho: Fuga de información.",
    },
    "D04": {
        "id": "D04",
        "tipo": "deduccion",
        "titulo": "El alias es Sofia",
        "required_cards": {"C13", "C15"},
        "visita": 4,
        "texto": (
            "El porcentaje del 40% para 'Lirio' en la contabilidad corresponde al "
            "apodo de infancia que solo la abuela de Sofia Del Roscio utilizaba."
        ),
        "unlocks": None,
        "unlock_text": "Identidad revelada: Sofia Del Roscio es 'Lirio'.",
    },
    "D05": {
        "id": "D05",
        "tipo": "deduccion",
        "titulo": "Sofia es socia de Blackwood",
        "required_cards": {"C11", "C13", "C15"},  # o D04 + C11
        "visita": 4,
        "texto": (
            "La voz de Blackwood llamándola 'la socia' y los libros contables confirman "
            "que Sofia orquestó el robo en sociedad con Blackwood."
        ),
        "unlocks": "teoria_final",
        "unlock_text": "Teoría central confirmada: Sofia y Blackwood eran socios.",
    },
    "D06": {
        "id": "D06",
        "tipo": "deduccion",
        "titulo": "Sofia cobraba dos veces",
        "required_cards": {"C07", "C15"},
        "visita": 4,
        "texto": (
            "Sofia vendía el cuadro a través de Blackwood y luego cobraba el seguro o "
            "la recompensa de recuperación. El museo se vendía dos veces."
        ),
        "flag": "doble_cobro_deducido",
        "unlocks": None,
        "unlock_text": "Flag activado: doble_cobro_deducido (Desbloquea Refutación 4 y Final C).",
    },
    "D07": {
        "id": "D07",
        "tipo": "deduccion",
        "titulo": "Blackwood traicionó a Sofia",
        "required_cards": {"C11", "C16"},
        "visita": 4,
        "texto": (
            "Blackwood guardó el cuadro en su bóveda en vez de revenderlo. Por eso "
            "Sofia contrató a Gallagher: Blackwood la engañó."
        ),
        "flag": "traicion_deducida",
        "unlocks": None,
        "unlock_text": "Flag activado: traicion_deducida (Desbloquea Refutación 5 y Final D).",
    },
    "F01": {
        "id": "F01",
        "tipo": "ruido",
        "titulo": "Blackwood es el único cerebro",
        "required_cards": {"C15", "C17"},
        "visita": 4,
        "texto": "Teoría incompleta: Atribuir todo a Blackwood ignora la complicidad interna de la familia Del Roscio.",
        "unlocks": None,
        "unlock_text": "Gallagher reflexiona: 'No cuadra. Hay piezas que apuntan a alguien más cercano.'",
    },
}

# ── Columna de Preguntas Abiertas (Corcho II y III) ───────────────────────

OPEN_QUESTIONS: Dict[int, List[str]] = {
    1: [
        "¿Quién facilitó la entrada al museo?",
        "¿Por qué no sonó la alarma?",
    ],
    2: [
        "¿Quién es 'el Tigre' y para quién trabaja?",
        "¿De dónde salió el dinero que cobró Morales?",
        "¿Qué significa el recorte de prensa de 1930?",
    ],
    3: [
        "¿Qué relación real tiene Sofia con el Club Velvet?",
        "¿A quién se refiere Blackwood con 'la socia'?",
        "¿Qué oculta la bóveda del sótano?",
    ],
    4: [
        "¿Quién es verdaderamente 'Lirio'?",
        "¿Por qué Blackwood conservaba el cuadro en su bóveda?",
        "¿Quién alertó a Stieger en la trastienda?",
    ],
}

# ── Monólogos de Error de Gallagher ────────────────────────────────────────

FAILURE_MONOLOGUES = [
    "No... estas pistas no tienen relación lógica. Debo observar mejor las palabras clave.",
    "Estoy forzando una conexión que no existe. El hilo rojo debe unir hechos irrefutables.",
    "Lauren me miraría con cara de duda. Esto no prueba nada concreto todavía.",
    "Un buen detective no inventa teorías: las deja hablar por sí solas. Probemos otra combinación.",
    "Interesante, pero no hay causa y efecto demostrable entre estos dos elementos.",
]

# ── Ayudas de Lauren por Visita ───────────────────────────────────────────

LAUREN_HINTS: Dict[int, str] = {
    1: (
        "Lauren: 'Jefe, mire los turnos de la guardia y compárelos con el informe del soplón. "
        "Alguien pagó muchas deudas justo al día siguiente del robo sin forzar.'"
    ),
    2: (
        "Lauren: 'Esa caja de cerillas de Morales tiene que venir de algún sitio nocturno. "
        "Y recuerde lo que dijo el guardia sobre el hombre de Blackwood.'"
    ),
    3: (
        "Lauren: 'La llave que nos dio la señorita Del Roscio... compárela con los planos "
        "que recuperó de la oficina de Blackwood.'"
    ),
    4: (
        "Lauren: 'Aquí está todo sobre la mesa, Tim. El alias en los libros contables, "
        "las palabras de Blackwood y lo que Sofia le contó en el club.'"
    ),
}

