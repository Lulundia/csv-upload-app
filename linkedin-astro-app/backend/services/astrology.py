import json
import random
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from ..models.profile import ProfileWithZodiac
from ..models.compatibility import CompatibilityPair, TeamCompatibilityReport

class AstrologyService:
    """Service for zodiac compatibility analysis and fun descriptions"""
    
    def __init__(self):
        self.zodiac_data = self._load_zodiac_data()
        
    def _load_zodiac_data(self) -> Dict:
        """Load zodiac data from shared JSON file"""
        try:
            # Go up to project root and find shared data
            current_dir = Path(__file__).parent
            zodiac_file = current_dir.parent.parent.parent / "shared" / "zodiac_data.json"
            
            with open(zodiac_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading zodiac data: {e}")
            # Return minimal fallback data
            return {
                "zodiac_signs": {},
                "compatibility_matrix": {},
                "compatibility_descriptions": {
                    "high": ["Great compatibility! ✨"],
                    "medium": ["Good potential! 🌟"],
                    "low": ["Interesting dynamic! 🤔"]
                }
            }
    
    def get_zodiac_info(self, sign: str) -> Dict:
        """Get detailed information about a zodiac sign"""
        sign_lower = sign.lower()
        return self.zodiac_data.get("zodiac_signs", {}).get(sign_lower, {
            "name": sign.title(),
            "emoji": "⭐",
            "element": "Unknown",
            "work_traits": ["Professional", "Dedicated"],
            "strengths": ["Experienced"],
            "challenges": ["Analysis needed"]
        })
    
    def calculate_compatibility(self, sign1: str, sign2: str) -> Tuple[int, str]:
        """
        Calculate compatibility score between two zodiac signs
        Returns (score, level) where level is 'high', 'medium', or 'low'
        """
        sign1_lower = sign1.lower()
        sign2_lower = sign2.lower()
        
        compatibility_matrix = self.zodiac_data.get("compatibility_matrix", {})
        
        # Get base compatibility score
        score = compatibility_matrix.get(sign1_lower, {}).get(sign2_lower, 70)
        
        # Determine compatibility level
        if score >= 85:
            level = "high"
        elif score >= 65:
            level = "medium"
        else:
            level = "low"
            
        return score, level
    
    def get_compatibility_description(self, sign1: str, sign2: str, level: str) -> str:
        """Get a fun compatibility description for two signs"""
        descriptions = self.zodiac_data.get("compatibility_descriptions", {}).get(level, [
            f"{sign1} + {sign2}: An interesting cosmic combination!"
        ])
        
        # Pick a random description and format it
        template = random.choice(descriptions)
        return template.format(sign1=sign1.title(), sign2=sign2.title())
    
    def analyze_pair_compatibility(self, person1: ProfileWithZodiac, person2: ProfileWithZodiac) -> CompatibilityPair:
        """Analyze compatibility between two people"""
        
        # Get base zodiac compatibility
        score, level = self.calculate_compatibility(person1.zodiac_sign, person2.zodiac_sign)
        description = self.get_compatibility_description(person1.zodiac_sign, person2.zodiac_sign, level)
        
        # Adjust score based on professional context
        adjusted_score = self._adjust_score_for_context(score, person1, person2)
        
        # Determine final level based on adjusted score
        if adjusted_score >= 85:
            final_level = "high"
        elif adjusted_score >= 65:
            final_level = "medium"
        else:
            final_level = "low"
        
        # Generate insights based on zodiac traits
        work_dynamic = self._generate_work_dynamic(person1, person2, final_level)
        communication_insight = self._generate_communication_insight(person1, person2)
        potential_conflicts = self._identify_potential_conflicts(person1, person2)
        strengths = self._identify_strengths(person1, person2)
        recommendations = self._generate_recommendations(person1, person2, final_level)
        
        return CompatibilityPair(
            person1=person1,
            person2=person2,
            compatibility_score=adjusted_score,
            compatibility_level=final_level,
            description=description,
            work_dynamic=work_dynamic,
            communication_style=communication_insight,
            potential_conflicts=potential_conflicts,
            strengths=strengths,
            recommendations=recommendations
        )
    
    def generate_team_report(self, main_user: ProfileWithZodiac, team_members: List[ProfileWithZodiac]) -> Dict:
        """Generate comprehensive team compatibility analysis"""
        
        all_members = [main_user] + team_members
        compatibility_pairs = []
        
        # Analyze all pairs
        for i, person1 in enumerate(all_members):
            for j, person2 in enumerate(all_members[i+1:], i+1):
                pair = self.analyze_pair_compatibility(person1, person2)
                compatibility_pairs.append(pair)
        
        # Calculate team metrics
        total_score = sum(pair.compatibility_score for pair in compatibility_pairs)
        team_average = total_score / len(compatibility_pairs) if compatibility_pairs else 70
        
        # Zodiac breakdown
        zodiac_breakdown = {}
        for member in all_members:
            sign = member.zodiac_sign.title()
            zodiac_breakdown[sign] = zodiac_breakdown.get(sign, 0) + 1
        
        # Find most/least compatible pairs
        most_compatible = max(compatibility_pairs, key=lambda p: p.compatibility_score) if compatibility_pairs else None
        most_challenging = min(compatibility_pairs, key=lambda p: p.compatibility_score) if compatibility_pairs else None
        
        # Generate team insights
        team_strengths = self._analyze_team_strengths(all_members)
        team_challenges = self._analyze_team_challenges(all_members)
        team_summary = self._generate_team_summary(all_members, team_average, zodiac_breakdown)
        
        return {
            "compatibility_pairs": compatibility_pairs,
            "team_average_score": round(team_average, 1),
            "team_dynamic_summary": team_summary,
            "team_strengths": team_strengths,
            "team_challenges": team_challenges,
            "team_zodiac_breakdown": zodiac_breakdown,
            "most_compatible_pair": most_compatible,
            "most_challenging_pair": most_challenging
        }
    
    def _adjust_score_for_context(self, base_score: int, person1: ProfileWithZodiac, person2: ProfileWithZodiac) -> int:
        """Adjust compatibility score based on professional context"""
        
        adjustments = 0
        
        # Same company bonus
        if (person1.profile.current_company and person2.profile.current_company and 
            person1.profile.current_company.lower() == person2.profile.current_company.lower()):
            adjustments += 5
        
        # Same industry bonus
        if (person1.profile.industry and person2.profile.industry and 
            person1.profile.industry.lower() == person2.profile.industry.lower()):
            adjustments += 3
        
        # Complementary roles (one manager, one individual contributor)
        p1_title = (person1.profile.current_position or "").lower()
        p2_title = (person2.profile.current_position or "").lower()
        
        manager_keywords = ["manager", "director", "vp", "president", "ceo", "cto", "cfo", "lead", "head"]
        p1_is_manager = any(keyword in p1_title for keyword in manager_keywords)
        p2_is_manager = any(keyword in p2_title for keyword in manager_keywords)
        
        if p1_is_manager != p2_is_manager:  # One manager, one not
            adjustments += 7
        
        # Apply adjustments but keep within reasonable bounds
        final_score = base_score + adjustments
        return max(30, min(100, final_score))  # Keep between 30-100
    
    def _generate_work_dynamic(self, person1: ProfileWithZodiac, person2: ProfileWithZodiac, level: str) -> str:
        """Generate work dynamic description"""
        
        sign1_info = self.get_zodiac_info(person1.zodiac_sign)
        sign2_info = self.get_zodiac_info(person2.zodiac_sign)
        
        if level == "high":
            return f"{person1.zodiac_sign.title()} and {person2.zodiac_sign.title()} create a powerful work synergy. Their {sign1_info.get('element', 'unknown')} and {sign2_info.get('element', 'unknown')} energies complement each other perfectly in professional settings."
        elif level == "medium":
            return f"{person1.zodiac_sign.title()} and {person2.zodiac_sign.title()} have good potential for collaboration. While they approach work differently, their diverse perspectives can lead to innovative solutions."
        else:
            return f"{person1.zodiac_sign.title()} and {person2.zodiac_sign.title()} bring contrasting work styles that require conscious effort to harmonize. Their differences can be strengths with proper communication."
    
    def _generate_communication_insight(self, person1: ProfileWithZodiac, person2: ProfileWithZodiac) -> str:
        """Generate communication style insight"""
        
        # This could be enhanced with more sophisticated logic based on elements, etc.
        sign1 = person1.zodiac_sign.title()
        sign2 = person2.zodiac_sign.title()
        
        communication_patterns = {
            "fire_fire": "High energy, direct communication with lots of enthusiasm",
            "fire_earth": "Fast-paced meets methodical - needs patience from both sides",
            "fire_air": "Dynamic conversations with quick idea exchanges",
            "fire_water": "Passionate meets intuitive - emotion-driven discussions",
            "earth_earth": "Practical, detailed conversations focused on results",
            "earth_air": "Structured meets conceptual - good for planning sessions",
            "earth_water": "Steady and supportive communication style",
            "air_air": "Intellectual exchanges with lots of brainstorming",
            "air_water": "Logical meets emotional - balanced perspective sharing",
            "water_water": "Intuitive, empathetic communication with emotional depth"
        }
        
        # Get elements (simplified mapping)
        elements = {
            "aries": "fire", "leo": "fire", "sagittarius": "fire",
            "taurus": "earth", "virgo": "earth", "capricorn": "earth",
            "gemini": "air", "libra": "air", "aquarius": "air",
            "cancer": "water", "scorpio": "water", "pisces": "water"
        }
        
        elem1 = elements.get(person1.zodiac_sign.lower(), "air")
        elem2 = elements.get(person2.zodiac_sign.lower(), "air")
        
        pattern_key = f"{elem1}_{elem2}" if elem1 <= elem2 else f"{elem2}_{elem1}"
        
        return communication_patterns.get(pattern_key, f"{sign1} and {sign2} communicate in their own unique way")
    
    def _identify_potential_conflicts(self, person1: ProfileWithZodiac, person2: ProfileWithZodiac) -> List[str]:
        """Identify potential workplace conflicts based on zodiac traits"""
        
        sign1_info = self.get_zodiac_info(person1.zodiac_sign)
        sign2_info = self.get_zodiac_info(person2.zodiac_sign)
        
        conflicts = []
        
        # Extract potential conflicts from zodiac challenges
        challenges1 = sign1_info.get("challenges", [])
        challenges2 = sign2_info.get("challenges", [])
        
        if "Impatience" in challenges1 and "Slow adaptation" in challenges2:
            conflicts.append("Pace differences - fast vs methodical approaches")
        
        if "Perfectionism" in challenges1 or "Perfectionism" in challenges2:
            conflicts.append("Different standards for quality and detail")
        
        if "Ego" in challenges1 and "Ego" in challenges2:
            conflicts.append("Potential leadership or recognition conflicts")
        
        if not conflicts:
            conflicts = ["Minor communication style differences", "Different work pace preferences"]
        
        return conflicts[:2]  # Keep it concise
    
    def _identify_strengths(self, person1: ProfileWithZodiac, person2: ProfileWithZodiac) -> List[str]:
        """Identify collaboration strengths"""
        
        sign1_info = self.get_zodiac_info(person1.zodiac_sign)
        sign2_info = self.get_zodiac_info(person2.zodiac_sign)
        
        strengths1 = sign1_info.get("strengths", [])
        strengths2 = sign2_info.get("strengths", [])
        
        combined_strengths = []
        
        # Look for complementary strengths
        if "Leadership" in strengths1 and "Collaboration" in strengths2:
            combined_strengths.append("Strong leadership with collaborative support")
        elif "Creativity" in strengths1 and "Organization" in strengths2:
            combined_strengths.append("Creative ideas with structured execution")
        elif "Innovation" in strengths1 and "Stability" in strengths2:
            combined_strengths.append("Innovation balanced with practical stability")
        
        # Add diverse perspectives
        combined_strengths.append(f"{person1.zodiac_sign.title()} {strengths1[0] if strengths1 else 'energy'} + {person2.zodiac_sign.title()} {strengths2[0] if strengths2 else 'approach'}")
        
        if len(combined_strengths) < 3:
            combined_strengths.append("Diverse professional backgrounds and perspectives")
        
        return combined_strengths[:3]
    
    def _generate_recommendations(self, person1: ProfileWithZodiac, person2: ProfileWithZodiac, level: str) -> str:
        """Generate actionable recommendations"""
        
        if level == "high":
            return f"Leverage your natural compatibility! {person1.zodiac_sign.title()} should focus on their strengths while {person2.zodiac_sign.title()} provides complementary support. Regular check-ins will keep this cosmic collaboration on track."
        elif level == "medium":
            return f"Schedule regular communication to align your different approaches. {person1.zodiac_sign.title()} and {person2.zodiac_sign.title()} should be explicit about expectations and play to each other's strengths."
        else:
            return f"Success requires intentional effort! Create structured communication protocols, clearly define roles, and celebrate your different perspectives as team assets rather than obstacles."
    
    def _analyze_team_strengths(self, team: List[ProfileWithZodiac]) -> List[str]:
        """Analyze overall team strengths based on zodiac mix"""
        
        strengths = set()
        elements = {"fire": 0, "earth": 0, "air": 0, "water": 0}
        
        element_map = {
            "aries": "fire", "leo": "fire", "sagittarius": "fire",
            "taurus": "earth", "virgo": "earth", "capricorn": "earth",
            "gemini": "air", "libra": "air", "aquarius": "air",
            "cancer": "water", "scorpio": "water", "pisces": "water"
        }
        
        for member in team:
            sign_info = self.get_zodiac_info(member.zodiac_sign)
            strengths.update(sign_info.get("strengths", []))
            
            element = element_map.get(member.zodiac_sign.lower(), "air")
            elements[element] += 1
        
        team_strengths = []
        
        # Element balance insights
        if all(count > 0 for count in elements.values()):
            team_strengths.append("Perfect elemental balance - all perspectives represented")
        elif elements["fire"] > 0 and elements["earth"] > 0:
            team_strengths.append("Great execution potential - vision meets implementation")
        elif elements["air"] > 0 and elements["water"] > 0:
            team_strengths.append("Strong communication and emotional intelligence")
        
        # Add top individual strengths
        common_strengths = list(strengths)[:2]
        team_strengths.extend(common_strengths)
        
        return team_strengths[:3]
    
    def _analyze_team_challenges(self, team: List[ProfileWithZodiac]) -> List[str]:
        """Analyze potential team challenges"""
        
        challenges = set()
        for member in team:
            sign_info = self.get_zodiac_info(member.zodiac_sign)
            challenges.update(sign_info.get("challenges", []))
        
        team_challenges = []
        
        if len(set(member.zodiac_sign for member in team)) == 1:
            team_challenges.append("Similar perspectives - may need diverse viewpoints")
        
        if "Perfectionism" in challenges:
            team_challenges.append("Managing perfectionist tendencies and deadlines")
        
        if "Impatience" in challenges:
            team_challenges.append("Balancing urgency with thorough planning")
        
        if not team_challenges:
            team_challenges = ["Coordinating different work styles", "Maintaining clear communication"]
        
        return team_challenges[:2]
    
    def _generate_team_summary(self, team: List[ProfileWithZodiac], avg_score: float, zodiac_breakdown: Dict[str, int]) -> str:
        """Generate fun team summary"""
        
        dominant_signs = [sign for sign, count in zodiac_breakdown.items() if count > 1]
        
        if avg_score >= 85:
            vibe = "cosmic powerhouse"
        elif avg_score >= 70:
            vibe = "harmonious constellation"
        else:
            vibe = "dynamically diverse galaxy"
        
        if dominant_signs:
            return f"This team is a {vibe} with strong {', '.join(dominant_signs)} energy! With {len(team)} unique personalities spanning {len(zodiac_breakdown)} zodiac signs, you've got the cosmic ingredients for both innovation and solid execution."
        else:
            return f"This team is a {vibe} with incredible zodiac diversity! Each of your {len(team)} members brings a unique astrological perspective, creating a well-rounded cosmic collective that can tackle any challenge."

# Utility function
def create_astrology_service() -> AstrologyService:
    """Create astrology service instance"""
    return AstrologyService()