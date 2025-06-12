from typing import List, Optional
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel

from langgraph.graph import MessagesState, END

class Event(BaseModel):
    id: int
    titulo: str
    content: str
    fecha: str
    link: str
    imagen: Optional[str] = "Sin imagen"

class EventAgenState(MessagesState):
    user_query: str
    events: List[Event]


BUSCADOR_PROMPT = PromptTemplate.from_template("""
Estás ayudando a un atleta a encontrar un evento deportivo.
El atleta te dice: "{user_query}"

A continuación tenés una lista de eventos disponibles con su título, fecha y ciudad. Elegí los 5 que mejor coincidan con su intención.

Eventos:
{eventos}

Devolvé solo los títulos de los 3 eventos más relevantes, cada uno en una línea.
""")