import base64
import re
from typing import Dict, Any, List
from openai import AsyncOpenAI
from fastapi import UploadFile, HTTPException
from services.public_data import gather_public_data
from config import OPENAI_API_KEY

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB

async def transcribe_business_card(image: UploadFile) -> Dict[str, Any]:
    try:
        # Validate image
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
                    "content": [
                        {
                            "type": "text",
                            "text": "Please transcribe the text from this business card image and provide the information in a structured JSON format. Include fields such as name, job_title, company, email, phone, website, address, and linkedin_profile if available. If a field is not present or cannot be determined, omit it from the JSON."
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        }
                    ],
                }
            ]
        )

        content = response.choices[0].message.content
        
        transcription = parse_gpt_response(content)
        
        public_data = await gather_public_data(transcription.get('email'), transcription.get('linkedin_profile'))
        
        result = {**transcription, 'public_data': public_data}
        
        return result

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error transcribing business card: {str(e)}")

async def validate_image(image: UploadFile):
    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported image format. Please upload a JPEG, PNG, GIF, or WebP image.")
    
    if image.size > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=400, detail="Image size exceeds the maximum limit of 10MB.")

def parse_gpt_response(content: str) -> Dict[str, Any]:
    try:
        # Try to parse as JSON first
        import json
        return json.loads(content)
    except json.JSONDecodeError:
        # If not JSON, fall back to line-by-line parsing
        return parse_line_by_line(content)

def parse_line_by_line(content: str) -> Dict[str, Any]:
    transcription = {}
    lines = content.split('\n')
    current_key = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip().lower().replace(' ', '_')
            value = value.strip()
            
            if key and value:
                transcription[key] = clean_value(key, value)
                current_key = key
        elif current_key:
            # Append to the previous key if it's a continuation
            transcription[current_key] += ' ' + line
    
    return transcription

def clean_value(key: str, value: str) -> Any:
    if key == 'email':
        # Basic email validation
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return value if re.match(email_pattern, value) else None
    elif key == 'phone':
        # Remove non-digit characters from phone number
        return re.sub(r'\D', '', value)
    elif key == 'website':
        # Basic URL validation
        url_pattern = r'^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$'
        return value if re.match(url_pattern, value) else None
    elif key == 'linkedin_profile':
        # Basic LinkedIn URL validation
        linkedin_pattern = r'^https:\/\/[a-z]{2,3}\.linkedin\.com\/.*$'
        return value if re.match(linkedin_pattern, value) else None
    else:
        return value.strip()