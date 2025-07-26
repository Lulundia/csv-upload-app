#!/usr/bin/env python3
"""
Test script to verify API keys are working
Run this after setting up your .env file
"""

import os
import asyncio
import aiohttp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_openai_api():
    """Test OpenAI API connection"""
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        return False
    
    if not api_key.startswith("sk-"):
        print("❌ OPENAI_API_KEY format is invalid (should start with 'sk-')")
        return False
    
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=api_key)
        
        # Simple test call
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'API test successful'"}],
            max_tokens=10
        )
        
        print("✅ OpenAI API: Working correctly")
        print(f"   Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API Error: {str(e)}")
        return False

async def test_apify_api():
    """Test Apify API connection"""
    api_token = os.getenv("APIFY_API_TOKEN")
    actor_id = os.getenv("APIFY_LINKEDIN_ACTOR_ID")
    
    if not api_token:
        print("❌ APIFY_API_TOKEN not found in environment variables")
        return False
    
    if not actor_id:
        print("❌ APIFY_LINKEDIN_ACTOR_ID not found in environment variables")
        return False
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test API token by checking account info
            url = "https://api.apify.com/v2/users/me"
            headers = {"Authorization": f"Bearer {api_token}"}
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    user_data = await response.json()
                    username = user_data.get("data", {}).get("username", "Unknown")
                    print(f"✅ Apify API: Working correctly")
                    print(f"   Account: {username}")
                    
                    # Test actor exists
                    actor_url = f"https://api.apify.com/v2/acts/{actor_id}"
                    async with session.get(actor_url, headers=headers) as actor_response:
                        if actor_response.status == 200:
                            actor_data = await actor_response.json()
                            actor_name = actor_data.get("data", {}).get("name", "Unknown")
                            print(f"✅ LinkedIn Actor: Found '{actor_name}'")
                            return True
                        else:
                            print(f"❌ LinkedIn Actor '{actor_id}' not found or not accessible")
                            return False
                else:
                    print(f"❌ Apify API Error: HTTP {response.status}")
                    return False
                    
    except Exception as e:
        print(f"❌ Apify API Error: {str(e)}")
        return False

async def main():
    """Run all API tests"""
    print("🧪 Testing API Connections...\n")
    
    # Test environment file loading
    if not os.path.exists(".env"):
        print("❌ .env file not found! Please create it with your API keys.")
        return
    
    print("✅ .env file found")
    
    # Test individual APIs
    openai_ok = await test_openai_api()
    print()
    apify_ok = await test_apify_api()
    print()
    
    # Summary
    if openai_ok and apify_ok:
        print("🎉 All APIs are working! You can now run the application.")
        print("\nTo start the app:")
        print("1. Backend: cd backend && python app.py")
        print("2. Frontend: cd frontend && npm start")
    else:
        print("❌ Some APIs failed. Please check your .env file and API keys.")
        print("\nMake sure your .env file looks like:")
        print("OPENAI_API_KEY=sk-your_actual_key_here")
        print("APIFY_API_TOKEN=apify_api_your_actual_token_here")
        print("APIFY_LINKEDIN_ACTOR_ID=apify/linkedin-profile-scraper")

if __name__ == "__main__":
    asyncio.run(main())