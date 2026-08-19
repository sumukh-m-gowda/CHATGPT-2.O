from typing import TypedDict, Annotated

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from dotenv import load_dotenv
import os 
import sqlite3
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI


class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


llm = ChatGoogleGenerativeAI(
    model='gemini-2.5-flash',
    google_api_key=os.environ['GEMINI_API_KEY']
)

def chat_node(state: ChatState):
    messages = state['messages']

    response = llm.invoke(messages)

    return {"messages": [response]}

conn = sqlite3.connect(database='chatbot.db' , check_same_thread=False)
checkpointer = SqliteSaver(conn = conn)

graph = StateGraph(ChatState)

graph.add_node("chat_node", chat_node)

graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

#list() can get u all the checkoints of particalar threadid 
# all_threads = set()
# for checks in checkpointer.list(None):
#     # print(checks)
#     all_threads.add(checks.config['configurable']['thread_id'])

# print(list(all_threads))

def retrieve_all_threads():
    all_threads = set()
    for checks in checkpointer.list(None):
    # print(checks)
            all_threads.add(checks.config['configurable']['thread_id'])

    return list(all_threads)