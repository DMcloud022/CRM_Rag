import aiohttp
import asyncio
from typing import Optional, Dict, Any
from backend.config import SERPER_API_KEY, PERPLEXITY_API_KEY, OPENAI_API_KEY
import json
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

async def gather_public_data(email: Optional[str], linkedin_profile: Optional[str]) -> Dict[str, Any]:
    public_data = {
        "serper_data": {},
        "perplexity_data": {},
        "combined_summary": "",
    }
    
    if email:
        serper_data = await search_email_data(email)
        perplexity_data = await search_perplexity_data(email)
        
        # Ensure we handle cases where `search_email_data` might return an error or empty response
        public_data["serper_data"] = serper_data if isinstance(serper_data, dict) else {}
        public_data["perplexity_data"] = perplexity_data if isinstance(perplexity_data, dict) else {}
        
        # Generate summary if we have data
        public_data["combined_summary"] = await summarize_public_data(public_data)
    
    return public_data

async def search_email_data(email: str) -> Dict[str, Any]:
    url = 'https://google.serper.dev/search'
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }
    data = {'q': email}
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=data, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Failed to retrieve data, status code: {response.status}"}
        except aiohttp.ClientError as e:
            return {"error": f"Request to Serper API failed: {str(e)}"}

async def search_perplexity_data(email: str) -> Dict[str, Any]:
    perplexity_client = AsyncOpenAI(api_key=PERPLEXITY_API_KEY, base_url="https://api.perplexity.ai")
    
    messages = [
        {
            "role": "system",
            "content": "Given an email address, provide a comprehensive report of publicly available information about the associated person. The report should include their professional details, personal information, and online presence, while excluding any hypothetical or inferred data. Provide factual information only and do not create or make assumptions about the individual."
        },
        {
            "role": "user",
            "content": f"Provide a thorough report on the publicly available information related to the individual associated with the email address: {email}. Please gather and categorize all relevant data you can find. Organize the data in a clear and concise manner, making sure to provide a comprehensive overview of the individual's publicly available information."
        },
    ]
    
    try:
        response = await perplexity_client.chat.completions.create(
            model="llama-3-sonar-large-32k-online",
            messages=messages,
        )
        
        content = response.choices[0].message.content
        
        try:
            perplexity_data = json.loads(content)
        except json.JSONDecodeError:
            perplexity_data = {"summary": content}

        return clean_data(perplexity_data)
    
    except Exception as e:
        print(f"Error querying Perplexity API: {e}")
        return {"error": str(e)}

def clean_data(data: Dict[str, Any]) -> Dict[str, Any]:
    if isinstance(data, dict):
        return {k: clean_data(v) for k, v in data.items() 
                if v not in (None, "", {}) and clean_data(v) not in (None, "", {})}
    elif isinstance(data, list):
        return [clean_data(v) for v in data if v not in (None, "", {}) and clean_data(v) not in (None, "", {})]
    else:
        return data

async def summarize_public_data(data: Dict[str, Any]) -> str:
    # Ensure that we are accessing keys safely
    serper_data = data.get("serper_data", {})
    perplexity_data = data.get("perplexity_data", {})
    
    if not serper_data and not perplexity_data:
        return "No public data available"

    combined_data = json.dumps({
        "serper_data": serper_data,
        "perplexity_data": perplexity_data
    }, indent=2)

    prompt = f"""
    Summarize the following public data into a comprehensive yet concise and structured summary of 3-4 sentences only. 
    This data includes information from both Serper and Perplexity APIs.

    Create a well-structured and easily readable summary that provides a complete overview of the professional's public data.

    Public Data:
    {combined_data}

    Please provide a structured summary of this data, highlighting the most important and reliable information.
    """

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error summarizing public data: {e}")
        return "Error: Unable to summarize public data"
