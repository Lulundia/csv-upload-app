from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import asyncio
from datetime import datetime
from typing import Dict, List, Any
import time

# Import models
from models.profile import BatchProfileRequest, ProfileWithZodiac, LinkedInProfile
from models.compatibility import TeamCompatibilityReport, ShareableReport

# Import services
from services.apify_scraper import create_apify_scraper
from services.openai_service import create_openai_service
from services.astrology import create_astrology_service

# Import utilities
from utils.helpers import (
    generate_report_id, validate_linkedin_url, is_valid_zodiac_sign,
    format_zodiac_sign, report_cache, validate_environment_variables,
    log_analysis_metrics, create_shareable_summary, format_report_for_social_sharing
)

app = FastAPI(
    title="LinkedIn Astrology Compatibility API",
    description="Analyze workplace compatibility using LinkedIn profiles and zodiac signs",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
try:
    apify_scraper = create_apify_scraper()
    openai_service = create_openai_service()
    astrology_service = create_astrology_service()
except ValueError as e:
    print(f"Service initialization error: {e}")
    apify_scraper = None
    openai_service = None
    astrology_service = None

@app.get("/")
async def root():
    """Health check and API info"""
    env_status = validate_environment_variables()
    return {
        "message": "LinkedIn Astrology Compatibility API",
        "version": "1.0.0",
        "status": "running",
        "environment_check": env_status,
        "services_available": {
            "apify": apify_scraper is not None,
            "openai": openai_service is not None,
            "astrology": astrology_service is not None
        }
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "timestamp": datetime.now().isoformat(),
        "status": "healthy",
        "services": {
            "apify_scraper": "operational" if apify_scraper else "not_configured",
            "openai_service": "operational" if openai_service else "not_configured", 
            "astrology_service": "operational" if astrology_service else "error"
        }
    }

@app.get("/zodiac-signs")
async def get_zodiac_signs():
    """Get list of all zodiac signs with info"""
    if not astrology_service:
        raise HTTPException(status_code=500, detail="Astrology service not available")
    
    signs_data = astrology_service.zodiac_data.get("zodiac_signs", {})
    return {
        "signs": [
            {
                "key": key,
                "name": info.get("name", key.title()),
                "emoji": info.get("emoji", "⭐"),
                "element": info.get("element", "Unknown"),
                "dates": info.get("dates", ""),
                "work_traits": info.get("work_traits", [])
            }
            for key, info in signs_data.items()
        ]
    }

@app.post("/analyze-team")
async def analyze_team_compatibility(request: BatchProfileRequest, background_tasks: BackgroundTasks):
    """
    Main endpoint: Analyze team compatibility
    1. Scrape LinkedIn profiles
    2. Analyze work styles with AI
    3. Calculate compatibility
    4. Generate report
    """
    start_time = time.time()
    
    # Validate input
    if not request.profiles:
        raise HTTPException(status_code=400, detail="At least one profile is required")
    
    # Validate URLs and zodiac signs
    for profile_input in request.profiles:
        if not validate_linkedin_url(str(profile_input.linkedin_url)):
            raise HTTPException(status_code=400, detail=f"Invalid LinkedIn URL: {profile_input.linkedin_url}")
        
        if not is_valid_zodiac_sign(profile_input.zodiac_sign):
            raise HTTPException(status_code=400, detail=f"Invalid zodiac sign: {profile_input.zodiac_sign}")
    
    # Check services availability
    if not all([apify_scraper, openai_service, astrology_service]):
        raise HTTPException(status_code=500, detail="Required services not available")
    
    try:
        # Generate report ID
        report_id = generate_report_id()
        
        # Step 1: Scrape LinkedIn profiles
        linkedin_urls = [str(profile.linkedin_url) for profile in request.profiles]
        scraped_profiles = await apify_scraper.scrape_profiles(linkedin_urls)
        
        # Step 2: Enrich profiles with zodiac and AI analysis
        enriched_profiles = []
        for i, scraped_profile in enumerate(scraped_profiles):
            profile_input = request.profiles[i]
            
            # AI analysis of work style using ALL scraped data
            ai_analysis = await openai_service.analyze_work_style(
                scraped_profile, 
                profile_input.zodiac_sign
            )
            
            # Create enriched profile
            enriched_profile = ProfileWithZodiac(
                profile=scraped_profile,
                zodiac_sign=format_zodiac_sign(profile_input.zodiac_sign),
                is_main_user=profile_input.is_main_user,
                work_style_analysis=ai_analysis.get("work_style_analysis"),
                personality_traits=ai_analysis.get("personality_traits"),
                leadership_style=ai_analysis.get("leadership_style"),
                communication_style=ai_analysis.get("communication_style")
            )
            enriched_profiles.append(enriched_profile)
        
        # Step 3: Identify main user and team members
        main_user = next((p for p in enriched_profiles if p.is_main_user), enriched_profiles[0])
        team_members = [p for p in enriched_profiles if not p.is_main_user]
        
        # Step 4: Generate compatibility analysis
        team_analysis = astrology_service.generate_team_report(main_user, team_members)
        
        # Step 5: Enhanced team summary with AI
        if openai_service:
            ai_team_summary = await openai_service.generate_team_summary(team_analysis)
            team_analysis["team_dynamic_summary"] = ai_team_summary
        
        # Step 6: Create comprehensive report
        processing_time = time.time() - start_time
        
        report = TeamCompatibilityReport(
            main_user=main_user,
            team_members=team_members,
            compatibility_pairs=team_analysis["compatibility_pairs"],
            team_average_score=team_analysis["team_average_score"],
            team_dynamic_summary=team_analysis["team_dynamic_summary"],
            team_strengths=team_analysis["team_strengths"],
            team_challenges=team_analysis["team_challenges"],
            team_zodiac_breakdown=team_analysis["team_zodiac_breakdown"],
            most_compatible_pair=team_analysis.get("most_compatible_pair"),
            most_challenging_pair=team_analysis.get("most_challenging_pair"),
            generated_at=datetime.now().isoformat(),
            report_id=report_id,
            shareable_url=f"/report/{report_id}"
        )
        
        # Step 7: Cache the report
        report_dict = report.dict()
        report_dict["processing_time_seconds"] = processing_time
        report_cache.set(report_id, report_dict)
        
        # Step 8: Log metrics in background
        background_tasks.add_task(log_analysis_metrics, report_dict)
        
        return {
            "status": "success",
            "report_id": report_id,
            "report": report_dict,
            "processing_time": round(processing_time, 2),
            "shareable_summary": create_shareable_summary(report_dict),
            "social_sharing": format_report_for_social_sharing(report_dict)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/report/{report_id}")
async def get_report(report_id: str):
    """Get a previously generated report"""
    report = report_cache.get(report_id)
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found or expired")
    
    return {
        "status": "success",
        "report": report,
        "shareable_summary": create_shareable_summary(report),
        "social_sharing": format_report_for_social_sharing(report)
    }

@app.get("/report/{report_id}/summary")
async def get_report_summary(report_id: str):
    """Get a lightweight summary of a report for sharing"""
    report = report_cache.get(report_id)
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found or expired")
    
    main_user = report.get("main_user", {}).get("profile", {})
    
    summary = ShareableReport(
        report_id=report_id,
        main_user_name=main_user.get("full_name", "Team Lead"),
        main_user_image=main_user.get("profile_image_url"),
        team_size=len(report.get("team_members", [])) + 1,
        average_compatibility=report.get("team_average_score", 0),
        top_insight=report.get("team_dynamic_summary", "")[:150] + "...",
        full_report_url=f"/report/{report_id}"
    )
    
    return summary

@app.post("/validate-profile")
async def validate_profile(linkedin_url: str, zodiac_sign: str):
    """Validate a single profile input"""
    errors = []
    
    if not validate_linkedin_url(linkedin_url):
        errors.append("Invalid LinkedIn URL format")
    
    if not is_valid_zodiac_sign(zodiac_sign):
        errors.append("Invalid zodiac sign")
    
    if errors:
        return {"valid": False, "errors": errors}
    
    return {"valid": True, "errors": []}

@app.get("/compatibility/{sign1}/{sign2}")
async def get_sign_compatibility(sign1: str, sign2: str):
    """Get compatibility between two zodiac signs"""
    if not astrology_service:
        raise HTTPException(status_code=500, detail="Astrology service not available")
    
    if not is_valid_zodiac_sign(sign1) or not is_valid_zodiac_sign(sign2):
        raise HTTPException(status_code=400, detail="Invalid zodiac signs")
    
    score, level = astrology_service.calculate_compatibility(sign1, sign2)
    description = astrology_service.get_compatibility_description(sign1, sign2, level)
    
    return {
        "sign1": sign1.title(),
        "sign2": sign2.title(),
        "compatibility_score": score,
        "compatibility_level": level,
        "description": description
    }

@app.delete("/report/{report_id}")
async def delete_report(report_id: str):
    """Delete a cached report"""
    if report_cache.get(report_id):
        report_cache.delete(report_id)
        return {"status": "success", "message": "Report deleted"}
    else:
        raise HTTPException(status_code=404, detail="Report not found")

@app.post("/cache/cleanup")
async def cleanup_cache():
    """Manually trigger cache cleanup"""
    report_cache.clear_expired()
    return {"status": "success", "message": "Cache cleaned up"}

# Error handlers
@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": "Validation error", "errors": str(exc)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)