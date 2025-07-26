# 🚀 Setup Guide - LinkedIn Astrology App

## 📋 Prerequisites

1. **Python 3.8+** installed
2. **Node.js 16+** and npm installed
3. API accounts for:
   - OpenAI
   - Apify

## 🔑 Step 1: Get Your API Keys

### OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Sign up/log in to your OpenAI account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)
5. **Important**: Add credits to your OpenAI account for API usage

### Apify API Token & Actor ID
1. Go to https://apify.com and create an account
2. Navigate to **Integrations** → **API tokens**
3. Copy your API token

4. **Find LinkedIn Actor**:
   - Go to https://apify.com/store
   - Search for "LinkedIn Profile Scraper"
   - Choose a reliable actor (e.g., "LinkedIn Profile Scraper by Apify")
   - Copy the Actor ID from the URL (e.g., `apify/linkedin-profile-scraper`)

## ⚙️ Step 2: Configure Environment Variables

1. **Edit the `.env` file** in the project root:

```bash
# Replace with your actual API keys
OPENAI_API_KEY=sk-your_actual_openai_key_here
APIFY_API_TOKEN=apify_api_your_actual_token_here
APIFY_LINKEDIN_ACTOR_ID=apify/linkedin-profile-scraper

# Leave these as-is for development
APP_ENV=development
DEBUG=true
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## 🧪 Step 3: Test Your API Setup

Run the test script to verify everything works:

```bash
cd linkedin-astro-app
python test_apis.py
```

You should see:
```
✅ OpenAI API: Working correctly
✅ Apify API: Working correctly
✅ LinkedIn Actor: Found 'LinkedIn Profile Scraper'
🎉 All APIs are working!
```

## 🏃‍♂️ Step 4: Install Dependencies & Run

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python app.py
```

The backend will start at: http://localhost:8000

### Frontend Setup (in a new terminal)
```bash
cd frontend
npm install
npm start
```

The frontend will start at: http://localhost:3000

## 🌟 Step 5: Test the App

1. Open http://localhost:3000
2. Add your LinkedIn profile URL
3. Select your zodiac sign
4. Add coworkers' profiles
5. Click "Analyze Team Compatibility"
6. Wait for the cosmic magic! ✨

## 🛠️ Troubleshooting

### "API Key not found" errors
- Make sure your `.env` file is in the project root
- Check that there are no spaces around the `=` signs
- Ensure your API keys are valid and have credits

### "Actor not found" errors
- Verify the Actor ID is correct
- Make sure you have access to the actor
- Try a different LinkedIn scraper actor from Apify store

### "Connection refused" errors
- Make sure both backend (port 8000) and frontend (port 3000) are running
- Check firewall settings
- Try restarting both services

### LinkedIn scraping issues
- Some LinkedIn profiles may be private
- Rate limiting may occur with too many profiles
- Use public LinkedIn profile URLs

## 💡 Tips

1. **Start small**: Test with 2-3 profiles first
2. **Use public profiles**: Private profiles won't work
3. **LinkedIn URLs**: Use the format `https://www.linkedin.com/in/username`
4. **API costs**: Be aware of OpenAI API usage costs
5. **Apify credits**: Monitor your Apify usage/credits

## 🎯 Expected Behavior

1. **Input Phase**: Add LinkedIn URLs + zodiac signs
2. **Scraping Phase**: ~30-60 seconds per profile
3. **Analysis Phase**: ~10-20 seconds for AI analysis
4. **Results Phase**: Beautiful report with compatibility scores
5. **Sharing**: Shareable links and social media integration

## 📞 Support

If you encounter issues:
1. Run `python test_apis.py` to verify setup
2. Check the browser console for errors
3. Check the backend terminal for error messages
4. Ensure all requirements are installed

---

**Ready to discover your team's cosmic compatibility!** 🌟✨