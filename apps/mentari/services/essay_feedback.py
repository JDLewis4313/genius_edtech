import re
from textstat import flesch_reading_ease, flesch_kincaid_grade

class EssayFeedbackService:
    """Enhanced writing and essay feedback service"""
    
    def analyze_college_essay(self, text, essay_type="personal_statement"):
        """Comprehensive college essay analysis"""
        analysis = {
            "word_count": len(text.split()),
            "character_count": len(text),
            "readability": self._assess_readability(text),
            "structure": self._analyze_structure(text),
            "content": self._analyze_content(text, essay_type),
            "style": self._analyze_style(text),
            "suggestions": self._generate_suggestions(text, essay_type)
        }
        
        return analysis
    
    def _assess_readability(self, text):
        """Assess text readability"""
        try:
            ease_score = flesch_reading_ease(text)
            grade_level = flesch_kincaid_grade(text)
            
            if ease_score >= 70:
                ease_desc = "Easy to read"
            elif ease_score >= 50:
                ease_desc = "Moderate difficulty"
            else:
                ease_desc = "Difficult to read"
            
            return {
                "flesch_ease": ease_score,
                "grade_level": grade_level,
                "description": ease_desc,
                "recommendation": "Aim for 8th-10th grade level for college essays"
            }
        except:
            return {"error": "Could not assess readability"}
    
    def _analyze_structure(self, text):
        """Analyze essay structure"""
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        avg_sentences_per_paragraph = len(sentences) / len(paragraphs) if paragraphs else 0
        avg_words_per_sentence = len(text.split()) / len(sentences) if sentences else 0
        
        feedback = []
        
        if len(paragraphs) < 3:
            feedback.append("Consider adding more paragraphs for better organization")
        elif len(paragraphs) > 7:
            feedback.append("Consider combining some paragraphs for better flow")
        
        if avg_words_per_sentence > 25:
            feedback.append("Some sentences might be too long - consider breaking them up")
        elif avg_words_per_sentence < 10:
            feedback.append("Consider combining some short sentences for better flow")
        
        return {
            "paragraph_count": len(paragraphs),
            "sentence_count": len(sentences),
            "avg_sentences_per_paragraph": round(avg_sentences_per_paragraph, 1),
            "avg_words_per_sentence": round(avg_words_per_sentence, 1),
            "feedback": feedback
        }
    
    def _analyze_content(self, text, essay_type):
        """Analyze essay content based on type"""
        text_lower = text.lower()
        
        content_analysis = {
            "personal_voice": self._check_personal_voice(text),
            "specific_examples": self._check_specific_examples(text),
            "essay_type_requirements": self._check_essay_requirements(text, essay_type)
        }
        
        return content_analysis
    
    def _check_personal_voice(self, text):
        """Check for personal voice and perspective"""
        personal_pronouns = len(re.findall(r'\b(I|my|me|myself)\b', text, re.IGNORECASE))
        total_words = len(text.split())
        
        if personal_pronouns < total_words * 0.02:
            return {
                "score": "Low",
                "feedback": "Consider adding more personal voice and perspective"
            }
        elif personal_pronouns > total_words * 0.08:
            return {
                "score": "High", 
                "feedback": "Good personal voice, but ensure you're not overusing 'I'"
            }
        else:
            return {
                "score": "Good",
                "feedback": "Nice balance of personal voice"
            }
    
    def _check_specific_examples(self, text):
        """Check for specific examples and details"""
        # Look for specific numbers, dates, names, places
        specifics = len(re.findall(r'\b(\d+|[A-Z][a-z]+\s+(School|University|College|Club|Team))\b', text))
        
        if specifics < 3:
            return {
                "score": "Low",
                "feedback": "Add more specific examples, names, numbers, or details"
            }
        else:
            return {
                "score": "Good", 
                "feedback": "Good use of specific examples and details"
            }
    
    def _check_essay_requirements(self, text, essay_type):
        """Check essay-type specific requirements"""
        requirements = {
            "personal_statement": [
                "Shows personal growth or insight",
                "Demonstrates self-reflection", 
                "Reveals character or values",
                "Connects to future goals"
            ],
            "why_us": [
                "Mentions specific programs or opportunities",
                "Shows research about the school",
                "Connects personal interests to school offerings",
                "Demonstrates genuine interest"
            ],
            "activity": [
                "Describes specific activities or experiences",
                "Shows impact or leadership",
                "Demonstrates passion or commitment",
                "Includes concrete examples"
            ]
        }
        
        return {
            "type": essay_type,
            "requirements": requirements.get(essay_type, requirements["personal_statement"]),
            "suggestion": f"Make sure your essay addresses the key elements of a {essay_type.replace('_', ' ')} essay"
        }
    
    def _analyze_style(self, text):
        """Analyze writing style"""
        # Check for transition words
        transitions = len(re.findall(r'\b(however|moreover|furthermore|therefore|consequently|meanwhile|additionally|finally)\b', text, re.IGNORECASE))
        
        # Check for varied sentence beginnings
        sentences = re.split(r'[.!?]+', text)
        first_words = [s.strip().split()[0].lower() if s.strip() and s.strip().split() else '' for s in sentences]
        unique_beginnings = len(set(first_words))
        
        return {
            "transition_words": transitions,
            "sentence_variety": f"{unique_beginnings}/{len(sentences)} unique sentence beginnings",
            "suggestions": self._style_suggestions(transitions, unique_beginnings, len(sentences))
        }
    
    def _style_suggestions(self, transitions, unique_beginnings, total_sentences):
        """Generate style improvement suggestions"""
        suggestions = []
        
        if transitions < total_sentences * 0.1:
            suggestions.append("Add more transition words to improve flow")
        
        if unique_beginnings < total_sentences * 0.7:
            suggestions.append("Vary your sentence beginnings for better style")
        
        suggestions.extend([
            "Read your essay aloud to check for flow",
            "Show, don't tell - use specific examples",
            "Avoid clichés and overused phrases",
            "End with a strong, memorable conclusion"
        ])
        
        return suggestions
    
    def _generate_suggestions(self, text, essay_type):
        """Generate overall improvement suggestions"""
        word_count = len(text.split())
        
        suggestions = []
        
        # Word count suggestions
        if essay_type == "personal_statement":
            if word_count < 400:
                suggestions.append("Consider expanding - most personal statements are 500-650 words")
            elif word_count > 700:
                suggestions.append("Consider trimming - stay within word limits (usually 650 words)")
        
        # General suggestions
        suggestions.extend([
            "Have someone else read your essay for feedback",
            "Check for grammar and spelling errors",
            "Make sure every sentence adds value",
            "Ensure your conclusion ties back to your introduction"
        ])
        
        return suggestions
    
    def get_essay_prompts_help(self, prompt_type):
        """Help students understand different essay prompts"""
        prompt_guides = {
            "personal_statement": {
                "purpose": "Show who you are beyond grades and test scores",
                "approach": "Choose a meaningful experience, challenge, or realization",
                "structure": "Hook → Context → Challenge/Experience → Growth → Future",
                "tips": [
                    "Be specific and personal",
                    "Show growth and self-reflection", 
                    "Connect to your future goals",
                    "Avoid common topics unless you have a unique angle"
                ]
            },
            "why_us": {
                "purpose": "Demonstrate genuine interest and fit with the school",
                "approach": "Research specific programs, opportunities, or values",
                "structure": "Personal interest → School research → Connection → Future plans",
                "tips": [
                    "Mention specific professors, programs, or opportunities",
                    "Connect your interests to what the school offers",
                    "Avoid generic statements that could apply to any school",
                    "Show you've done your research"
                ]
            },
            "challenge": {
                "purpose": "Show resilience, problem-solving, and growth",
                "approach": "Choose a genuine challenge you've overcome",
                "structure": "Challenge → Actions taken → Outcome → Learning → Growth",
                "tips": [
                    "Focus on what you did, not what was done to you",
                    "Show specific actions you took",
                    "Highlight personal growth and learning",
                    "Avoid trauma dumping or oversharing"
                ]
            }
        }
        
        return prompt_guides.get(prompt_type, prompt_guides["personal_statement"])
