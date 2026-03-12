from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

from config import GROQ_API_KEY, GROQ_MODEL, SYSTEM_PROMPT


def build_agent():
    """Build and return a simple LLM instance."""
    
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model=GROQ_MODEL,
        temperature=0.3,
        max_tokens=2048,
    )

    return llm


def get_response(llm, user_input: str, chat_history: list) -> str:
    """Get a response from the LLM."""
    
    # Build conversation history
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    
    # Add chat history
    for msg in chat_history:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    
    # Add current user input
    messages.append({
        "role": "user", 
        "content": user_input
    })

    try:
        # Use direct LLM invocation
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        return f"I apologize, but I encountered an error: {str(e)}. Please try rephrasing your question."
