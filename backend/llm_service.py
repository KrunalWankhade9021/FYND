import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# Fallback for development without keys
api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None

def generate_response(rating: int, review_text: str) -> str:
    """Generates a polite, personalized response to the user."""
    if not client:
        return "Thank you for your feedback! (AI integration not configured)"
    
    # Dynamic Persona based on rating
    tone = "deeply apologetic and humble" if rating < 4 else "warm, grateful, and enthusiastic"
    
    prompt = f"""
    You are a Senior Customer Success Manager at 'Fynd'. Your personality is {tone}.
    
    Task: Write a reply to a customer who gave a {rating}/5 star rating.
    Review: "{review_text}"
    
    Emoji Guide (Use 1-2 strictly based on meaning):
    - 🌟 / 🤩 : For 5-star praise (Excitement, Pride).
    - 🙏 / 🤝 : For gratitude and partnership.
    - 🥺 / 😔 : For apologies (Genuine regret).
    - 💪 / 🚀 : For commitment to improve (Action-oriented).
    - ❤️ : For warm connection.

    Guidelines:
    1. Be human and authentic.
    2. Reference specific details from the review.
    3. Length: Max 3 sentences.
    4. Sign-off: "Warmly, The Fynd Team".
    
    Response:
    """
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.7
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM Error (Response): {e}")
        return "Thank you for your valuable feedback."

def generate_admin_insights(rating: int, review_text: str):
    """Generates a structured summary and action plan for the admin."""
    if not client:
        return "Simulated Summary: User feedback.", "Simulated Action: Review manually."
    
    prompt = f"""
    Act as a Business Intelligence Analyst. Analyze this customer review.
    
    Data:
    - Rating: {rating}/5
    - Text: "{review_text}"
    
    Task:
    1. Summary: Condense the core sentiment and specific issue/praise into 1 concise sentence.
    2. Action: Recommend 1 specific, actionable step the team should take (max 5 words).
    
    Output Format (Strictly follow this):
    Summary: [Your summary here]
    Action: [Your bold action here]
    """
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.5
        )
        content = completion.choices[0].message.content.strip()
        
        # Robust Parsing
        summary = "Analysis failed."
        action = "Manual Review"
        
        lines = content.split('\n')
        for line in lines:
            if "Summary:" in line:
                summary = line.split("Summary:", 1)[1].strip()
            elif "Action:" in line:
                action = line.split("Action:", 1)[1].strip()
                
        return summary, action
    except Exception as e:
        print(f"LLM Error (Insights): {e}")
        return "Error analyzing review.", "Check logs."
