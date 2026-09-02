import os
from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage,HumanMessage,SystemMessage,AIMessage
from typing import TypedDict,Annotated
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from pydantic import BaseModel,Field
import operator
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

llm = ChatOpenAI(model= "gpt-5.6-luna")

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage],add_messages]

def chat_node(state:ChatState):
    messages=state["messages"]
    response=llm.invoke(messages)
    return {"messages":[response]}

checkpoint=MemorySaver()
graph=StateGraph(ChatState)

graph.add_node("chat_node",chat_node)

graph.add_edge(START,"chat_node")
graph.add_edge("chat_node",END)

chatbot=graph.compile(checkpointer=checkpoint)
chatbot

thread_id="1"
initial_state={"messages":[HumanMessage(content="What is RAG?")]}
config={"configurable":{"thread_id": thread_id}}
response=chatbot.invoke(initial_state,config=config)
response['messages'][-1].content

thread_id="1"
while True:
    user_message = input("Enter your query (or type 'exit' to stop): ").strip()
    if user_message.lower() in ["exit", "quit", "bye"]:
        print("Goodbye!")
        break
    if not user_message:
        continue
    print("User:", user_message)
    config={"configurable":{"thread_id": thread_id}}
    initial_state = {"messages": [HumanMessage(content=user_message)]}
    response = chatbot.invoke(initial_state, config=config)
    print("AI:", response["messages"][-1].content)
