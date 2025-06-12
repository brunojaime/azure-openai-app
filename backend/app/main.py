from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import asyncio
from agent import run_agent
app = FastAPI()

class QueryInput(BaseModel):
    query : str



@app.get("/joke")
async def query(data: str,number_of_jokes:int):
    response = await run_agent(data,number_of_jokes)
    return response


if __name__=="__main__":
    uvicorn.run(app,host="0.0.0.0",port=8010)