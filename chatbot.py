from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory

from config import GROQ_API_KEY, GROQ_MODEL, SYSTEM_PROMPT
from utils.tools import REAL_ESTATE_TOOLS


def build_agent():
    """Build and return a simple LLM with tools."""
    
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model=GROQ_MODEL,
        temperature=0.3,
        max_tokens=2048,
    )

    # Create a simple prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT + "\n\nAvailable tools: " + str([tool.name for tool in REAL_ESTATE_TOOLS])),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ])

    # Create a simple chain
    chain = LLMChain(llm=llm, prompt=prompt)
    
    return chain


def get_response(chain, user_input: str, chat_history: list) -> str:
    """Get a response from the agent."""
    # Convert history to LangChain message format
    history_str = ""
    for msg in chat_history:
        if msg["role"] == "user":
            history_str += f"User: {msg['content']}\n"
        elif msg["role"] == "assistant":
            history_str += f"Assistant: {msg['content']}\n"

    try:
        result = chain.run(
            input=user_input,
            chat_history=history_str
        )
        return result
    except Exception as e:
        return f"I apologize, but I encountered an error: {str(e)}. Please try rephrasing your question."
