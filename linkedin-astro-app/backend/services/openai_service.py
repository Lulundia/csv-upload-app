import os
import json
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from ..models.profile import ProfileWithZodiac, LinkedInProfile

class OpenAIAnalysisService:
    """Service to analyze LinkedIn profiles using OpenAI"""
    
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        
    async def analyze_work_style(self, profile: LinkedInProfile, zodiac_sign: str) -> Dict[str, Any]:
        """
        Analyze a person's work style using ALL available LinkedIn data
        Returns comprehensive insights for compatibility analysis
        """
        
        # Build comprehensive profile context from ALL scraped data
        profile_context = self._build_profile_context(profile)
        
        prompt = f"""
        Analyze this LinkedIn profile combined with their zodiac sign to generate comprehensive work style insights.
        
        PROFILE DATA:
        {profile_context}
        
        ZODIAC SIGN: {zodiac_sign}
        
        Please provide a detailed analysis in JSON format with these fields:
        
        {{
            "work_style_analysis": "2-3 sentence summary of their work style",
            "personality_traits": ["trait1", "trait2", "trait3", "trait4", "trait5"],
            "leadership_style": "Description of how they lead or follow",
            "communication_style": "How they communicate and collaborate",
            "strengths_in_workplace": ["strength1", "strength2", "strength3"],
            "potential_challenges": ["challenge1", "challenge2", "challenge3"],
            "ideal_work_environment": "Description of their ideal workplace",
            "collaboration_preferences": "How they prefer to work with others",
            "decision_making_style": "How they make decisions",
            "stress_response": "How they handle workplace stress",
            "motivation_drivers": ["driver1", "driver2", "driver3"],
            "career_patterns": "Analysis of their career progression and patterns",
            "industry_expertise": "Their areas of expertise based on experience",
            "networking_style": "How they build professional relationships"
        }}
        
        Base your analysis on:
        1. Their job titles, companies, and career progression
        2. Skills and endorsements patterns
        3. Education background and achievements
        4. Industry experience and expertise areas
        5. Leadership roles and responsibilities
        6. Project involvement and certifications
        7. Zodiac sign characteristics and work traits
        8. Any other available data (volunteering, publications, etc.)
        
        Make the analysis professional yet engaging, suitable for a fun workplace compatibility report.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert workplace psychologist and astrology consultant. Provide insightful, accurate, and engaging analysis based on professional data and zodiac characteristics."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            analysis_text = response.choices[0].message.content
            
            # Parse JSON response
            try:
                analysis = json.loads(analysis_text)
                return analysis
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    "work_style_analysis": analysis_text[:200] + "...",
                    "personality_traits": ["Analytical", "Professional", "Goal-oriented"],
                    "leadership_style": "Collaborative approach",
                    "communication_style": "Clear and direct",
                    "strengths_in_workplace": ["Experienced", "Skilled", "Dedicated"],
                    "potential_challenges": ["May need more data for detailed analysis"],
                    "ideal_work_environment": "Professional collaborative setting",
                    "collaboration_preferences": "Team-oriented",
                    "decision_making_style": "Data-driven",
                    "stress_response": "Methodical problem-solving",
                    "motivation_drivers": ["Achievement", "Growth", "Impact"],
                    "career_patterns": "Steady professional growth",
                    "industry_expertise": profile.industry or "Various fields",
                    "networking_style": "Professional relationship building"
                }
                
        except Exception as e:
            print(f"Error in OpenAI analysis: {str(e)}")
            # Return default analysis
            return {
                "work_style_analysis": f"Professional {zodiac_sign} with experience in {profile.industry or 'their field'}",
                "personality_traits": ["Professional", "Experienced", "Dedicated"],
                "leadership_style": "Collaborative",
                "communication_style": "Direct",
                "strengths_in_workplace": ["Experience", "Skills", "Reliability"],
                "potential_challenges": ["Analysis unavailable"],
                "ideal_work_environment": "Collaborative workspace",
                "collaboration_preferences": "Team-focused",
                "decision_making_style": "Thoughtful",
                "stress_response": "Problem-solving oriented",
                "motivation_drivers": ["Success", "Growth"],
                "career_patterns": "Professional development",
                "industry_expertise": profile.industry or "Professional field",
                "networking_style": "Relationship-focused"
            }
    
    async def generate_compatibility_analysis(self, person1: ProfileWithZodiac, person2: ProfileWithZodiac, base_score: int) -> Dict[str, Any]:
        """
        Generate detailed compatibility analysis between two people
        Uses their comprehensive work style analyses and zodiac compatibility
        """
        
        prompt = f"""
        Generate a detailed workplace compatibility analysis between these two professionals:
        
        PERSON 1: {person1.profile.full_name} ({person1.zodiac_sign})
        - Current Role: {person1.profile.current_position} at {person1.profile.current_company}
        - Work Style: {person1.work_style_analysis}
        - Traits: {', '.join(person1.personality_traits or [])}
        - Leadership: {person1.leadership_style}
        - Communication: {person1.communication_style}
        
        PERSON 2: {person2.profile.full_name} ({person2.zodiac_sign})
        - Current Role: {person2.profile.current_position} at {person2.profile.current_company}
        - Work Style: {person2.work_style_analysis}
        - Traits: {', '.join(person2.personality_traits or [])}
        - Leadership: {person2.leadership_style}
        - Communication: {person2.communication_style}
        
        BASE COMPATIBILITY SCORE: {base_score}/100
        
        Provide analysis in JSON format:
        {{
            "work_dynamic": "How they work together (2-3 sentences)",
            "communication_style": "How their communication styles mesh",
            "potential_conflicts": ["conflict1", "conflict2"],
            "strengths": ["strength1", "strength2", "strength3"],
            "recommendations": "Advice for working together effectively",
            "collaboration_score": {base_score},
            "fun_insight": "A playful observation about their zodiac + work combo"
        }}
        
        Make it professional but fun, like a workplace horoscope!
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a workplace compatibility expert who combines professional psychology with astrology insights to create engaging, helpful analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=800
            )
            
            analysis_text = response.choices[0].message.content
            
            try:
                analysis = json.loads(analysis_text)
                return analysis
            except json.JSONDecodeError:
                return {
                    "work_dynamic": f"{person1.zodiac_sign} and {person2.zodiac_sign} create an interesting workplace dynamic",
                    "communication_style": "Their communication styles complement each other",
                    "potential_conflicts": ["Different work paces", "Communication preferences"],
                    "strengths": ["Diverse perspectives", "Complementary skills", "Mutual respect"],
                    "recommendations": "Focus on clear communication and leveraging each other's strengths",
                    "collaboration_score": base_score,
                    "fun_insight": f"When {person1.zodiac_sign} meets {person2.zodiac_sign}, expect cosmic collaboration!"
                }
                
        except Exception as e:
            print(f"Error in compatibility analysis: {str(e)}")
            return {
                "work_dynamic": f"{person1.zodiac_sign} and {person2.zodiac_sign} working relationship",
                "communication_style": "Professional communication",
                "potential_conflicts": ["Different approaches"],
                "strengths": ["Diverse skills", "Professional experience"],
                "recommendations": "Maintain open communication",
                "collaboration_score": base_score,
                "fun_insight": "Every zodiac combination has its cosmic potential!"
            }
    
    async def generate_team_summary(self, team_analysis: Dict[str, Any]) -> str:
        """Generate an overall team dynamic summary"""
        
        prompt = f"""
        Generate a fun, engaging team summary based on this analysis:
        
        TEAM DATA:
        {json.dumps(team_analysis, indent=2)}
        
        Write a 2-3 sentence summary that captures:
        1. The overall team vibe
        2. Key strengths
        3. Fun zodiac observations
        
        Make it sound like "Spotify Wrapped meets workplace astrology" - professional but playful!
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a creative workplace analyst who writes engaging team summaries with astrological flair."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,
                max_tokens=200
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating team summary: {str(e)}")
            return "This team brings together a cosmic mix of talents and personalities, creating a unique workplace constellation!"
    
    def _build_profile_context(self, profile: LinkedInProfile) -> str:
        """Build comprehensive context from ALL available profile data"""
        
        context_parts = []
        
        # Basic info
        if profile.full_name:
            context_parts.append(f"Name: {profile.full_name}")
        if profile.headline:
            context_parts.append(f"Headline: {profile.headline}")
        if profile.summary:
            context_parts.append(f"Summary: {profile.summary}")
        if profile.location:
            context_parts.append(f"Location: {profile.location}")
        if profile.industry:
            context_parts.append(f"Industry: {profile.industry}")
        
        # Current position
        if profile.current_position and profile.current_company:
            context_parts.append(f"Current Role: {profile.current_position} at {profile.current_company}")
        
        # Work experience
        if profile.work_experiences:
            context_parts.append("Work Experience:")
            for i, exp in enumerate(profile.work_experiences[:5]):  # Top 5 experiences
                exp_text = f"  {i+1}. {exp.title or 'Unknown'} at {exp.company or 'Unknown'}"
                if exp.duration:
                    exp_text += f" ({exp.duration})"
                if exp.description:
                    exp_text += f" - {exp.description[:100]}..."
                context_parts.append(exp_text)
        
        # Education
        if profile.education:
            context_parts.append("Education:")
            for edu in profile.education:
                edu_text = f"  - {edu.degree or 'Degree'} in {edu.field_of_study or 'Field'} from {edu.school or 'Institution'}"
                context_parts.append(edu_text)
        
        # Skills
        if profile.skills:
            skills_text = "Skills: " + ", ".join([skill.name for skill in profile.skills[:10] if skill.name])
            context_parts.append(skills_text)
        
        # Additional qualifications
        if profile.certifications:
            context_parts.append(f"Certifications: {len(profile.certifications)} certifications")
        
        if profile.languages:
            context_parts.append(f"Languages: {', '.join(profile.languages)}")
        
        if profile.volunteer_experiences:
            context_parts.append(f"Volunteering: {len(profile.volunteer_experiences)} volunteer experiences")
        
        if profile.publications:
            context_parts.append(f"Publications: {len(profile.publications)} publications")
        
        if profile.projects:
            context_parts.append(f"Projects: {len(profile.projects)} projects")
        
        if profile.connections_count:
            context_parts.append(f"LinkedIn Connections: {profile.connections_count}")
        
        return "\n".join(context_parts)

# Utility function
def create_openai_service() -> OpenAIAnalysisService:
    """Create OpenAI service with environment variable"""
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError("OPENAI_API_KEY must be set in environment variables")
    
    return OpenAIAnalysisService(api_key)