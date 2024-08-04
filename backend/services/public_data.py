import aiohttp
import asyncio
from typing import Optional, Dict, Any, List
from config import SERPER_API_KEY, PERPLEXITY_API_KEY
import json
from fastapi import HTTPException

async def gather_public_data(email: Optional[str], linkedin_profile: Optional[str]) -> Dict[str, Any]:
    public_data = {}
    
    tasks = []
    if email:
        tasks.extend([
            search_serper(email),
            search_email_data(email),
        ])
    
    if linkedin_profile:
        tasks.append(search_perplexity(linkedin_profile))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    if email:
        public_data["serper_data"] = results[0] if not isinstance(results[0], Exception) else {}
        public_data["email_data"] = results[1] if not isinstance(results[1], Exception) else {}
    
    if linkedin_profile:
        public_data["perplexity_data"] = results[-1] if not isinstance(results[-1], Exception) else {}
    
    return public_data

async def search_serper(query: str) -> Dict[str, Any]:
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query, "num": 20}) 
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=payload) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise HTTPException(status_code=response.status, detail="Error from Serper API")
    except aiohttp.ClientError as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to Serper API: {str(e)}")

async def search_perplexity(query: str) -> str:
    url = "https://api.perplexity.ai/chat/completions"
    payload = json.dumps({
        "model": "mixtral-8x7b-instruct",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant that provides comprehensive information about professionals based on their LinkedIn profiles."
            },
            {
                "role": "user",
                "content": f"Provide a detailed summary of the professional information for the person with this LinkedIn profile: {query}. Include their work history, education, skills, and any notable achievements or publications if available."
            }
        ]
    })
    headers = {
        'Authorization': f'Bearer {PERPLEXITY_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['choices'][0]['message']['content']
                else:
                    raise HTTPException(status_code=response.status, detail="Error from Perplexity API")
    except aiohttp.ClientError as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to Perplexity API: {str(e)}")

async def search_email_data(email: str) -> Dict[str, Any]:
    tasks = [
        search_social_profiles(email),
        search_professional_info(email),
        search_company_info(email),
        search_public_records(email),
        search_digital_footprint(email)
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return {
        "social_profiles": results[0] if not isinstance(results[0], Exception) else {},
        "professional_info": results[1] if not isinstance(results[1], Exception) else {},
        "company_info": results[2] if not isinstance(results[2], Exception) else {},
        "public_records": results[3] if not isinstance(results[3], Exception) else {},
        "digital_footprint": results[4] if not isinstance(results[4], Exception) else {}
    }

async def search_social_profiles(email: str) -> Dict[str, str]:
    platforms = ['linkedin.com', 'twitter.com', 'facebook.com', 'github.com']
    results = {}
    for platform in platforms:
        query = f"site:{platform} {email}"
        data = await search_serper(query)
        if 'organic' in data:
            for result in data['organic']:
                if platform in result.get('link', ''):
                    results[platform] = result['link']
                    break
    return results

async def search_professional_info(email: str) -> Dict[str, Any]:
    query = f"{email} professional profile"
    data = await search_serper(query)
    info = {}
    if 'organic' in data:
        for result in data['organic']:
            if 'linkedin.com/in/' in result.get('link', ''):
                info['linkedin'] = result['link']
                info['title'] = result.get('title', '')
                info['snippet'] = result.get('snippet', '')
                break
    return info

async def search_company_info(email: str) -> Dict[str, Any]:
    domain = email.split('@')[-1]
    query = f"site:{domain}"
    data = await search_serper(query)
    info = {}
    if 'organic' in data:
        for result in data['organic']:
            if domain in result.get('link', ''):
                info['website'] = result['link']
                info['title'] = result.get('title', '')
                info['snippet'] = result.get('snippet', '')
                break
    return info

async def search_public_records(email: str) -> List[str]:
    query = f"{email} public records"
    data = await search_serper(query)
    records = []
    if 'organic' in data:
        records = [result['link'] for result in data['organic'][:5]]
    return records

async def search_digital_footprint(email: str) -> List[Dict[str, str]]:
    query = f"{email}"
    data = await search_serper(query)
    footprint = []
    if 'organic' in data:
        footprint = [
            {
                'title': result.get('title', ''),
                'link': result.get('link', ''),
                'snippet': result.get('snippet', '')
            }
            for result in data['organic'][:10]
        ]
    return footprint