import os
import json
import google.generativeai as genai
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException, Query

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Aura Backend API",
    description="AI-Powered Dating Assistant Backend for analyzing vibe and compatibility."
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
    tone: str  # e.g., "Flirty", "Funny", "Mysterious"
    explanation: str # Why this line works

class RizzResponse(BaseModel):
    image_analysis: str
    options: List[RizzOption]

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
        response = model.generate_content(content)

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
        prompt = f"""
                You are a world-class social dynamics expert. 
                Generate the perfect "reply" to this Instagram Story.

                TARGET LANGUAGE: {language.upper()}

                Step 1: Analyze the image.
                Step 2: Generate 3 DISTINCT opening lines in {language}.

                CRITICAL CULTURAL INSTRUCTION:
                - Do not just translate. Use the natural slang, humor, and dating culture of {language}.
                - If {language} is Turkish, use natural phrases like "Oha", "Yok artık" if appropriate.
                - If {language} is English, use Gen-Z slang if the vibe fits.

                Guidelines:
                - NO generic "Hello".
                - Be specific to the photo content.

                Return strictly JSON:
                {{
                    "image_analysis": "Brief description in {language}",
                    "options": [
                        {{ "tone": "Funny", "text": "Line in {language}", "explanation": "Why this works (in {language})" }},
                        {{ "tone": "Flirty", "text": "Line in {language}", "explanation": "Why this works (in {language})" }},
                        {{ "tone": "Casual", "text": "Line in {language}", "explanation": "Why this works (in {language})" }}
                    ]
                }}
                """

        content = [
            prompt,
            {"mime_type": "image/jpeg", "data": image_bytes}
        ]

        response = model.generate_content(content)

        # Clean up JSON
        cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
        result = json.loads(cleaned_text)

        return result

    except Exception as e:
        print(f"Rizz generation error: {e}")
        raise HTTPException(status_code=500, detail="Rizz machine broken. Try again.")


if __name__ == "__main__":
    import uvicorn

    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=8000)
