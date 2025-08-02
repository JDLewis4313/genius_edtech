import re
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# ML imports with graceful fallbacks
try:
    import torch
    from transformers import (
        AutoTokenizer, AutoModelForSequenceClassification,
        pipeline, AutoModel
    )
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.pipeline import Pipeline
    import numpy as np
    from textblob import TextBlob  # FIX: Add TextBlob to imports
    DEPENDENCIES_AVAILABLE = True
    TEXTBLOB_AVAILABLE = True
except ImportError as e:
    DEPENDENCIES_AVAILABLE = False
    TEXTBLOB_AVAILABLE = False
    logging.warning(f"NL dependencies not available: {e}")
    
    # Try importing just TextBlob if other ML libs fail
    try:
        from textblob import TextBlob
        TEXTBLOB_AVAILABLE = True
    except ImportError:
        TEXTBLOB_AVAILABLE = False

logger = logging.getLogger(__name__)

class NLEnhancer:
    """Natural Language Enhancement Layer for Mentari"""
    
    def __init__(self):
        self._intent_model = None
        self._emotion_model = None
        self._entity_extractor = None
        self._initialized = False
        self._fallback_mode = not DEPENDENCIES_AVAILABLE
        
        # Educational intent mapping
        self.intent_patterns = {
            'greeting': [
                'hello', 'hi', 'hey', 'good morning', 'good afternoon', 
                'good evening', 'whats up', 'how are you'
            ],
            'math_help': [
                'solve', 'equation', 'algebra', 'calculus', 'derivative', 
                'integral', 'math', 'mathematics', 'calculate'
            ],
            'chemistry_help': [
                'molar mass', 'element', 'periodic table', 'molecule', 
                'compound', 'chemistry', 'atomic', 'chemical'
            ],
            'quiz_request': [
                'quiz', 'test', 'practice', 'question', 'assessment',
                'challenge', 'exam'
            ],
            'help_seeking': [
                'help', 'confused', 'struggling', 'dont understand',
                'difficult', 'hard', 'stuck', 'lost'
            ],
            'progress_inquiry': [
                'progress', 'how am i doing', 'stats', 'performance',
                'improvement', 'growth', 'analytics'
            ],
            'reflection': [
                'reflect', 'journal', 'feeling', 'thinking about',
                'mood', 'emotions', 'thoughts'
            ],
            'encouragement_needed': [
                'frustrated', 'tired', 'overwhelmed', 'stressed',
                'anxious', 'worried', 'discouraged'
            ]
        }
        
        # Emotion indicators
        self.emotion_patterns = {
            'frustrated': [
                'frustrated', 'annoyed', 'irritated', 'cant figure out',
                'this is stupid', 'hate this', 'giving up'
            ],
            'confused': [
                'confused', 'lost', 'dont understand', 'unclear',
                'what does this mean', 'makes no sense'
            ],
            'excited': [
                'excited', 'awesome', 'great', 'love this', 'amazing',
                'fantastic', 'cool', 'interesting'
            ],
            'confident': [
                'got it', 'understand', 'makes sense', 'easy',
                'i know', 'clear', 'obvious'
            ],
            'overwhelmed': [
                'overwhelmed', 'too much', 'cant handle', 'stressed',
                'pressure', 'too many', 'exhausted'
            ],
            'curious': [
                'curious', 'wonder', 'what if', 'why', 'how does',
                'interesting', 'want to know'
            ]
        }
        
        # Educational entities
        self.entity_patterns = {
            'math_topics': [
                'algebra', 'calculus', 'geometry', 'trigonometry',
                'statistics', 'probability', 'derivatives', 'integrals'
            ],
            'chemistry_topics': [
                'periodic table', 'elements', 'molecules', 'compounds',
                'reactions', 'balancing', 'molar mass', 'atoms'
            ],
            'difficulty_indicators': [
                'easy', 'hard', 'difficult', 'challenging', 'simple',
                'complex', 'basic', 'advanced'
            ],
            'time_references': [
                'today', 'tomorrow', 'yesterday', 'this week',
                'next week', 'deadline', 'due date'
            ]
        }
    
    def enhance_message(self, message: str, user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Main enhancement method - adds NL insights to message"""
        try:
            if self._fallback_mode:
                return self._fallback_enhancement(message)
            
            if not self._initialized:
                self._lazy_initialize()
            
            # Core NL processing
            enhancement = {
                'original_message': message,
                'timestamp': datetime.now().isoformat(),
                'nl_available': True,
                
                # A: Intent Classification
                'intent_analysis': self._classify_intent(message),
                
                # B: Entity Extraction  
                'entity_analysis': self._extract_entities(message),
                
                # C: Emotion Detection
                'emotion_analysis': self._detect_emotion(message),
                
                # Additional insights
                'enhanced_keywords': self._generate_enhanced_keywords(message),
                'conversation_context': self._analyze_conversation_context(message, user_context),
                'learning_indicators': self._detect_learning_indicators(message)
            }
            
            return enhancement
            
        except Exception as e:
            logger.error(f"NL Enhancement failed: {e}")
            return self._fallback_enhancement(message)
    
    def _lazy_initialize(self):
        """Initialize models only when first needed"""
        try:
            logger.info("Initializing NL models...")
            
            # Initialize intent classifier
            self._initialize_intent_model()
            
            # Initialize emotion detector
            self._initialize_emotion_model()
            
            # Initialize entity extractor
            self._initialize_entity_extractor()
            
            self._initialized = True
            logger.info("NL models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize NL models: {e}")
            self._fallback_mode = True
    
    def _initialize_intent_model(self):
        """Initialize intent classification model"""
        try:
            # Use lightweight scikit-learn approach for speed
            self._intent_model = self._create_intent_classifier()
        except Exception as e:
            logger.warning(f"Intent model initialization failed: {e}")
            self._intent_model = None
    
    def _create_intent_classifier(self):
        """Create and train a simple intent classifier"""
        # Training data based on educational patterns
        training_texts = []
        training_labels = []
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                # Add exact patterns
                training_texts.append(pattern)
                training_labels.append(intent)
                
                # Add variations
                training_texts.append(f"i need help with {pattern}")
                training_labels.append(intent)
                
                training_texts.append(f"can you help me {pattern}")
                training_labels.append(intent)
        
        # Create pipeline
        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=1000)),
            ('classifier', MultinomialNB())
        ])
        
        # Train
        pipeline.fit(training_texts, training_labels)
        
        return pipeline
    
    def _initialize_emotion_model(self):
        """Initialize emotion detection model"""
        try:
            # Use TextBlob for sentiment + pattern matching for specific emotions
            self._emotion_model = "textblob_with_patterns"
        except Exception as e:
            logger.warning(f"Emotion model initialization failed: {e}")
            self._emotion_model = None
    
    def _initialize_entity_extractor(self):
        """Initialize entity extraction"""
        try:
            # Use pattern matching + transformers for educational entities
            self._entity_extractor = "pattern_based"
        except Exception as e:
            logger.warning(f"Entity extractor initialization failed: {e}")
            self._entity_extractor = None
    
    def _classify_intent(self, message: str) -> Dict[str, Any]:
        """A: Intent Classification"""
        try:
            if self._intent_model:
                # Use trained model
                prediction = self._intent_model.predict([message])[0]
                probabilities = self._intent_model.predict_proba([message])[0]
                confidence = max(probabilities)
                
                # Get top intents
                intent_names = self._intent_model.classes_
                intent_scores = dict(zip(intent_names, probabilities))
                top_intents = sorted(intent_scores.items(), key=lambda x: x[1], reverse=True)[:3]
                
                return {
                    'primary_intent': prediction,
                    'confidence': float(confidence),
                    'top_intents': [{'intent': intent, 'score': float(score)} for intent, score in top_intents],
                    'method': 'ml_classifier'
                }
            else:
                # Fallback to pattern matching
                return self._pattern_based_intent(message)
                
        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            return self._pattern_based_intent(message)
    
    def _pattern_based_intent(self, message: str) -> Dict[str, Any]:
        """Fallback intent classification using patterns"""
        message_lower = message.lower()
        intent_scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                if pattern in message_lower:
                    score += 1
            
            if score > 0:
                intent_scores[intent] = score / len(patterns)
        
        if intent_scores:
            primary_intent = max(intent_scores, key=intent_scores.get)
            confidence = intent_scores[primary_intent]
            
            return {
                'primary_intent': primary_intent,
                'confidence': confidence,
                'top_intents': [{'intent': k, 'score': v} for k, v in sorted(intent_scores.items(), key=lambda x: x[1], reverse=True)],
                'method': 'pattern_matching'
            }
        
        return {
            'primary_intent': 'general_inquiry',
            'confidence': 0.3,
            'top_intents': [{'intent': 'general_inquiry', 'score': 0.3}],
            'method': 'default'
        }
    
    def _extract_entities(self, message: str) -> Dict[str, Any]:
        """B: Entity Extraction"""
        try:
            entities = {}
            message_lower = message.lower()
            
            # Extract educational entities
            for entity_type, patterns in self.entity_patterns.items():
                found_entities = []
                for pattern in patterns:
                    if pattern in message_lower:
                        found_entities.append(pattern)
                
                if found_entities:
                    entities[entity_type] = found_entities
            
            # Extract chemical formulas
            chemical_formulas = re.findall(r'\b([A-Z][a-z]?\d*)+\b', message)
            if chemical_formulas:
                entities['chemical_formulas'] = chemical_formulas
            
            # Extract numbers (for math problems)
            numbers = re.findall(r'\b\d+\.?\d*\b', message)
            if numbers:
                entities['numbers'] = numbers
            
            # Extract mathematical expressions
            math_expressions = re.findall(r'[x\+\-\*\/\=\^\(\)]+', message)
            if math_expressions:
                entities['math_expressions'] = math_expressions
            
            return {
                'entities': entities,
                'entity_count': sum(len(v) for v in entities.values()),
                'method': 'pattern_extraction'
            }
            
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return {'entities': {}, 'entity_count': 0, 'method': 'failed'}
    
    def _detect_emotion(self, message: str) -> Dict[str, Any]:
        """C: Emotion Detection"""
        try:
            # Pattern-based emotion detection
            message_lower = message.lower()
            emotion_scores = {}
            
            for emotion, patterns in self.emotion_patterns.items():
                score = 0
                for pattern in patterns:
                    if pattern in message_lower:
                        score += 1
                
                if score > 0:
                    emotion_scores[emotion] = score / len(patterns)
            
            # Add sentiment analysis if TextBlob available
            sentiment_data = None
            if TEXTBLOB_AVAILABLE:  # FIX: Check availability
                try:
                    blob = TextBlob(message)
                    sentiment_polarity = blob.sentiment.polarity
                    sentiment_subjectivity = blob.sentiment.subjectivity
                    
                    # Convert sentiment to emotion categories
                    if sentiment_polarity > 0.3:
                        emotion_scores['positive'] = sentiment_polarity
                    elif sentiment_polarity < -0.3:
                        emotion_scores['negative'] = abs(sentiment_polarity)
                    
                    sentiment_data = {
                        'polarity': sentiment_polarity,
                        'subjectivity': sentiment_subjectivity
                    }
                except Exception as e:
                    logger.warning(f"TextBlob sentiment analysis failed: {e}")
            
            # Determine primary emotion
            if emotion_scores:
                primary_emotion = max(emotion_scores, key=emotion_scores.get)
                confidence = emotion_scores[primary_emotion]
            else:
                primary_emotion = 'neutral'
                confidence = 0.5
            
            return {
                'primary_emotion': primary_emotion,
                'confidence': confidence,
                'emotion_scores': emotion_scores,
                'sentiment': sentiment_data,
                'method': 'pattern_and_sentiment' if sentiment_data else 'pattern_only'
            }
            
        except Exception as e:
            logger.error(f"Emotion detection failed: {e}")
            return {
                'primary_emotion': 'neutral',
                'confidence': 0.5,
                'emotion_scores': {},
                'sentiment': None,
                'method': 'failed'
            }
    
    def _generate_enhanced_keywords(self, message: str) -> List[str]:
        """Generate enhanced keywords for better matching"""
        try:
            keywords = set()
            
            # Original keywords
            words = re.findall(r'\b\w+\b', message.lower())
            keywords.update(words)
            
            # Add educational synonyms
            synonym_map = {
                'math': ['mathematics', 'calculation', 'problem'],
                'chemistry': ['chem', 'chemical', 'science'],
                'help': ['assist', 'support', 'guide'],
                'confused': ['lost', 'unclear', 'stuck'],
                'quiz': ['test', 'assessment', 'practice']
            }
            
            for word in words:
                if word in synonym_map:
                    keywords.update(synonym_map[word])
            
            return list(keywords)
            
        except Exception as e:
            logger.error(f"Keyword generation failed: {e}")
            return message.lower().split()
    
    def _analyze_conversation_context(self, message: str, user_context: Optional[Dict]) -> Dict[str, Any]:
        """Analyze conversation context and flow"""
        context = {
            'message_length': len(message.split()),
            'question_indicators': len(re.findall(r'\?', message)),
            'urgency_indicators': len(re.findall(r'urgent|asap|quickly|now|help!', message.lower())),
            'politeness_indicators': len(re.findall(r'please|thank|thanks|sorry', message.lower()))
        }
        
        if user_context:
            context['has_user_context'] = True
            context['user_context_keys'] = list(user_context.keys())
        else:
            context['has_user_context'] = False
        
        return context
    
    def _detect_learning_indicators(self, message: str) -> Dict[str, Any]:
        """Detect learning-specific indicators"""
        message_lower = message.lower()
        
        indicators = {
            'struggle_level': self._assess_struggle_level(message_lower),
            'learning_stage': self._identify_learning_stage(message_lower),
            'help_type_needed': self._identify_help_type(message_lower),
            'academic_pressure': self._detect_academic_pressure(message_lower)
        }
        
        return indicators
    
    def _assess_struggle_level(self, message: str) -> str:
        """Assess how much the student is struggling"""
        high_struggle = ['cant', 'impossible', 'giving up', 'hate', 'failing']
        medium_struggle = ['difficult', 'hard', 'confused', 'struggling']
        low_struggle = ['little help', 'clarification', 'check my work']
        
        if any(indicator in message for indicator in high_struggle):
            return 'high'
        elif any(indicator in message for indicator in medium_struggle):
            return 'medium'
        elif any(indicator in message for indicator in low_struggle):
            return 'low'
        else:
            return 'none'
    
    def _identify_learning_stage(self, message: str) -> str:
        """Identify what stage of learning the student is in"""
        if any(word in message for word in ['new to', 'never', 'first time', 'beginning']):
            return 'introduction'
        elif any(word in message for word in ['practice', 'more examples', 'similar problems']):
            return 'practice'
        elif any(word in message for word in ['test', 'exam', 'quiz', 'review']):
            return 'assessment'
        elif any(word in message for word in ['advanced', 'next level', 'harder']):
            return 'advancement'
        else:
            return 'exploration'
    
    def _identify_help_type(self, message: str) -> str:
        """Identify what type of help is needed"""
        if any(word in message for word in ['explain', 'understand', 'what is', 'how does']):
            return 'conceptual'
        elif any(word in message for word in ['solve', 'calculate', 'find', 'answer']):
            return 'procedural'
        elif any(word in message for word in ['example', 'show me', 'demonstrate']):
            return 'example_based'
        elif any(word in message for word in ['check', 'correct', 'right', 'wrong']):
            return 'verification'
        else:
            return 'general'
    
    def _detect_academic_pressure(self, message: str) -> str:
        """Detect academic pressure indicators"""
        high_pressure = ['deadline', 'due tomorrow', 'test tomorrow', 'grade']
        medium_pressure = ['homework', 'assignment', 'study for']
        
        if any(indicator in message for indicator in high_pressure):
            return 'high'
        elif any(indicator in message for indicator in medium_pressure):
            return 'medium'
        else:
            return 'low'
    
    def _fallback_enhancement(self, message: str) -> Dict[str, Any]:
        """Fallback when NL models aren't available"""
        return {
            'original_message': message,
            'nl_available': False,
            'fallback_mode': True,
            'intent_analysis': self._pattern_based_intent(message),
            'entity_analysis': self._extract_entities(message),
            'emotion_analysis': {'primary_emotion': 'neutral', 'confidence': 0.5},
            'enhanced_keywords': message.lower().split(),
            'conversation_context': {'message_length': len(message.split())},
            'learning_indicators': {'struggle_level': 'unknown'}
        }

# Global instance for lazy loading
_nl_enhancer_instance = None

def get_nl_enhancer():
    """Get global NL enhancer instance (lazy loaded)"""
    global _nl_enhancer_instance
    if _nl_enhancer_instance is None:
        _nl_enhancer_instance = NLEnhancer()
    return _nl_enhancer_instance