from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import asyncio
from agent import run_agent
app = FastAPI()

class Pregunta(BaseModel):
    data: str



@app.post("/consulta")
async def query(pregunta: Pregunta):
    print(f"📥 Recibida pregunta: {pregunta.data}")
    response = await run_agent(pregunta.data)
    print("📤 Respuesta del agente:", response.content)
    
    return {"respuesta": response.content}


if __name__=="__main__":
    uvicorn.run(app,host="0.0.0.0",port=8010)

    