import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import HumanMessage

load_dotenv()

# ── Define the LLM (the agent's brain) ────────────────────
llm = ChatOpenAI(
    model='gpt-4o-mini',
    temperature=0,
    api_key=os.getenv('OPENAI_API_KEY'),
)


# ── Define tools (functions the agent can call) ───────────
@tool
def add_numbers(a: float, b: float) -> float:
    """Add two numbers together. Use when you need to compute a sum."""
    return a + b


@tool
def multiply_numbers(a: float, b: float) -> float:
    """Multiply two numbers. Use when you need to compute a product."""
    return a * b


@tool
def get_current_year() -> int:
    """Get the current year. Use when the calculation involves the current year."""
    from datetime import datetime
    return datetime.now().year


"""
# Wrap plain functions as langchain `Tool` objects so the agent will actually execute them
tools = [
    Tool.from_function(add_numbers, name="add_numbers", description="Add two numbers together."),
    Tool.from_function(multiply_numbers, name="multiply_numbers", description="Multiply two numbers."),
    Tool.from_function(get_current_year, name="get_current_year", description="Return the current year."),
]
"""

tools = [add_numbers, multiply_numbers, get_current_year]

# ── Create the agent ───────────────────────────────────────
# create_agent wires together: LLM + tools with native tool-calling
# (no custom prompt needed - the agent handles tool invocation automatically)
agent = create_agent(llm, tools, debug=False)

# ── Run the agent ─────────────────────────────────────────
result = agent.invoke({'messages': [HumanMessage(content='What is 37 multiplied by 48, then add 2025 minus the current year?')]})
print('\nFINAL ANSWER:', result['messages'][-1].content)
