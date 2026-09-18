"""
P.I. Gallagher: The Missing Art

Data module for all NPC dialogues, cutscene scripts, and ambient rumors.
Structured by character, location, and story level.
"""

from typing import Any, Dict, List

# ── Diálogos Estructurados por Personaje y Nivel ────────────────────────────

DIALOGUES: Dict[str, Dict[str, Any]] = {
    # ── Sofia Del Roscio (Oficina - Nivel 0) ──
    "sofia_office_intro": {
        "speaker": "Sofia Del Roscio",
        "pages": [
            (
                "Detective Gallagher... gracias por recibirme. "
                "Sé que sus métodos son poco convencionales, pero la policía "
                "no ha avanzado ni un palmo con el robo de mi museo."
            ),
            (
                "La noche del 12 sustrajeron 'La Dama del Lirio'. No es solo "
                "una obra renacentista de valor incalculable... es el legado "
                "más íntimo de mi familia."
            ),
            (
                "Necesito que examine la escena en el Museo Del Roscio. "
                "Su socia Lauren mencionó que buscaría antecedentes en los "
                "archivos policiales. Les pagaré el doble de su tarifa habitual."
            ),
        ],
        "reward_cards": [],
        "set_level": 1,
        "notification": "Caso aceptado: Recuperar 'La Dama del Lirio'",
    },
    # ── Sofia Del Roscio (Club Velvet - Nivel 3) ──
    "sofia_club": {
        "speaker": "Sofia Del Roscio",
        "pages": [
            (
                "Detective... no esperaba que llegara tan rápido al Club Velvet. "
                "Apenas he pisado este club un par de veces en mi vida, pero me dijeron "
                "que Blackwood podría tener tratos con el mercado negro de arte."
            ),
            (
                "Ese cuadro... mi abuela solía llamarme 'Lirio' cuando era niña, "
                "precisamente por la pintura. No puedo permitir que caiga en manos "
                "de un contrabandista vulgar."
            ),
            (
                "Encontré esta llave de latón entre los papeles viejos de mi padre. "
                "Dicen que abre la puerta de servicio que conduce al sótano del club. "
                "Tómela. Tenga mucho cuidado con los guardias de Blackwood."
            ),
        ],
        "reward_cards": ["C08", "C10", "C13", "C14"],
        "set_flags": {"sofia_club_talked": True},
        "notification": "Nuevas pistas obtenidas: Llave de Sofia, Recuerdo y Declaración",
    },
    # ── Lauren (Oficina - Compañera) ──
    "lauren_office": {
        "speaker": "Lauren",
        "default": [
            "Jefe, tenemos que revisar las pistas en la pizarra de corcho.",
            "Si unimos las palabras clave correctas con el hilo rojo, las piezas encajarán.",
            "No deje que Blackwood se nos adelante.",
        ],
        "hints": {
            0: "Espere a que la señorita Del Roscio nos explique el caso.",
            1: "Vaya al museo a inspeccionar el marco robado mientras yo saco el expediente del archivo policial.",
            2: "El corcho I está listo. Conecte los turnos del guardia con sus gastos repentinos.",
            3: "El canillita en la plaza suele tener periódicos viejos con noticias interesantes. Luego iremos al Club.",
            4: "Esa llave de Sofia debe abrir algo en los planos que encontramos en las oficinas de Blackwood.",
            5: "La bóveda de Blackwood... es hora de escuchar los números de la caja fuerte.",
            6: "¡Tenemos todas las pruebas! Vuelva a la pizarra para armar la teoría final.",
        },
    },
    # ── Curador del Museo (Museo) ──
    "museum_curator": {
        "speaker": "Curador Lombardi",
        "pages": [
            (
                "¡Es una tragedia inmensa, detective! 'La Dama del Lirio' estaba colgada "
                "en esa pared del fondo. A la mañana siguiente, solo quedaba el marco vacío."
            ),
            (
                "Lo más desconcertante es que las cerraduras de roble estaban intactas "
                "y el sistema de alarma desconectado limpiamente desde el panel interior. "
                "Inspeccione usted mismo la pared del fondo si no me cree."
            ),
        ],
    },
    # ── Inspección del Marco Vacío en Museo ──
    "museum_frame_inspection": {
        "speaker": "P.I. Gallagher",
        "pages": [
            (
                "El marco dorado sigue en la pared. El lienzo fue cortado con precisión "
                "quirúrgica. Ninguna cerradura rota... y los cables de la campana de "
                "alarma fueron aislados con cinta de tela desde dentro."
            ),
            (
                "Fue un trabajo interno sin forzar. Quien lo hizo conocía las rondas "
                "y los códigos de seguridad."
            ),
        ],
        "reward_cards": ["C01"],
        "notification": "Nueva pista: C01 Informe policial (sin forzar, alarma desactivada)",
    },
    # ── Oficial de la Comisaría ──
    "police_officer": {
        "speaker": "Sargento Bianchi",
        "pages": [
            (
                "Circulen, caballeros. La comisaría central está hasta arriba de trabajo "
                "por los disturbios en el puerto. El archivo del sótano está restringido "
                "a personal autorizado... no queremos curiosos husmeando cajones."
            ),
        ],
    },
    # ── Canillita / Newsboy (Ciudad) ──
    "canillita": {
        "speaker": "Canillita",
        "default": [
            "¡Extra, extra! ¡La crisis arrecia en los muelles!",
            "¡Compre el diario de la tarde! ¡Tres centavos!",
        ],
        "special_c07": {
            "speaker": "Canillita",
            "pages": [
                (
                    "¡Oiga, mister! ¿Usted es el detective Gallagher? "
                    "Un colega me dijo que andaba preguntando por los Del Roscio."
                ),
                (
                    "Mire lo que encontré limpiando la trastienda del puesto: "
                    "un recorte de prensa de hace dos años. Dice que el museo "
                    "ya cobró un seguro millonario por otra pieza que luego 'reapareció'. "
                    "¡Tómelo, seguro le sirve más a usted que a mí!"
                ),
            ],
            "reward_cards": ["C07"],
            "set_flags": {"recorte_encontrado": True},
            "notification": "Nueva pista obtenida: C07 Recorte de periódico (opcional)",
        },
    },
    # ── Morales (Callejón - Nivel 2) ──
    "morales_interrogation": {
        "speaker": "Guardia Morales",
        "pages": [
            (
                "¡No me haga nada, detective! ¡Yo no quería meterme en esto! "
                "Un tipo con traje a rayas vino al bar y me puso un fajo de billetes en la mano. "
                "Solo tenía que dejar la puerta trasera entreabierta y apagar la alarma."
            ),
            (
                "Dijo que venía de parte de Cornelius Blackwood... y mencionó a un tal "
                "'el Tigre' si abría la boca. ¡Mire, se me cayó esta caja de cerillas "
                "del club nocturno donde me citaron! ¡No sé nada más, se lo juro!"
            ),
        ],
        "reward_cards": ["C04", "C05", "C06"],
        "notification": "Pistas obtenidas: C04 Caja de cerillas, C05 Testimonio y C06 Recibo",
    },
    # ── Portero del Club Velvet ──
    "nightclub_doorman": {
        "speaker": "Portero del Club",
        "pages_locked": [
            (
                "Alto ahí, forastero. Este es un club privado de caballeros. "
                "Sin contraseña en la mirilla, no entra ni el mismísimo alcalde."
            ),
        ],
        "pages_unlocked": [
            (
                "¿La contraseña de la cerilla?... Pase, detective. "
                "La señorita Del Roscio lo está esperando en un reservado al fondo."
            ),
        ],
    },
    # ── Transeúntes y Rumores en la Ciudad ──
    "citizen_unemployed": {
        "speaker": "Desempleado",
        "pages": [
            (
                "Desde el crack del 29 la ciudad se fue al diablo. Los ricos del museo "
                "siguen viviendo de fiestas y seguros, mientras nosotros hacemos cola "
                "por un plato de sopa caliente."
            ),
        ],
    },
    "citizen_patron": {
        "speaker": "Parroquiano",
        "pages": [
            (
                "Dicen que Cornelius Blackwood maneja todo el licor y el juego clandestino. "
                "Nadie entra a su bóveda sin que su perro de presa, 'el Tigre', lo sepa."
            ),
        ],
    },
    # ── Emboscada y Victoria de Niko Stieger (Club Velvet) ──
    "steiger_ambush": {
        "speaker": "Niko Stieger",
        "pages": [
            "Blackwood dijo que vendrías, detective. Pero no te pagó para salir vivo con esto.",
        ],
        "reward_cards": ["C18"],
    },
    "steiger_victory": {
        "speaker": "P.I. Gallagher",
        "pages": [
            "Stieger cae noqueado contra el suelo de la bóveda... Su Thompson rueda humeante por las baldosas.",
            "Tengo el cuadro 'La Dama del Lirio' y los libros de contabilidad. Debo volver a mi oficina para organizar las pruebas finales en el corcho.",
        ],
    },
    # ── Careo Final con Sofia (Museo) ──
    "sofia_museum": {
        "speaker": "Sofia Del Roscio",
        "pages": [
            "Detective... Veo que logró salir con vida de la guarida de Blackwood.",
            "¿Recuperó 'La Dama del Lirio'? ¿O acaso vino a mirarme como si ocultara algo?",
        ],
    },
}

