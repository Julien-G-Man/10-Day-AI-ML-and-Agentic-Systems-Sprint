from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from datetime import datetime

@tool
def get_current_year() -> int:
    """Get the current year."""
    return datetime.now().year

# Use a dummy API key for testing structural creation and input schema
llm = ChatOpenAI(model='gpt-4o-mini', api_key="dummy")
agent = create_agent(llm, [get_current_year])

# Check the input schema
print("Input schema:", agent.input_schema)
print("Input schema fields:", agent.input_schema.model_fields if hasattr(agent.input_schema, "model_fields") else "N/A")

try:
    # This will likely fail due to the dummy key, but it will confirm the input structure
    result = agent.invoke({"messages": [HumanMessage(content="What is the current year?")]})
    print("Success! Result:", result)
except Exception as e:
    print("Invocation failed (as expected with dummy key):", type(e).__name__)
