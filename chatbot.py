from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor
from langchain.agents.agent_toolkits import create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain.memory import ConversationBufferWindowMemory

from config import GROQ_API_KEY, GROQ_MODEL, SYSTEM_PROMPT
from utils.tools import REAL_ESTATE_TOOLS


def build_agent() -> AgentExecutor:
    """Build and return the LangChain ReAct agent."""

    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model=GROQ_MODEL,
        temperature=0.3,
        max_tokens=2048,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm=llm, tools=REAL_ESTATE_TOOLS, prompt=prompt)

    agent_executor = AgentExecutor(
        agent=agent,
        tools=REAL_ESTATE_TOOLS,
        verbose=False,
        max_iterations=5,
        handle_parsing_errors=True,
        return_intermediate_steps=False,
        llm=llm,
    )

    return agent_executor


def get_response(agent: AgentExecutor, user_input: str, chat_history: list) -> str:
    """Get a response from the agent."""
    # Convert history to LangChain message format
    lc_history = []
    for msg in chat_history:
        if msg["role"] == "user":
            lc_history.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            lc_history.append(AIMessage(content=msg["content"]))

    result = agent.invoke({
        "input": user_input,
        "chat_history": lc_history,
    })

    return result.get("output", "I'm sorry, I couldn't process that request.")
