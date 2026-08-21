from typing import TypedDict, Annotated

from langchain_core.messages import BaseMessage , HumanMessage
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from dotenv import load_dotenv
import os 
import sqlite3
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
load_dotenv()
import requests

from langchain_google_genai import ChatGoogleGenerativeAI


class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


llm = ChatGoogleGenerativeAI(
    model='gemini-2.5-flash',
    google_api_key=os.environ['GEMINI_API_KEY']
)

search_tool = DuckDuckGoSearchRun(region="us-en")

@tool
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """
    Perform a basic arithmetic operation on two numbers.
    Supported operations: add, sub, mul, div
    """
    try:
        if operation == "add":
            result = first_num + second_num
        elif operation == "sub":
            result = first_num - second_num
        elif operation == "mul":
            result = first_num * second_num
        elif operation == "div":
            if second_num == 0:
                return {"error": "Division by zero is not allowed"}
            result = first_num / second_num
        else:
            return {"error": f"Unsupported operation '{operation}'"}
        
        return {"first_num": first_num, "second_num": second_num, "operation": operation, "result": result}
    except Exception as e:
        return {"error": str(e)}




# @tool
# def get_stock_price(symbol: str) -> dict:
#     """
#     Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA') 
#     using Alpha Vantage with API key in the URL.
#     """
#     url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=C9PE94QUEW9VWGFM"
#     r = requests.get(url)
#     return r.json()



tools = [search_tool, calculator]
llm_with_tools = llm.bind_tools(tools)

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