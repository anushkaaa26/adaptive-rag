"""
ReAct agent setup: wires up the retriever and web search as tools for a
reasoning-and-acting agent, used as an alternative entry point to the
adaptive graph for more open-ended, multi-step queries.
"""
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import Tool

from src.config.settings import settings
from src.llms.groq_llm import get_llm
from src.rag.retriever_setup import get_retriever
from src.tools.common_tools import load_prompts, format_docs
from src.core.logger import get_logger

logger = get_logger(__name__)
_prompts = load_prompts()

_REACT_TEMPLATE = """{system_prompt}

You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}
"""


def _retrieve_tool_fn(query: str) -> str:
    docs = get_retriever().invoke(query)
    return format_docs(docs)


def _web_search_tool_fn(query: str) -> str:
    search = TavilySearchResults(k=4, tavily_api_key=settings.TAVILY_API_KEY)
    results = search.invoke({"query": query})
    if isinstance(results, list):
        return "\n\n".join(r.get("content", "") for r in results)
    return str(results)


def build_react_agent() -> AgentExecutor:
    tools = [
        Tool(
            name="document_retriever",
            func=_retrieve_tool_fn,
            description="Search the user's uploaded documents for relevant information.",
        ),
        Tool(
            name="web_search",
            func=_web_search_tool_fn,
            description="Search the web for real-time or current information.",
        ),
    ]

    llm = get_llm()
    prompt = PromptTemplate.from_template(_REACT_TEMPLATE).partial(
        system_prompt=_prompts["system_prompt"]
    )
    agent = create_react_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
