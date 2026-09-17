from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ConfrontationPhase:
    id: str
    npc_statement: str
    required_cards: List[str]
    success_dialogue: str
    npc_reaction: str
    fail_reactions: str
    guidance_hint: Optional[str] = None
    condition_flag: Optional[str] = None

MORALES_CONFRONTATION = [
    ConfrontationPhase(
        id="morales_turno",
        npc_statement="Esa noche ni siquiera estaba de turno.",
        required_cards=["C03"],
        success_dialogue="Gallagher: Lauren revisó los turnos en la comisaría. Estabas asignado de 22:00 a 06:00.",
        npc_reaction="Morales suda y tartamudea.",
        fail_reactions="Morales: '¿Ves? Ni siquiera sabes de qué hablas.'\nGallagher: (No... Lauren me avisó de algo sobre sus horarios. Debo revisar los turnos.)",
        guidance_hint="Gallagher: (Lauren me dijo que revisara sus turnos. Esa es la clave.)"
    ),
    ConfrontationPhase(
        id="morales_deudas",
        npc_statement="Soy un pobre diablo. No tengo ni para el alquiler.",
        required_cards=["C02"],
        success_dialogue="Gallagher: Qué raro. Porque el 13 pagaste todas tus deudas de una vez.",
        npc_reaction="Morales entra en pánico.",
        fail_reactions="Morales: 'Te digo la verdad, pregúntale a cualquiera.'\nGallagher: (No encaja. Alguien que no tiene dinero no puede liquidar sus deudas de golpe.)"
    )
]

SOFIA_CONFRONTATION = [
    ConfrontationPhase(
        id="sofia_club",
        npc_statement="Casi no vengo al club. Apenas lo conozco.",
        required_cards=["C10"],
        success_dialogue="Gallagher: El portero de la mirilla sabía tu nombre. El barman sabía tu bebida. Eso no se consigue en un par de visitas.",
        npc_reaction="Sofia tensa la mandíbula y desvía la mirada.",
        fail_reactions="Sofia: 'Como dije, es un lugar extraño para mí.'\nGallagher: (Miente. La saludaron como a una habitual.)"
    ),
    ConfrontationPhase(
        id="sofia_llave",
        npc_statement="Esa llave... la encontré en unos viejos papeles familiares.",
        required_cards=["C09"],
        success_dialogue="Gallagher: Esa llave abre una sola puerta: la del sótano de Blackwood. Tu padre nunca bajó ahí. Tú sí.",
        npc_reaction="Sofia se cruza de brazos, defensiva.",
        fail_reactions="Sofia: '¿Acaso pruebas lo contrario?'\nGallagher: (Esa llave abre una cerradura muy específica según los planos.)"
    ),
    ConfrontationPhase(
        id="sofia_alias",
        npc_statement="Lirio es una flor genérica. Podría ser cualquiera.",
        required_cards=["C13"],
        success_dialogue="Gallagher: Solo una a la que su abuela llamaba así.",
        npc_reaction="Sofia guarda un largo silencio. La fachada cae.",
        fail_reactions="Sofia: 'El mundo está lleno de lirios, detective.'\nGallagher: (No, ella me contó en confianza quién la llamaba así.)"
    ),
    ConfrontationPhase(
        id="sofia_doble_cobro",
        npc_statement="El museo necesitaba salvarse de la ruina.",
        required_cards=["C07", "C15"],
        success_dialogue="Gallagher: Cobraste por venderlos y otra vez por recuperarlos. El museo no se estaba salvando. Se estaba vendiendo dos veces.",
        npc_reaction="Sofia sonríe con frialdad.",
        fail_reactions="Sofia: 'Hice lo necesario por el legado de mi padre.'\nGallagher: (No... hay un recorte de periódico antiguo y un libro de contabilidad que dicen lo contrario. Ambos se necesitan.)",
        condition_flag="doble_cobro_deducido"
    ),
    ConfrontationPhase(
        id="sofia_traicion",
        npc_statement="Todo estaba bajo control hasta que interveniste.",
        required_cards=["C11"],
        success_dialogue="Gallagher: Porque Blackwood se quedó con lo único que no estaba en venta. Y tú no podías ir a la policía a denunciar un robo que tú misma organizaste.",
        npc_reaction="Sofia aprieta los puños.",
        fail_reactions="Sofia: 'Tú arruinaste el plan.'\nGallagher: (Tengo una grabación que prueba que Blackwood se burlaba de ella. Ella fue la engañada.)",
        condition_flag="traicion_deducida"
    )
]

