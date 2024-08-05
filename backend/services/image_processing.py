import base64
import json
from typing import Dict, Any
from fastapi import UploadFile, HTTPException
from openai import AsyncOpenAI
from config import OPENAI_API_KEY

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB

async def transcribe_business_card(image: UploadFile) -> Dict[str, Any]:
    try:
        await validate_image(image)
        image_content = await image.read()
        base64_image = base64.b64encode(image_content).decode("utf-8")

        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI assistant tasked with transcribing business card information. Extract all relevant details and present them in a structured JSON format."
                },
                {
                    "role": "user",
                    "content": "Please transcribe the text from this business card image and provide the information in a structured JSON format. Include fields such as name, job_title, company, email, phone, website, address, and linkedin_profile if available. If a field is not present or cannot be determined, omit it from the JSON."
                },
                {
                    "role": "user",
                    "content": f"data:image/jpeg;base64,{base64_image}" 
                }
            ]
        )

        content = response.choices[0].message.content
        transcription = parse_gpt_response(content)
        
        return transcription

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error transcribing business card: {str(e)}")

async def validate_image(image: UploadFile):
    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported image format. Please upload one of: {', '.join(ALLOWED_IMAGE_TYPES)}.")
    
    if image.size > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=400, detail=f"Image size exceeds the maximum limit of {MAX_IMAGE_SIZE / (1024 * 1024)}MB.")

def parse_gpt_response(content: str) -> Dict[str, Any]:
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {"error": "Failed to parse response from GPT model"} 
