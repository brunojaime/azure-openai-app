from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import asyncio
from agent import run_agent
import tempfile
from document_intelligence import analizar_documento_azure

app = FastAPI()

class Pregunta(BaseModel):
    data: str



@app.post("/consulta")
async def query(pregunta: Pregunta):
    print(f"📥 Recibida pregunta: {pregunta.data}")
    response = await run_agent(pregunta.data)
    print("📤 Respuesta del agente:", response.content)
    
    return {"respuesta": response.content}


@app.post("/analizar_documento")
async def analizar_documento(file: UploadFile = File(...)):
    try:
        print(f"[INFO] Recibido archivo: {file.filename}")

        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}") as tmp:
            file_bytes = await file.read()
            tmp.write(file_bytes)
            tmp_path = tmp.name

        print(f"[INFO] Archivo guardado temporalmente en: {tmp_path}")

        resultado = analizar_documento_azure(tmp_path)

        print(f"[INFO] Resultado de análisis: {resultado}")

        return JSONResponse(content=resultado)

    except Exception as e:
        print(f"[ERROR] Falló el análisis del documento: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__=="__main__":
    uvicorn.run(app,host="0.0.0.0",port=8010)

    