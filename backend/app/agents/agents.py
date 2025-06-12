from langgraph.graph import END, START, StateGraph, MessagesState
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
from typing import Annotated, Literal, TypedDict

def router_definition(state:MessagesState) -> Literal['tools',END]:
    messages = state['messages']

    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END



def create_custom_react_agent(llm : ChatOpenAI,tools,checkpointer):
    workflow = StateGraph(MessagesState)
    llm_with_tools = llm.bind_tools(tools)

    tool_node = ToolNode(tools)

    def call_model(state:MessagesState):
        messages = state['messages']
        response = llm_with_tools.invoke(messages)
        return {"messages":[response]}


    workflow.add_node("agent",call_model)
    workflow.add_node("tools",tool_node)

    workflow.add_edge(START,"agent")
    workflow.add_conditional_edges("agent",router_definition,{"tools":"tools",END:END})

    app = workflow.compile()

    return app