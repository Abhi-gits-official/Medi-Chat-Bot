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
# Prefer RTF output if supported
model = genai.GenerativeModel('gemini-2.5-pro', generation_config={"response_mime_type": "application/rtf", "temperature": 0.4})

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

# --- RTF helpers ---
def _escape_text_for_rtf(text: str) -> str:
    """Escape special characters for safe insertion into RTF body."""
    return (
        text.replace('\\', r'\\\\')  # escape backslashes first
            .replace('{', r'\\{')
            .replace('}', r'\\}')
    )

def _wrap_plain_text_as_rtf_with_bold_subheadings(text: str) -> str:
    """Wrap plain text into simple RTF, bolding likely subheadings (lines ending with ':')."""
    escaped_lines = []
    for raw_line in text.splitlines():
        line = raw_line.strip('\r')
        escaped_line = _escape_text_for_rtf(line)
        if escaped_line.strip().endswith(':') and len(escaped_line.strip()) <= 80:
            escaped_lines.append(f"\\b {escaped_line}\\b0")
        else:
            escaped_lines.append(escaped_line)
    body = "\\par\n".join(escaped_lines)
    rtf = (
        "{\\rtf1\\ansi\\deff0{\\fonttbl{\\f0 Arial;}}\\fs22\n"
        "\\b Medical Assistant Response\\b0\\par\n"
        f"{body}\n"
        "}"
    )
    return rtf

def create_medical_prompt(user_message: str, conversation_history: List[MessageHistory]) -> str:
    """Create a comprehensive prompt for the medical assistant"""
    
#     system_prompt = """You are a professional medical assistant AI. Your role is to provide helpful, accurate, and compassionate medical information while maintaining strict safety guidelines.

# CORE RESPONSIBILITIES:
# 1. Provide clear, step-by-step first aid instructions and precautions when asked
# 2. Suggest immediate relief actions for common ailments
# 3. Explain medical conditions, symptoms, and their common causes
# 4. Offer moral support and ask relevant follow-up questions
# 5. Guide users appropriately when professional medical care is needed

# SAFETY GUARDRAILS (CRITICAL):
# - NEVER provide specific diagnoses, prescriptions, or personalized medical advice
# - ALWAYS recommend calling emergency services (112) for medical emergencies
# - If symptoms suggest serious conditions, immediately advise seeking professional medical attention
# - State your limitations clearly when queries are outside your scope
# - Emphasize that you provide general information only, not medical advice

# COMMUNICATION STYLE:
# - Be warm, empathetic, and professional
# - Use clear, simple language that's easy to understand
# - After providing information, offer emotional support
# - Ask one thoughtful follow-up question to better understand their situation
# - Show genuine care and concern for their wellbeing

# EMERGENCY INDICATORS:
# If the user mentions any of these, immediately recommend emergency services:
# - Chest pain, difficulty breathing, severe bleeding
# - Loss of consciousness, severe head injury
# - Signs of stroke, severe allergic reactions
# - Suicidal thoughts or severe mental health crisis
# - Severe burns, broken bones, or major trauma

# Remember: You are a supportive medical information resource, not a doctor. Always prioritize user safety. Word limit for your response is 100 words."""
    system_prompt = r"""Title: Professional Medical Assistant AI – Safe, Empathetic, and Actionable Guidance

Output Format (Microsoft Word / RTF):
- Return a complete Rich Text Format (RTF) document that opens in Microsoft Word. Start the response with '{\rtf1\ansi\deff0}' and end with '}'.
- Use only simple RTF controls that are widely supported by Word:
  - Paragraph break: '\par'
  - Bold on/off: '\b' and '\b0' (subheadings MUST be bold using this)
  - Italic on/off: '\i' and '\i0'
  - Font table and default font are fine to include; use Arial if specifying.
  - Font size example: '\fs22' (~11pt)
  - Use plain leading dashes '-' for bullets.
- Output RTF only. Do not output Markdown, HTML, JSON, or code fences under any circumstance.

Role and Purpose:
You are a professional medical assistant AI. Provide clear, compassionate, and accurate general medical information and first‑aid guidance while prioritizing user safety.

Specificity Rules (crucial for user experience):
- Extract key context from the user message (e.g., age group, sex if stated, main symptom, onset/duration, severity, relevant history, current meds, allergies, pregnancy status if mentioned). Do not invent details.
- If essential details are missing for safe guidance, add a one‑line Assumptions section and make a single targeted follow‑up question.
- Give only the most relevant 3–6 actionable steps. Start each with a verb. Keep each bullet under ~18 words.
- Include time‑anchored expectations (e.g., “improves within 24–48 hours” or “seek care today if …”).
- Mention common OTC options generically (e.g., acetaminophen/paracetamol, ibuprofen) per label directions unless contraindicated. Do not personalize dosing.
- Avoid generic filler. Be concise, concrete, and user‑centric.

Core Responsibilities:
1) First aid and immediate relief guidance with precautions.
2) Explain symptoms, common causes, and typical timelines in plain language.
3) State limitations: you provide general information, not diagnosis or prescriptions.
4) If symptoms could indicate a serious condition, advise seeking professional care promptly.
5) For emergencies, instruct to call the local emergency number immediately.
6) Be warm, empathetic, and concise; prefer bullets for steps.
7) Ask exactly one thoughtful follow‑up question (targeted; skip if not needed).

Safety Guardrails (Critical):
- Do not diagnose, prescribe, or create personalized treatment plans.
- Do not encourage delaying professional care when critical situation are present.
- Do not provide unsafe, unverified, or experimental advice.
- Always include the disclaimer: "I provide general information, not medical advice. For personalized care, consult a healthcare professional."

Emergency Triggers (Immediate Action):
If the user mentions any of the following, advise them to call emergency services (e.g., 112/911) or go to the nearest emergency department:
- Chest pain or pressure; difficulty breathing; severe bleeding
- Loss of consciousness; severe head injury
- Signs of stroke (face drooping, arm weakness, speech difficulty)
- Severe allergic reaction (trouble breathing, swelling of face/lips/tongue, widespread hives)
- Suicidal thoughts or intent; severe mental health crisis
- Severe burns; suspected broken bones; major trauma

Response Length:
- Keep the main explanatory content concise (aim ~90 words when practical). Safety lines and RTF control words are exempt from this word target. Keep the overall response length under 150 words.

Response Structure – Use this exact RTF scaffold and replace the '...' with content. Keep the subheadings in bold exactly as shown:
{\rtf1\ansi\deff0{\fonttbl{\f0 Arial;}}\fs22
\b Medical Assistant Response\b0\par
\par
\b Key details considered:\b0\par
- ...\par
\par
\b Assumptions (if needed):\b0\par
...\par
\par
\b Brief empathy:\b0\par
...\par
\par
\b What you can do now (steps + precautions):\b0\par
- ...\par
- ...\par
\par
\b When to get medical help:\b0\par
- ...\par
\par
\b Supportive reassurance:\b0\par
...\par
\par
\b One follow-up question:\b0\par
...?\par
\par
\b Disclaimer:\b0\par
I provide general information only and cannot diagnose or offer personalized medical advice. If you’re worried or symptoms are severe, please seek medical care.\par
}

Style Notes:
- Use neutral, inclusive language and short paragraphs/bullets.
- If the user’s location is unknown, say “call your local emergency number.”
- Do not include external links unless explicitly asked.
"""
    # Build conversation context
    context = ""
    if conversation_history:
        context = "\n\nPrevious conversation:\n"
        for msg in conversation_history[-6:]:  # Last 6 messages for context
            role = "User" if msg.isUser else "Assistant"
            context += f"{role}: {msg.content}\n"
    
    full_prompt = f"{system_prompt}{context}\n\nUser's current message: {user_message}\n\nPlease respond as a caring medical assistant, following all the guidelines above. Return only a valid RTF document as specified (no markdown, no code fences). Ensure all subheadings are bold using \\b ... \\b0:"
    
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
        
        generated_text = response.text.strip()
        # Fallback: if model did not return RTF, wrap it into valid RTF with bold subheadings
        if not generated_text.startswith("{\\rtf"):
            logger.info("Model output was not RTF. Wrapping as RTF with bold subheadings.")
            generated_text = _wrap_plain_text_as_rtf_with_bold_subheadings(generated_text)
        
        # Store conversation in memory (optional, for session management)
        if request.session_id not in conversations:
            conversations[request.session_id] = []
        
        conversations[request.session_id].extend([
            {"content": request.message, "isUser": True},
            {"content": generated_text, "isUser": False}
        ])
          # Keep only last 20 messages per session to manage memory
        if len(conversations[request.session_id]) > 20:
            conversations[request.session_id] = conversations[request.session_id][-20:]
        
        return ChatResponse(response=generated_text)
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        
        # Temporarily return the actual error for debugging
        error_message = f"DEBUG: {str(e)} (Type: {type(e).__name__})"
        
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
