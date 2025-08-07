from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import google.generativeai as genai
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Medical Assistant API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173", "http://127.0.0.1:5174"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Google Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY not found in environment variables. Please set it in .env file.")
    
genai.configure(api_key=GEMINI_API_KEY)

# Initialize the Gemini model
model = genai.GenerativeModel('gemini-pro')

# In-memory conversation storage
conversations: Dict[str, List[Dict]] = {}

class MessageHistory(BaseModel):
    content: str
    isUser: bool

class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[MessageHistory]] = []
    session_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    response: str

def create_medical_prompt(user_message: str, conversation_history: List[MessageHistory]) -> str:
    """Create a comprehensive prompt for the medical assistant"""
    
    system_prompt = """You are a professional medical assistant AI. Your role is to provide helpful, accurate, and compassionate medical information while maintaining strict safety guidelines.

CORE RESPONSIBILITIES:
1. Provide clear, step-by-step first aid instructions and precautions when asked
2. Suggest immediate relief actions for common ailments
3. Explain medical conditions, symptoms, and their common causes
4. Offer moral support and ask relevant follow-up questions
5. Guide users appropriately when professional medical care is needed

SAFETY GUARDRAILS (CRITICAL):
- NEVER provide specific diagnoses, prescriptions, or personalized medical advice
- ALWAYS recommend calling emergency services (911) for medical emergencies
- If symptoms suggest serious conditions, immediately advise seeking professional medical attention
- State your limitations clearly when queries are outside your scope
- Emphasize that you provide general information only, not medical advice

COMMUNICATION STYLE:
- Be warm, empathetic, and professional
- Use clear, simple language that's easy to understand
- After providing information, offer emotional support
- Ask one thoughtful follow-up question to better understand their situation
- Show genuine care and concern for their wellbeing

EMERGENCY INDICATORS:
If the user mentions any of these, immediately recommend emergency services:
- Chest pain, difficulty breathing, severe bleeding
- Loss of consciousness, severe head injury
- Signs of stroke, severe allergic reactions
- Suicidal thoughts or severe mental health crisis
- Severe burns, broken bones, or major trauma

Remember: You are a supportive medical information resource, not a doctor. Always prioritize user safety."""

    # Build conversation context
    context = ""
    if conversation_history:
        context = "\n\nPrevious conversation:\n"
        for msg in conversation_history[-6:]:  # Last 6 messages for context
            role = "User" if msg.isUser else "Assistant"
            context += f"{role}: {msg.content}\n"
    
    full_prompt = f"{system_prompt}{context}\n\nUser's current message: {user_message}\n\nPlease respond as a caring medical assistant, following all the guidelines above:"
    
    return full_prompt

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Medical Assistant API is running", "status": "healthy"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint for medical assistance"""
    
    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=500, 
            detail="Server configuration error. Please contact administrator."
        )
    
    try:
        # Create the prompt with conversation context
        prompt = create_medical_prompt(request.message, request.conversation_history)
        
        logger.info(f"Processing chat request for session: {request.session_id}")
        
        # Generate response using Gemini
        response = model.generate_content(prompt)
        
        if not response.text:
            raise HTTPException(
                status_code=500,
                detail="Unable to generate response. Please try again."
            )
        
        # Store conversation in memory (optional, for session management)
        if request.session_id not in conversations:
            conversations[request.session_id] = []
        
        conversations[request.session_id].extend([
            {"content": request.message, "isUser": True},
            {"content": response.text, "isUser": False}
        ])
        
        # Keep only last 20 messages per session to manage memory
        if len(conversations[request.session_id]) > 20:
            conversations[request.session_id] = conversations[request.session_id][-20:]
        
        return ChatResponse(response=response.text)
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        
        # Check if it's a Gemini API error
        if "API_KEY" in str(e).upper():
            error_message = "I'm having trouble connecting to my knowledge base. Please check the API configuration."
        elif "QUOTA" in str(e).upper() or "RATE_LIMIT" in str(e).upper():
            error_message = "I'm currently experiencing high traffic. Please try again in a moment."
        else:
            error_message = "I apologize, but I'm having technical difficulties right now. Please try again later, and if this is an emergency, please contact emergency services immediately."
        
        return ChatResponse(response=error_message)

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "api_configured": bool(GEMINI_API_KEY),
        "active_sessions": len(conversations)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
