from langchain_core.messages import HumanMessage,SystemMessage
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
load_dotenv()
import asyncio

model = init_chat_model("gpt-4o-mini",model_provider="openai")

async def run_agent(data:str, count: int):
    
    system_template = "Tell me {count} a jokes about {story_theme}"

    promp_template = ChatPromptTemplate.from_messages(
        [("system",system_template),("user","{count}")]
    )
    prompt = promp_template.invoke({"story_theme":data,"count":count})
    response = await model.ainvoke(prompt)
    return response