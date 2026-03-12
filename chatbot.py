import groq
from config import GROQ_API_KEY, GROQ_MODEL, SYSTEM_PROMPT


def build_agent():
    """Build and return a Groq client."""
    
    client = groq.Groq(api_key=GROQ_API_KEY)
    return client


def get_response(client, user_input: str, chat_history: list) -> str:
    """Get a response from the Groq API directly."""
    
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
        # Use direct Groq API call
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=2048,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"I apologize, but I encountered an error: {str(e)}. Please try rephrasing your question."
