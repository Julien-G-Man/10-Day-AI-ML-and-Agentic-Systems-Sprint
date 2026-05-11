# app/agent.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_classic.memory import ConversationBufferWindowMemory
from langchain_core.messages import HumanMessage
from app.tools.satellite_tools import lookup_satellite_database, calculate_orbital_params
from app.tools.search_tools import web_search, search_satellite_news
from app.tools.report_tools import compile_satellite_report

load_dotenv()

AGENT_SYSTEM_PROMPT = '''You are an expert satellite intelligence analyst.
Your job: produce comprehensive, accurate intelligence reports about satellites.

WORKFLOW (follow this order):
1. Look up the satellite in the internal database FIRST
2. Calculate orbital mechanics if needed
3. Search for recent news about the satellite
4. Compile everything into a report using compile_satellite_report

RULES: - Always use compile_satellite_report as your FINAL action - Never make up data — only use information from tool results - If a satellite is not in the database, say so and search the web for info - Be concise but complete'''

class AgentRunner:
    def __init__(self, agent, memory, verbose: bool = False):
        self.agent = agent
        self.memory = memory
        self.verbose = verbose

    def invoke(self, input_dict):
        # support {'input': 'text'} for backwards compatibility
        user_text = input_dict.get('input') if isinstance(input_dict, dict) else str(input_dict)
        # build messages including memory
        mem_vars = self.memory.load_memory_variables({})
        chat = mem_vars.get('chat_history')
        messages = []
        if chat:
            if isinstance(chat, list):
                messages.extend(chat)
            else:
                messages.append(HumanMessage(content=str(chat)))
        messages.append(HumanMessage(content=user_text))

        result = self.agent.invoke({'messages': messages})
        assistant_msg = result['messages'][-1].content
        try:
            self.memory.save_context({'input': user_text}, {'output': assistant_msg})
        except Exception:
            pass
        return {'messages': result['messages'], 'output': assistant_msg, 'raw': result}


def build_satellite_agent(verbose: bool = False):
    tools = [
        lookup_satellite_database,
        calculate_orbital_params,
        web_search,
        search_satellite_news,
        compile_satellite_report,
    ]
    llm = ChatOpenAI(model='gpt-4o-mini', temperature=0, api_key=os.getenv('OPENAI_API_KEY'))

    # Memory buffer
    memory = ConversationBufferWindowMemory(k=6, memory_key='chat_history', return_messages=True)

    # Create agent using a system prompt; avoid using deprecated hub.pull
    agent = create_agent(llm, tools, system_prompt=AGENT_SYSTEM_PROMPT, debug=verbose)

    return AgentRunner(agent, memory, verbose=verbose)

# Test from command line
if __name__ == '__main__':
    executor = build_satellite_agent(verbose=True)
    result = executor.invoke({'input': 'Generate a complete intelligence report on the James Webb Space Telescope.'})
    print('\n=== FINAL REPORT ===')
    print(result['output'])
