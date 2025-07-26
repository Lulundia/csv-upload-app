import asyncio
import aiohttp
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
from ..models.profile import LinkedInProfile, WorkExperience, Education, Skill

class ApifyLinkedInScraper:
    """Service to scrape LinkedIn profiles using Apify API"""
    
    def __init__(self, api_token: str, actor_id: str):
        self.api_token = api_token
        self.actor_id = actor_id
        self.base_url = "https://api.apify.com/v2"
        
    async def scrape_profiles(self, linkedin_urls: List[str]) -> List[LinkedInProfile]:
        """
        Scrape multiple LinkedIn profiles in batch
        Captures ALL available data including profile pictures
        """
        profiles = []
        
        # Run Apify actor for each profile
        for url in linkedin_urls:
            try:
                profile_data = await self._scrape_single_profile(url)
                if profile_data:
                    profile = self._parse_profile_data(url, profile_data)
                    profiles.append(profile)
            except Exception as e:
                print(f"Error scraping {url}: {str(e)}")
                # Create minimal profile with URL only
                profiles.append(LinkedInProfile(url=url, full_name="Profile unavailable"))
                
        return profiles
    
    async def _scrape_single_profile(self, linkedin_url: str) -> Optional[Dict[str, Any]]:
        """Scrape a single LinkedIn profile using Apify"""
        
        # Prepare input for Apify actor
        actor_input = {
            "startUrls": [{"url": linkedin_url}],
            "includeUnlistedFields": True,  # Get ALL available fields
            "includeSkills": True,
            "includeEducation": True,
            "includeExperience": True,
            "includeCertifications": True,
            "includeVolunteering": True,
            "includePublications": True,
            "includePatents": True,
            "includeCourses": True,
            "includeProjects": True,
            "includeHonorsAwards": True,
            "includeLanguages": True,
            "includeImages": True,  # IMPORTANT: Include profile and background images
            "saveHtml": False,
            "maxDelay": 5,
            "minDelay": 1
        }
        
        async with aiohttp.ClientSession() as session:
            # Start the actor run
            start_url = f"{self.base_url}/acts/{self.actor_id}/runs"
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            
            async with session.post(start_url, json=actor_input, headers=headers) as response:
                if response.status != 201:
                    print(f"Failed to start Apify actor: {response.status}")
                    return None
                
                run_data = await response.json()
                run_id = run_data["data"]["id"]
            
            # Wait for completion and get results
            return await self._wait_for_results(session, run_id, headers)
    
    async def _wait_for_results(self, session: aiohttp.ClientSession, run_id: str, headers: Dict) -> Optional[Dict[str, Any]]:
        """Wait for Apify run to complete and fetch results"""
        
        max_wait_time = 120  # 2 minutes max
        wait_interval = 5
        elapsed_time = 0
        
        while elapsed_time < max_wait_time:
            # Check run status
            status_url = f"{self.base_url}/actor-runs/{run_id}"
            async with session.get(status_url, headers=headers) as response:
                if response.status == 200:
                    run_info = await response.json()
                    status = run_info["data"]["status"]
                    
                    if status == "SUCCEEDED":
                        # Get the results
                        dataset_id = run_info["data"]["defaultDatasetId"]
                        results_url = f"{self.base_url}/datasets/{dataset_id}/items"
                        
                        async with session.get(results_url, headers=headers) as results_response:
                            if results_response.status == 200:
                                results = await results_response.json()
                                return results[0] if results else None
                    
                    elif status in ["FAILED", "ABORTED", "TIMED-OUT"]:
                        print(f"Apify run failed with status: {status}")
                        return None
            
            # Wait before checking again
            await asyncio.sleep(wait_interval)
            elapsed_time += wait_interval
        
        print(f"Apify run timed out after {max_wait_time} seconds")
        return None
    
    def _parse_profile_data(self, url: str, raw_data: Dict[str, Any]) -> LinkedInProfile:
        """Parse raw Apify data into LinkedInProfile model"""
        
        # Parse work experiences
        work_experiences = []
        if raw_data.get("experience"):
            for exp in raw_data["experience"]:
                work_exp = WorkExperience(
                    title=exp.get("title"),
                    company=exp.get("companyName"),
                    description=exp.get("description"),
                    location=exp.get("location"),
                    start_date=exp.get("startDate"),
                    end_date=exp.get("endDate"),
                    duration=exp.get("duration"),
                    is_current=exp.get("endDate") is None or exp.get("endDate") == "Present"
                )
                work_experiences.append(work_exp)
        
        # Parse education
        education_list = []
        if raw_data.get("education"):
            for edu in raw_data["education"]:
                education = Education(
                    school=edu.get("schoolName"),
                    degree=edu.get("degreeName"),
                    field_of_study=edu.get("fieldOfStudy"),
                    start_date=edu.get("startDate"),
                    end_date=edu.get("endDate"),
                    description=edu.get("description")
                )
                education_list.append(education)
        
        # Parse skills
        skills_list = []
        if raw_data.get("skills"):
            for skill in raw_data["skills"]:
                skill_obj = Skill(
                    name=skill.get("name"),
                    endorsements=skill.get("endorsements", 0)
                )
                skills_list.append(skill_obj)
        
        # Extract current position info
        current_position = None
        current_company = None
        if work_experiences:
            current_work = next((exp for exp in work_experiences if exp.is_current), work_experiences[0])
            current_position = current_work.title
            current_company = current_work.company
        
        # Create LinkedInProfile with ALL available data
        profile = LinkedInProfile(
            url=url,
            full_name=raw_data.get("fullName"),
            first_name=raw_data.get("firstName"),
            last_name=raw_data.get("lastName"),
            headline=raw_data.get("headline"),
            summary=raw_data.get("summary"),
            
            # IMPORTANT: Profile images for final report
            profile_image_url=raw_data.get("profileImageUrl") or raw_data.get("photoUrl"),
            background_image_url=raw_data.get("backgroundImageUrl"),
            
            current_company=current_company,
            current_position=current_position,
            location=raw_data.get("location"),
            industry=raw_data.get("industry"),
            
            work_experiences=work_experiences,
            education=education_list,
            skills=skills_list,
            
            connections_count=raw_data.get("connectionsCount"),
            followers_count=raw_data.get("followersCount"),
            
            # Additional data for comprehensive analysis
            languages=raw_data.get("languages", []),
            certifications=raw_data.get("certifications", []),
            volunteer_experiences=raw_data.get("volunteering", []),
            publications=raw_data.get("publications", []),
            patents=raw_data.get("patents", []),
            courses=raw_data.get("courses", []),
            projects=raw_data.get("projects", []),
            honors_awards=raw_data.get("honorsAwards", []),
            
            scraped_at=datetime.now(),
            raw_data=raw_data  # Store ALL raw data for future use
        )
        
        return profile

# Utility function to create scraper instance
def create_apify_scraper() -> ApifyLinkedInScraper:
    """Create Apify scraper with environment variables"""
    api_token = os.getenv("APIFY_API_TOKEN")
    actor_id = os.getenv("APIFY_LINKEDIN_ACTOR_ID")
    
    if not api_token or not actor_id:
        raise ValueError("APIFY_API_TOKEN and APIFY_LINKEDIN_ACTOR_ID must be set in environment variables")
    
    return ApifyLinkedInScraper(api_token, actor_id)