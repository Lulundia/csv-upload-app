from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime

class WorkExperience(BaseModel):
    """Individual work experience entry"""
    title: Optional[str] = None
    company: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    duration: Optional[str] = None
    is_current: Optional[bool] = False

class Education(BaseModel):
    """Education entry"""
    school: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None

class Skill(BaseModel):
    """Professional skill"""
    name: Optional[str] = None
    endorsements: Optional[int] = 0

class LinkedInProfile(BaseModel):
    """Complete LinkedIn profile data from Apify scraper"""
    # Basic info
    url: str
    full_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    headline: Optional[str] = None  # Current job title
    summary: Optional[str] = None
    
    # Profile image - IMPORTANT for final report
    profile_image_url: Optional[str] = None
    background_image_url: Optional[str] = None
    
    # Current position
    current_company: Optional[str] = None
    current_position: Optional[str] = None
    
    # Location and contact
    location: Optional[str] = None
    industry: Optional[str] = None
    
    # Experience and career data
    work_experiences: List[WorkExperience] = []
    education: List[Education] = []
    skills: List[Skill] = []
    
    # Additional LinkedIn data
    connections_count: Optional[int] = None
    followers_count: Optional[int] = None
    
    # Languages, certifications, etc.
    languages: List[str] = []
    certifications: List[Dict[str, Any]] = []
    volunteer_experiences: List[Dict[str, Any]] = []
    publications: List[Dict[str, Any]] = []
    patents: List[Dict[str, Any]] = []
    courses: List[Dict[str, Any]] = []
    projects: List[Dict[str, Any]] = []
    honors_awards: List[Dict[str, Any]] = []
    
    # Metadata
    scraped_at: Optional[datetime] = None
    raw_data: Optional[Dict[str, Any]] = None  # Store all raw Apify data

class ProfileInput(BaseModel):
    """User input for a single profile"""
    linkedin_url: HttpUrl
    zodiac_sign: str
    is_main_user: bool = False  # True for the user's own profile

class BatchProfileRequest(BaseModel):
    """Request to analyze multiple profiles"""
    profiles: List[ProfileInput]
    
    def get_main_profile(self) -> Optional[ProfileInput]:
        """Get the main user's profile"""
        for profile in self.profiles:
            if profile.is_main_user:
                return profile
        return None
    
    def get_coworker_profiles(self) -> List[ProfileInput]:
        """Get all coworker profiles"""
        return [p for p in self.profiles if not p.is_main_user]

class ProfileWithZodiac(BaseModel):
    """LinkedIn profile enriched with zodiac information"""
    profile: LinkedInProfile
    zodiac_sign: str
    is_main_user: bool = False
    
    # AI-generated insights
    work_style_analysis: Optional[str] = None
    personality_traits: Optional[List[str]] = None
    leadership_style: Optional[str] = None
    communication_style: Optional[str] = None