from datetime import datetime, timedelta
import json

class AdvisingService:
    """Enhanced college and financial aid advising service"""
    
    def __init__(self):
        self.current_year = datetime.now().year
        self.senior_year = self.current_year if datetime.now().month >= 8 else self.current_year - 1
    
    def get_fafsa_timeline(self, graduation_year=None):
        """Get FAFSA application timeline"""
        if not graduation_year:
            graduation_year = self.senior_year + 1
        
        timeline = {
            "October 1": f"FAFSA opens for {graduation_year-1}-{graduation_year} school year",
            "December 1": "Priority deadline for many state aid programs",
            "January 1": "CSS Profile deadline for many private schools",
            "March 1": "Common priority deadline for institutional aid",
            "June 30": f"Final deadline to submit FAFSA for {graduation_year-1}-{graduation_year}"
        }
        
        return timeline
    
    def calculate_efc_estimate(self, parent_income, student_income=0, assets=0, family_size=4):
        """Rough EFC (Expected Family Contribution) estimate"""
        try:
            parent_income = float(parent_income)
            student_income = float(student_income)
            assets = float(assets)
            family_size = int(family_size)
            
            # Simplified EFC calculation (actual formula is much more complex)
            income_allowance = 25000 + (family_size - 2) * 3000
            available_income = max(0, parent_income - income_allowance)
            
            # Progressive tax on available income
            if available_income <= 15000:
                income_assessment = available_income * 0.22
            elif available_income <= 40000:
                income_assessment = 15000 * 0.22 + (available_income - 15000) * 0.25
            else:
                income_assessment = 15000 * 0.22 + 25000 * 0.25 + (available_income - 40000) * 0.47
            
            # Asset assessment (simplified)
            asset_allowance = 10000 if family_size <= 2 else 15000
            available_assets = max(0, assets - asset_allowance)
            asset_assessment = available_assets * 0.12
            
            # Student contribution
            student_contribution = max(0, student_income - 6970) * 0.5
            
            efc = int(income_assessment + asset_assessment + student_contribution)
            
            return {
                "estimated_efc": efc,
                "explanation": f"Based on parent income ${parent_income:,.0f}, student income ${student_income:,.0f}, assets ${assets:,.0f}, family size {family_size}",
                "note": "This is a rough estimate. Use the official FAFSA4caster for more accuracy."
            }
        except Exception as e:
            return {"error": f"Error calculating EFC: {str(e)}"}
    
    def get_application_checklist(self, grade_level="senior"):
        """Get college application checklist by grade level"""
        checklists = {
            "freshman": [
                "Focus on grades - GPA is crucial",
                "Explore extracurricular activities",
                "Take challenging courses",
                "Start building study habits"
            ],
            "sophomore": [
                "Continue strong academic performance",
                "Take PSAT for practice",
                "Explore career interests",
                "Consider leadership opportunities",
                "Start college research"
            ],
            "junior": [
                "Take SAT/ACT tests",
                "Take SAT Subject Tests if needed",
                "Research colleges seriously",
                "Visit college campuses",
                "Build relationships with teachers for recommendations",
                "Create preliminary college list"
            ],
            "senior": [
                "Complete college applications",
                "Submit FAFSA (after October 1)",
                "Apply for scholarships",
                "Request final transcripts",
                "Make final college decision",
                "Submit enrollment deposit"
            ]
        }
        
        return checklists.get(grade_level.lower(), checklists["senior"])
    
    def scholarship_search_tips(self):
        """Provide scholarship search guidance"""
        return {
            "where_to_look": [
                "Your school's guidance office",
                "College financial aid offices", 
                "Fastweb.com, Scholarships.com",
                "Local community organizations",
                "Your parents' employers",
                "Professional associations"
            ],
            "application_tips": [
                "Start early - many deadlines are in fall",
                "Read requirements carefully",
                "Tailor essays to each scholarship",
                "Get strong letters of recommendation",
                "Meet all deadlines",
                "Apply to many scholarships, not just large ones"
            ],
            "essay_topics": [
                "Academic and career goals",
                "Leadership experiences", 
                "Community service",
                "Overcoming challenges",
                "Why you deserve the scholarship"
            ]
        }
