from langchain_core.messages import HumanMessage,SystemMessage
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
load_dotenv()
import asyncio

model = init_chat_model("gpt-4o-mini",model_provider="openai")

async def run_agent(data:str):
   
    system_template = """
   
    You are a helpfull assistant and has to answe the user question:
   
        """

    promp_template = ChatPromptTemplate.from_messages(
        [("system",system_template),("user","{user_question}")]
    )
    prompt = promp_template.invoke({"user_question":data})
    response = await model.ainvoke(prompt)
    
    return response