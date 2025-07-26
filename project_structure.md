# LinkedIn Astrology Compatibility Web App

## Project Structure

```
linkedin-astro-app/
├── backend/
│   ├── app.py                 # FastAPI main application
│   ├── models/
│   │   ├── __init__.py
│   │   ├── profile.py         # Profile data models
│   │   └── compatibility.py   # Compatibility models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── apify_scraper.py   # LinkedIn scraping via Apify
│   │   ├── openai_service.py  # OpenAI API integration
│   │   └── astrology.py       # Zodiac compatibility logic
│   ├── utils/
│   │   ├── __init__.py
│   │   └── helpers.py         # Utility functions
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── public/
│   │   ├── index.html
│   │   └── favicon.ico
│   ├── src/
│   │   ├── components/
│   │   │   ├── ProfileInput.js    # LinkedIn URL input form
│   │   │   ├── ZodiacSelector.js  # Zodiac sign selection
│   │   │   ├── CompatibilityReport.js # Results display
│   │   │   └── LoadingSpinner.js  # Loading states
│   │   ├── services/
│   │   │   └── api.js             # API communication
│   │   ├── styles/
│   │   │   └── main.css           # Styling
│   │   ├── App.js                 # Main React component
│   │   └── index.js               # React entry point
│   ├── package.json
│   └── package-lock.json
├── shared/
│   └── zodiac_data.json           # Zodiac signs and compatibility rules
├── .env.example                   # Environment variables template
├── README.md                      # Project documentation
└── docker-compose.yml            # Optional containerization
```

## Tech Stack
- **Backend**: FastAPI (Python)
- **Frontend**: React.js
- **APIs**: Apify (LinkedIn scraping), OpenAI (analysis)
- **Storage**: JSON files (MVP), easily upgradeable to Supabase
- **Styling**: CSS with modern design principles

## Key Features
1. LinkedIn profile URL input and validation
2. Zodiac sign assignment (dropdown/emoji selector)
3. Batch profile scraping via Apify
4. AI-powered work style analysis
5. Astrology-based compatibility scoring
6. Visual report generation with sharing capabilities
7. Clean, playful UI with "Spotify Wrapped" vibes