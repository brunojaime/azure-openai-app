import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mcp.server.fastmcp import FastMCP
import httpx
from typing import Optional, List
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel

load_dotenv()

mcp = FastMCP("AsDeporte")

# ---- MODELO ----
class Evento(BaseModel):
    id: int
    titulo: str
    content: str
    fecha: str
    link: str
    imagen: Optional[str] = "Sin imagen"

class EventoRecomendado(BaseModel):
    evento: Evento
    motivo: str


class ListEventoRecomendado(BaseModel):
    eventosRecomendados: List[EventoRecomendado]
# ---- FUNCION SCRAPER ----
def obtener_eventos(limit: int = 15) -> List[Evento]:
    url = "https://web.asdeporte.com/wp-json/wp/v2/posts"
    try:
        r = httpx.get(url, params={"page": 1, "per_page": limit, "_embed": 1})
        r.raise_for_status()
        data = r.json()
        return [
            Evento(
                id=e["id"],
                titulo=e["title"]["rendered"],
                content=e["content"]["rendered"],
                fecha=e["date"],
                link=e["link"],
                imagen=e.get("_embedded", {}).get("wp:featuredmedia", [{}])[0].get("source_url", "Sin imagen")
            )
            for e in data
        ]
    except Exception as e:
        raise RuntimeError(f"Error al obtener eventos: {str(e)}")

# ---- MCP TOOL ----
@mcp.tool()
def listar_eventos(cantidad: Optional[int] = 5) -> dict:
    """
    Devuelve los últimos eventos de AsDeporte como JSON estructurado.
    SOlo llamar a esta tool si no hay ninguna busqueda mas avanzada
    """
    eventos = obtener_eventos(cantidad)
    return {
        "type": "json",
        "data": [evento.model_dump() for evento in eventos]
    }
'''
@mcp.tool()
def buscar_eventos_por_keywords(keywords: List[str], limite: int = 10) -> dict:
    """
    Busca eventos cuyo título o descripción contenga alguna palabra clave.
    Prioriza coincidencias en el título. Solo usa la descripción si no se alcanza el límite.
    """
    todos = obtener_eventos(limit=50)

    en_titulo = [
        e for e in todos
        if any(k.lower() in e.titulo.lower() for k in keywords)
    ]

    if len(en_titulo) >= limite:
        seleccionados = en_titulo[:limite]
    else:
        # Agregamos los que matchean solo en content, pero no están ya en en_titulo
        faltan = limite - len(en_titulo)
        en_contenido = [
            e for e in todos
            if any(k.lower() in e.content.lower() for k in keywords)
            and e not in en_titulo
        ]
        seleccionados = en_titulo + en_contenido[:faltan]

    return {
        "type": "json",
        "data": [evento.model_dump() for evento in seleccionados]
    }
'''
llm = ChatOpenAI(model="gpt-4o")

llm_structured_evento = llm.with_structured_output(ListEventoRecomendado)
RECOMENDADOR_PROMPT = PromptTemplate.from_template("""
Estás ayudando a un atleta a encontrar un evento deportivo.
El atleta te dice: "{pregunta_usuario}"

A continuación tenés una lista de eventos disponibles con su título, fecha y ciudad. Elegí maximo 5 que mejor coincidan con su intención.

Eventos:
{eventos}

""")

@mcp.tool()
def recomendar_eventos_por_descripcion(pregunta: str) -> ListEventoRecomendado:
    """
    Recomienda eventos según una descripción natural del usuario.
    Devuelve cada evento más un motivo.
    """
    eventos = obtener_eventos()
    lista_eventos = [
        {
            "id": e.id,
            "titulo": e.titulo,
            "content": e.content,
            "fecha": e.fecha,
            "link": e.link,
            "imagen": e.imagen
        }
        for e in eventos
    ]

    prompt = RECOMENDADOR_PROMPT | llm_structured_evento
    respuesta = prompt.invoke({
        "pregunta_usuario": pregunta,
        "eventos": lista_eventos
    })
    
   # print(serializar_eventos_recomendados(respuesta.eventosRecomendados))
    return {
    "type": "json",
    "data": serializar_eventos_recomendados(respuesta.eventosRecomendados)
}

def serializar_eventos_recomendados(eventos: List[EventoRecomendado]) -> List[dict]:
    return [
        {
            "id": e.evento.id,
            "titulo": e.evento.titulo,
            "fecha": e.evento.fecha,
            "link": e.evento.link,
            "imagen": e.evento.imagen,
            "motivo": e.motivo
        }
        for e in eventos
    ]
# ---- EJECUCION ----
if __name__ == "__main__":
   #print(recomendar_eventos_por_descripcion("Me decis eeventos qeu tengo que ver con francia"))
    mcp.run(transport="stdio")
