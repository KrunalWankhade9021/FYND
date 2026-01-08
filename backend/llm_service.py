import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# Fallback for development without keys
api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None

def generate_response(rating: int, review_text: str) -> str:
    """Generates a polite response to the user."""
    if not client:
        return "Thank you for your feedback! (AI integration not configured)"
    
    prompt = f"""
    You are a customer service AI. Write a short, polite response to a user who gave a {rating}/5 star rating.
    Review: "{review_text}"
    Response:
    """
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM Error (Response): {e}")
        return "Thank you for your valuable feedback."

def generate_admin_insights(rating: int, review_text: str):
    """Generates a summary and recommended action for the admin."""
    if not client:
        return "Simulated Summary: User feedback.", "Simulated Action: Review manually."
    
    prompt = f"""
    Analyze this customer review.
    Rating: {rating}/5
    Review: "{review_text}"
    
    Provide output in exactly this format:
    Summary: [A concise 1-sentence summary]
    Action: [A short 3-5 word recommended action]
    """
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
        )
        content = completion.choices[0].message.content.strip()
        
        # Simple parsing (robustness can be improved)
        summary = "No summary available."
        action = "Manual review."
        
        for line in content.split('\n'):
            if line.startswith("Summary:"):
                summary = line.replace("Summary:", "").strip()
            elif line.startswith("Action:"):
                action = line.replace("Action:", "").strip()
                
        return summary, action
    except Exception as e:
        print(f"LLM Error (Insights): {e}")
        return "Error analyzing review.", "Check logs."
