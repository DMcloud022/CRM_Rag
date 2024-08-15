import aiohttp
import asyncio
from typing import Optional, Dict, Any
from config import SERPER_API_KEY, PERPLEXITY_API_KEY, OPENAI_API_KEY
import json
from openai import AsyncOpenAI
from models.lead import Lead, PublicData, WorkExperience, Education

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

async def gather_public_data(email: Optional[str]) -> Dict[str, Any]:
    public_data = {
        "serper_data": {},
        "perplexity_data": {},
    }
    
    if email:
        public_data["serper_data"] = await search_email_data(email)
        public_data["perplexity_data"] = await search_perplexity_data(email)
    
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

async def structure_public_data(serper_data: Dict[str, Any], perplexity_data: Dict[str, Any]) -> PublicData:
    combined_data = json.dumps({
        "serper_data": serper_data,
        "perplexity_data": perplexity_data
    })

    prompt = f"""
    Analyze the following public data and structure it according to the PublicData model:

    {combined_data}

    Extract and structure the following information:
    1. Bio
    2. Skills
    3. Languages
    4. Interests
    5. Publications
    6. Awards
    7. Work Experience (list of companies, positions, start dates, end dates)
    8. Education (list of institutions, degrees, fields of study, graduation years)

    Provide the structured data in JSON format.
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
        structured_data = json.loads(response.choices[0].message.content)
        return PublicData(**structured_data)
    except Exception as e:
        print(f"Error structuring public data: {e}")
        return PublicData()

async def enrich_lead_with_public_data(lead: Lead, public_data: Dict[str, Any]) -> Lead:
    structured_data = await structure_public_data(public_data["serper_data"], public_data["perplexity_data"])
    lead.public_data = structured_data
    return lead