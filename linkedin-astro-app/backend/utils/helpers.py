import re
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

def generate_report_id() -> str:
    """Generate a unique report ID"""
    return str(uuid.uuid4())[:8]

def validate_linkedin_url(url: str) -> bool:
    """Validate LinkedIn profile URL format"""
    linkedin_patterns = [
        r'^https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9\-]+/?$',
        r'^https?://(?:www\.)?linkedin\.com/pub/[a-zA-Z0-9\-/]+/?$'
    ]
    
    return any(re.match(pattern, url) for pattern in linkedin_patterns)

def extract_linkedin_username(url: str) -> Optional[str]:
    """Extract username/ID from LinkedIn URL"""
    match = re.search(r'/in/([a-zA-Z0-9\-]+)', url)
    if match:
        return match.group(1)
    
    match = re.search(r'/pub/([a-zA-Z0-9\-]+)', url)
    if match:
        return match.group(1)
    
    return None

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations"""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def format_zodiac_sign(sign: str) -> str:
    """Format zodiac sign to standard format"""
    return sign.lower().strip()

def is_valid_zodiac_sign(sign: str) -> bool:
    """Validate zodiac sign"""
    valid_signs = {
        'aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo',
        'libra', 'scorpio', 'sagittarius', 'capricorn', 'aquarius', 'pisces'
    }
    return format_zodiac_sign(sign) in valid_signs

def calculate_age_from_date(date_str: str) -> Optional[int]:
    """Calculate age from date string (if available)"""
    try:
        birth_date = datetime.strptime(date_str, '%Y-%m-%d')
        today = datetime.now()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age
    except:
        return None

def extract_experience_years(work_experiences: List[Dict[str, Any]]) -> int:
    """Calculate total years of experience from work history"""
    total_months = 0
    
    for exp in work_experiences:
        duration = exp.get('duration', '')
        
        # Parse duration strings like "2 yrs 3 mos", "1 yr", "6 mos"
        years_match = re.search(r'(\d+)\s*yrs?', duration)
        months_match = re.search(r'(\d+)\s*mos?', duration)
        
        if years_match:
            total_months += int(years_match.group(1)) * 12
        if months_match:
            total_months += int(months_match.group(1))
    
    return max(0, total_months // 12)

def get_current_position_info(work_experiences: List[Dict[str, Any]]) -> Dict[str, Optional[str]]:
    """Extract current position information"""
    if not work_experiences:
        return {"title": None, "company": None, "level": "individual_contributor"}
    
    current_exp = work_experiences[0]  # Assuming first is most recent
    title = current_exp.get('title', '').lower()
    
    # Determine seniority level
    level = "individual_contributor"
    if any(keyword in title for keyword in ['ceo', 'president', 'founder']):
        level = "executive"
    elif any(keyword in title for keyword in ['vp', 'vice president', 'director']):
        level = "senior_management"
    elif any(keyword in title for keyword in ['manager', 'lead', 'head', 'supervisor']):
        level = "management"
    elif any(keyword in title for keyword in ['senior', 'principal', 'staff']):
        level = "senior"
    
    return {
        "title": current_exp.get('title'),
        "company": current_exp.get('company'),
        "level": level
    }

def extract_skills_keywords(skills: List[Dict[str, Any]]) -> List[str]:
    """Extract and categorize skills"""
    technical_keywords = {
        'python', 'javascript', 'react', 'node', 'sql', 'aws', 'docker', 
        'kubernetes', 'machine learning', 'data science', 'analytics'
    }
    
    management_keywords = {
        'leadership', 'management', 'strategy', 'planning', 'team building',
        'project management', 'agile', 'scrum'
    }
    
    skill_names = [skill.get('name', '').lower() for skill in skills]
    
    categorized_skills = {
        'technical': [skill for skill in skill_names if any(keyword in skill for keyword in technical_keywords)],
        'management': [skill for skill in skill_names if any(keyword in skill for keyword in management_keywords)],
        'other': [skill for skill in skill_names if skill not in ['technical', 'management']]
    }
    
    return categorized_skills

def create_shareable_summary(report_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a summary suitable for sharing/preview"""
    return {
        "team_size": len(report_data.get('team_members', [])) + 1,
        "average_compatibility": report_data.get('team_average_score', 0),
        "top_insight": report_data.get('team_dynamic_summary', '')[:100] + '...',
        "zodiac_mix": list(report_data.get('team_zodiac_breakdown', {}).keys()),
        "generated_at": datetime.now().isoformat()
    }

def get_compatibility_emoji(score: int) -> str:
    """Get emoji based on compatibility score"""
    if score >= 90:
        return "🔥"
    elif score >= 80:
        return "✨"
    elif score >= 70:
        return "🌟"
    elif score >= 60:
        return "⭐"
    else:
        return "🌙"

def format_report_for_social_sharing(report: Dict[str, Any]) -> Dict[str, str]:
    """Format report data for social media sharing"""
    main_user = report.get('main_user', {})
    team_size = len(report.get('team_members', [])) + 1
    avg_score = report.get('team_average_score', 0)
    
    title = f"{main_user.get('profile', {}).get('full_name', 'Someone')}'s Team Cosmic Compatibility"
    description = f"🌟 Team of {team_size} • {avg_score}% cosmic alignment • {get_compatibility_emoji(avg_score)}"
    
    hashtags = "#WorkplaceAstrology #TeamCompatibility #LinkedInAstro #CosmicCollaboration"
    
    return {
        "title": title,
        "description": description,
        "hashtags": hashtags,
        "preview_text": f"Discover how your team's zodiac signs affect workplace dynamics! {description}"
    }

def validate_environment_variables() -> Dict[str, bool]:
    """Check if required environment variables are set"""
    import os
    
    required_vars = {
        "OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY")),
        "APIFY_API_TOKEN": bool(os.getenv("APIFY_API_TOKEN")),
        "APIFY_LINKEDIN_ACTOR_ID": bool(os.getenv("APIFY_LINKEDIN_ACTOR_ID"))
    }
    
    return required_vars

def log_analysis_metrics(report_data: Dict[str, Any]) -> None:
    """Log metrics for analysis performance tracking"""
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "team_size": len(report_data.get('team_members', [])) + 1,
        "average_score": report_data.get('team_average_score', 0),
        "processing_time": report_data.get('processing_time_seconds', 0),
        "zodiac_distribution": report_data.get('team_zodiac_breakdown', {})
    }
    
    # In a production app, this would log to a proper analytics service
    print(f"Analysis Metrics: {json.dumps(metrics, indent=2)}")

class ReportCache:
    """Simple in-memory cache for reports (for MVP - replace with Redis in production)"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._timestamps: Dict[str, datetime] = {}
        self.max_age_hours = 24
    
    def get(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Get cached report if it exists and is not expired"""
        if report_id not in self._cache:
            return None
        
        # Check if expired
        cached_time = self._timestamps.get(report_id)
        if cached_time and (datetime.now() - cached_time).total_seconds() > (self.max_age_hours * 3600):
            self.delete(report_id)
            return None
        
        return self._cache.get(report_id)
    
    def set(self, report_id: str, report_data: Dict[str, Any]) -> None:
        """Cache report data"""
        self._cache[report_id] = report_data
        self._timestamps[report_id] = datetime.now()
    
    def delete(self, report_id: str) -> None:
        """Delete cached report"""
        self._cache.pop(report_id, None)
        self._timestamps.pop(report_id, None)
    
    def clear_expired(self) -> None:
        """Clear all expired cache entries"""
        current_time = datetime.now()
        expired_ids = [
            report_id for report_id, timestamp in self._timestamps.items()
            if (current_time - timestamp).total_seconds() > (self.max_age_hours * 3600)
        ]
        
        for report_id in expired_ids:
            self.delete(report_id)

# Global cache instance for MVP
report_cache = ReportCache()