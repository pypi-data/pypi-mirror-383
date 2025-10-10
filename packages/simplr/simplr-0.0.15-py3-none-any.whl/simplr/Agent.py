from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END, START

from operator import add as add_messages
from typing import List, Annotated, TypedDict

from .Config import get_config
from .CLI import CLI
from .System import get_system_prompt
from .Cache import Cache

import subprocess
import shlex
import os


os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"

class AgentState(TypedDict):
    messages: Annotated[List, add_messages]

@tool
def select_option(
    options: Annotated[List[str], "List of 1-3 possible commands that could complete the user's request."],
):
    """ Gets and runs user's choice from a list of 1-3 commands that could complete the user's request. """

    command = CLI.select("Possible commands:", options + ["Skip"], CLI.SELECT_DEFAULT_STYLE, prefixed=False)
    if command == "Skip":
        return {
            "command": "skipped",
            "result": "none"
        }
    if command.startswith("cd "):
        path = command[3:].strip()
        try:
            os.chdir(path)
            CLI.PREFIX = f"{os.getcwd()} >>>"
            return {
                "command": command,
                "result": "success"
            }
        except FileNotFoundError:
            print(f"Directory not found: {path}")
            return {
                "command": command,
                "result": "failed"
            }
    try:
        result = subprocess.run(command, shell=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print("An exception occured.")
        print(e)
        return {
            "command": command,
            "result": e
        }
    except KeyboardInterrupt:
        print("Keyboard interrupt.")
        return {
            "command": command,
            "result": "keyboard interrupt"
        }

    return {
        "command": command,
        "result": str(result),
    }

def get_input(state: AgentState):

    command = CLI.ask("", CLI.ASK_DEFAULT_STYLE, check=False)
    return { "messages": [HumanMessage(content=command)] }


TOOLS: List = [select_option]
TOOL_DICT: dict = { tool.name : tool for tool in TOOLS }
CONFIG = get_config()
LLM = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=CONFIG.google_api_key).bind_tools(TOOLS)
SYSTEM_PROMPT = get_system_prompt()

def call(state: AgentState):

    command = state["messages"][-1].content
    if command.startswith("cd "):
        path = command[3:].strip()
        try:
            os.chdir(path)
            CLI.PREFIX = f"{os.getcwd()} >>>"
            global SYSTEM_PROMPT
            SYSTEM_PROMPT = get_system_prompt(os.getcwd())
            return { "messages": [HumanMessage(content=f"Command Called: {command} Result: success")] }
        except FileNotFoundError:
            print(f"Directory not found: {path}")
            return { "messages": [HumanMessage(content=f"Command Called: {command} Result: failed")] }

    try:
        result = subprocess.run(command, shell=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print("An exception occured.")
        print(e)
        return { "messages": [HumanMessage(content=f"Command Called: {command} Result: {e}")] }
    except KeyboardInterrupt:
        print("Keyboard interrupt.")
        return { "messages": [HumanMessage(content=f"Command Called: {command} Result: keyboard interrupt")] }

    return { "messages": [HumanMessage(content=f"Command Called: {command} Result: {str(result)}")] }

def call_llm(state: AgentState):
    try:
        with CLI.CONSOLE.status("Finding commands...", spinner="dots", spinner_style="bold cyan"):
            messages = state['messages']
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
            response = LLM.invoke(messages)
    except Exception as e:
        print("An exception occurred: ", e)
        return { "messages": [] }
    return { "messages": [response] }

def should_call_llm(state: AgentState):

    message = state["messages"][-1].content
    if message == "exit":
        return "exit"
    
    args = message.split(" ")
    if args[0] == "simplr" and len(args) > 1 and args[1] == ">":
        return "llm"
    elif args[0] == "simplr":
        return "continue"
    else:
        return "call_"
    
def print_messages(state: AgentState):

    CLI.CONSOLE.print("\n[dim white]Call the LLM with [#047F80]simplr > \"REQUEST\"[/#047F80].[/dim white]")
    CLI.CONSOLE.print("[dim white]Exit with [#047F80]exit[/#047F80].[/dim white]\n")

    return { "messages": [] }
    
    
def load_cache(state: AgentState):

    if not CONFIG.cache_chats:
        return { "messages": [] }

    cached = Cache.get()
    return { "messages": cached + [state["messages"][-1]] if len(state["messages"]) > 0 else []}

def cache(state: AgentState):

    if not CONFIG.cache_chats:
        return { "messages": [] }

    Cache.cache(state)

    
def has_tools(state: AgentState):

    result = state['messages'][-1]
    return "True" if hasattr(result, 'tool_calls') and len(result.tool_calls) > 0 else "False"

def invalid_call(state: AgentState):
    print("No possible commands were found.")
    return { "messages": [] }
    
def tool_node(state: AgentState):
    
    tool_call = state["messages"][-1].tool_calls[0]
    tool = TOOL_DICT.get(tool_call["name"])

    if tool:
        result = TOOL_DICT[tool_call["name"]].invoke({ "options": tool_call["args"].get("options", []) })
        if result["command"].startswith("cd "):
            Cache.cache(state, path=os.path.abspath(os.path.join(os.getcwd(), os.pardir)))
        return { "messages": [HumanMessage(content=f"Command Called: {result["command"]} Result: {result["result"]}")]}
    else:
        return { "messages": [SystemMessage(content="Invalid tool call.")] }

def create_and_run_cli():

    graph: StateGraph = StateGraph(AgentState)

    graph.add_node("print_messages", print_messages)
    graph.add_node("get_input", get_input)
    graph.add_node("call_llm", call_llm)
    graph.add_node("tool_node", tool_node)
    graph.add_node("call_node", call)
    graph.add_node("load_cache", load_cache)
    graph.add_node("cache", cache)
    graph.add_node("invalid_call", invalid_call)

    graph.add_edge(START, "print_messages")
    graph.add_edge("print_messages", "load_cache")
    graph.add_edge("load_cache", "get_input")
    graph.add_conditional_edges(
        "get_input",
        should_call_llm,
        {
            "exit": "cache",
            "call_": "call_node",
            "llm": "call_llm",
            "continue": "get_input"
        }
    )
    graph.add_conditional_edges(
        "call_llm",
        has_tools,
        {
            "True": "tool_node",
            "False": "invalid_call"
        }
    )
    graph.add_edge("invalid_call", "get_input")
    graph.add_edge("tool_node", "get_input")
    graph.add_edge("call_node", "get_input")
    graph.add_edge("cache", END)

    agent = graph.compile()

    agent.invoke({"messages": []}, { "recursion_limit": 1028 })

def create_and_run_agent(input: str):

    graph: StateGraph = StateGraph(AgentState)

    graph.add_node("call_llm", call_llm)
    graph.add_node("tool_node", tool_node)
    graph.add_node("call_node", call)
    graph.add_node("load_cache", load_cache)
    graph.add_node("cache", cache)
    graph.add_node("invalid_call", invalid_call)

    graph.add_edge(START, "load_cache")
    graph.add_conditional_edges(
        "load_cache",
        should_call_llm,
        {
            "exit": "cache",
            "call_": "call_node",
            "llm": "call_llm",
        }
    )
    graph.add_conditional_edges(
        "call_llm",
        has_tools,
        {
            "True": "tool_node",
            "False": "invalid_call"
        }
    )
    graph.add_edge("invalid_call", END)
    graph.add_edge("tool_node", END)
    graph.add_edge("call_node", END)
    graph.add_edge("cache", END)

    agent = graph.compile()
    agent.invoke({"messages": [HumanMessage(content="simplr > " + input)]}, { "recursion_limit": 256 })