# agent.py
import os
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.memory import InMemorySaver
from agents.agents import create_custom_react_agent


import json
import asyncio

load_dotenv()

# Crear modelo LLM y checkpointer en memoria
llm = ChatOpenAI()
checkpointer = InMemorySaver()


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
mcp_path = os.path.join(BASE_DIR, "mcp.json")
# Cargar configuración de servidores MCP
with open(mcp_path, "r") as f:
    servers_config = json.load(f)

# Crear cliente MCP
client = MultiServerMCPClient(servers_config)

# Obtener herramientas MCP (esto requiere async)
tools = asyncio.run(client.get_tools())
print("🔧 Tools cargadas:", [tool.name for tool in tools])

# Crear agente LangGraph con memoria

agent = create_custom_react_agent(llm,tools,checkpointer=checkpointer)


# Función pública para ejecutar el agente
async def run_agent(data: str):
    config = {"configurable": {"thread_id": "1"}}
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": data}]},
        config,
        
    )
    print("RESULT:",result)
    return result["messages"][-1]
