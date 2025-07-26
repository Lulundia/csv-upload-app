from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from .profile import ProfileWithZodiac

class CompatibilityPair(BaseModel):
    """Compatibility analysis between two people"""
    person1: ProfileWithZodiac
    person2: ProfileWithZodiac
    compatibility_score: int  # 0-100
    compatibility_level: str  # "high", "medium", "low"
    description: str
    
    # Detailed analysis
    work_dynamic: Optional[str] = None
    communication_style: Optional[str] = None
    potential_conflicts: Optional[List[str]] = None
    strengths: Optional[List[str]] = None
    recommendations: Optional[str] = None

class TeamCompatibilityReport(BaseModel):
    """Complete team compatibility analysis"""
    main_user: ProfileWithZodiac
    team_members: List[ProfileWithZodiac]
    
    # Individual compatibility pairs
    compatibility_pairs: List[CompatibilityPair]
    
    # Overall team insights
    team_average_score: float
    team_dynamic_summary: str
    team_strengths: List[str]
    team_challenges: List[str]
    
    # Fun elements for shareability
    team_zodiac_breakdown: Dict[str, int]  # Count of each sign
    most_compatible_pair: Optional[CompatibilityPair] = None
    most_challenging_pair: Optional[CompatibilityPair] = None
    
    # Report metadata
    generated_at: str
    report_id: str
    shareable_url: Optional[str] = None

class ShareableReport(BaseModel):
    """Lightweight version for sharing/display"""
    report_id: str
    main_user_name: str
    main_user_image: Optional[str] = None
    team_size: int
    average_compatibility: float
    top_insight: str
    preview_image_url: Optional[str] = None  # Generated preview card
    full_report_url: str

class ReportGenerationRequest(BaseModel):
    """Request to generate a visual report"""
    compatibility_report: TeamCompatibilityReport
    include_images: bool = True
    format: str = "web"  # "web", "image", "pdf"
    branding: Optional[Dict[str, str]] = None  # Custom branding options