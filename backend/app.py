import os
import json
import google.generativeai as genai
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Aura AI Engine",
    description="Scalable backend API for Aura dating assistant. Powered by Google Gemini Generative AI.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONFIGURATION ---
# Configure Google Gemini API
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY is missing in .env file")

genai.configure(api_key=api_key)

# Using 'gemini-2.5-flash' for speed and cost-efficiency.
model = genai.GenerativeModel('gemini-2.5-flash')


# --- DATA MODELS ---
class MatchResponse(BaseModel):
    score: int
    title: str
    description: str
    red_flags: List[str]
    green_flags: List[str]
    verdict: str

# --- RIZZ FEATURE MODELS ---

class RizzOption(BaseModel):
    text: str
    explanation: str 

class RizzResponse(BaseModel):
    image_analysis: str
    options: List[RizzOption]
    
# --- ARGUMENT JUDGE MODEL ---
class ArgumentResponse(BaseModel):
    winner: str 
    score: int
    analysis: str 
    winning_point: str 
    weak_point: str
    advice: str 

# --- CHAT REPLY MODELS ---
class ReplyOption(BaseModel):
    tone: str 
    text: str 
    explanation: str 

class ChatReplyResponse(BaseModel):
    analysis: str 
    replies: List[ReplyOption]

# --- ENDPOINTS ---

@app.get("/")
def read_root():
    """Health check endpoint to ensure the API is running."""
    return {"status": "Aura Backend is running!", "docs_url": "/docs"}


@app.post("/check-aura", response_model=MatchResponse)
async def check_aura(
        me: UploadFile = File(...),
        target: UploadFile = File(...),
        language: str = Query("Turkish", description="Output language (e.g., English, Turkish, Spanish)")
):
    """
    Analyzes two uploaded images (User vs Target) to determine visual compatibility and vibe.
    Returns a JSON object with a score, verdict, and constructive feedback.
    """
    try:
        # Read image files as bytes
        me_bytes = await me.read()
        target_bytes = await target.read()

        # System Prompt for the AI
        prompt = f"""
                You are a brutally honest but constructive dating coach and vibe analyst. 
                Analyze these two people based on their visual "aura", style, grooming, and context.

                IMPORTANT: PROVIDE THE ENTIRE OUTPUT IN {language.upper()} LANGUAGE.

                Person 1 is the USER. Person 2 is the TARGET.

                Task: Determine if Person 2 would be interested in Person 1 based on visual compatibility.

                Rules:
                1. Be realistic. If styles clash, point it out.
                2. Do NOT be mean about genetics. Focus on "Vibe", "Style", "Effort".
                3. Give a compatibility score (0-100).
                4. Output strictly in JSON.

                JSON Structure (Translate values to {language}):
                {{
                    "score": 75,
                    "title": "Short catchy title in {language}",
                    "description": "2-3 sentences explaining the dynamic in {language}.",
                    "red_flags": ["List 2 potential clashes in {language}"],
                    "green_flags": ["List 2 matching points in {language}"],
                    "verdict": "Direct answer in {language} (e.g., 'Yes, likely', 'No')"
                }}
                """

        # Prepare content for Gemini (Multimodal: Text + Image + Image)
        content = [
            prompt,
            {"mime_type": "image/jpeg", "data": me_bytes},
            {"mime_type": "image/jpeg", "data": target_bytes}
        ]

        # Generate response
        response = await model.generate_content_async(content)

        # Clean up JSON string (remove markdown code blocks if present)
        cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
        result = json.loads(cleaned_text)

        return result

    except Exception as e:
        print(f"Error during analysis: {e}")
        raise HTTPException(status_code=500, detail="Aura analysis failed. Please try again.")


@app.post("/generate-rizz", response_model=RizzResponse)
async def generate_rizz(
        image: UploadFile = File(...),
        extra_context: str = "Make it impressive but casual.",
        language: str = Query("Turkish", description="Target language")
):
    """
    Analyzes an Instagram story screenshot and generates conversation starters (Rizz lines).
    """
    try:
        image_bytes = await image.read()

        # System Prompt: The "Rizz God" Persona
        prompt = """
                You are a world-class social dynamics expert. 
                Generate 3 DISTINCT "replies" to this Instagram Story, all matching the same vibe.

                TARGET LANGUAGE: {lang_upper}
                REQUIRED VIBE/CONTEXT: {context}

                Step 1: Analyze the image.
                Step 2: Generate 3 DIFFERENT opening lines in {lang}. 
                ALL lines must strictly follow the requested vibe: "{context}".

                CRITICAL CULTURAL INSTRUCTION:
                - Use natural slang, humor, and dating culture of {lang}.
                - NO generic "Hello".
                - If {lang} is Turkish, use natural phrases like "Oha", "Yok artık", "Şaka mı".

                Return strictly JSON:
                {{
                    "image_analysis": "Brief description in {lang}",
                    "options": [
                        {{ "text": "First variation of {context} line", "explanation": "Short reason" }},
                        {{ "text": "Second variation of {context} line", "explanation": "Short reason" }},
                        {{ "text": "Third variation of {context} line", "explanation": "Short reason" }}
                    ]
                }}
                """.format(
                    lang_upper=language.upper(), 
                    context=extra_context, 
                    lang=language
                )
         
        content = [prompt, {"mime_type": "image/jpeg", "data": image_bytes}]
        response = await model.generate_content_async(content)

        # Clean up JSON
        cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
        result = json.loads(cleaned_text)

        return result

    except Exception as e:
        print(f"Rizz generation error: {e}")
        raise HTTPException(status_code=500, detail="Rizz machine broken. Try again.")

@app.post("/judge-argument", response_model=ArgumentResponse)
async def judge_argument(
    image: UploadFile = File(...),
    context: str = "This is a chat with my partner.",
    language: str = Query("Turkish", description="Output language")
):
    """
    Analyzes a chat screenshot to determine who is winning the argument.
    Provides tactical advice and logical fallacy detection.
    """
    try:
        image_bytes = await image.read()

        prompt = f"""
        You are an expert Debate Judge and Psychologist specializing in conflict resolution and manipulation detection.
        Analyze this chat screenshot provided by the user.
        
        TARGET LANGUAGE: {language.upper()}
        
        Task:
        1. Identify the two parties (Sender vs Receiver).
        2. Determine who is currently "winning" the argument based on logic, emotional control, and leverage.
        3. Identify any logical fallacies (gaslighting, strawman, ad hominem).
        4. Provide a tactical advice for the user to turn the tables or end the argument.
        
        Output strictly in JSON format (Translate all values to {language}):
        {{
            "winner": "Name/Side who is winning (e.g. 'Grey Bubbles' or 'The Partner')",
            "score": 85,
            "analysis": "Brief, sharp analysis of the power dynamic in {language}.",
            "winning_point": "The strongest point made by the winner in {language}.",
            "weak_point": "The mistake or weak spot of the loser in {language}.",
            "advice": "A strategic, Machiavellian piece of advice for the user in {language}."
        }}
        """

        content = [
            prompt,
            {"mime_type": "image/jpeg", "data": image_bytes}
        ]

        response = await model.generate_content_async(content)
        cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
        result = json.loads(cleaned_text)

        return result

    except Exception as e:
        print(f"Argument judge error: {e}")
        raise HTTPException(status_code=500, detail="The judge is out to lunch.")

@app.post("/generate-chat-reply", response_model=ChatReplyResponse)
async def generate_chat_reply(
    image: UploadFile = File(...),
    context: str = "I like this person, help me keep the conversation going.",
    language: str = Query("Turkish", description="Output language")
):
    """
    Analyzes a chat screenshot (WhatsApp, iMessage, DM) and generates the perfect replies
    to continue or save the conversation.
    """
    try:
        image_bytes = await image.read()

        prompt = f"""
        You are a top-tier Dating & Communication Coach. 
        The user needs help replying to this specific chat conversation.
        
        TARGET LANGUAGE: {language.upper()}
        
        Task:
        1. Read the chat history in the image. Identify who is who.
        2. Analyze the "Vibe" (Is the other person dry? Enthusiastic? Ghosting?).
        3. Generate 3 DISTINCT replies for the user to send NEXT.
        
        Options to generate:
        - Option 1 (Cool/Low Investment): Matches their energy, doesn't try too hard.
        - Option 2 (Playful/Teasing): Spices things up, creates tension.
        - Option 3 (Direct/Bold): Moves things forward (date or topic change).
        
        CRITICAL:
        - Output strictly in {language}.
        - Use natural slang/texting style suitable for {language}.
        - Keep replies relatively short (like a real text).
        
        Return strictly JSON:
        {{
            "analysis": "Brief analysis of the situation in {language} (e.g. 'She is giving short answers, pull back a bit').",
            "replies": [
                {{ "tone": "Cool/Casual", "text": "Reply text in {language}", "explanation": "Why this works in {language}" }},
                {{ "tone": "Playful", "text": "Reply text in {language}", "explanation": "Why this works in {language}" }},
                {{ "tone": "Direct", "text": "Reply text in {language}", "explanation": "Why this works in {language}" }}
            ]
        }}
        """

        content = [
            prompt,
            {"mime_type": "image/jpeg", "data": image_bytes}
        ]

        response = await model.generate_content_async(content)
        
        cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
        result = json.loads(cleaned_text)

        return result

    except Exception as e:
        print(f"Chat reply error: {e}")
        raise HTTPException(status_code=500, detail="Could not generate a reply.")


if __name__ == "__main__":
    import uvicorn

    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=8000)
