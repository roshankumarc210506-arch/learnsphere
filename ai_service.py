"""
AI Service for LearnSphere
Handles AI-powered question generation and content analysis
"""

import google.generativeai as genai
import os
import json
from typing import List, Dict, Optional

class AIService:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the AI service with Gemini API"""
        self.api_key = api_key or os.environ.get('GEMINI_API_KEY')
        self.model = None
        self.initialization_error = None
        self.last_error_time = None
        self.error_count = 0
        self.max_retries = 3
        self.retry_delay = 300  # 5 minutes
        
        if self.api_key:
            self._initialize_model()
        else:
            self.initialization_error = "GEMINI_API_KEY not set. AI features disabled."
            print("⚠", self.initialization_error)
            
    def _initialize_model(self):
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            print("✓ AI Service initialized successfully")
            # Reset error tracking on successful initialization
            self.initialization_error = None
            self.error_count = 0
            self.last_error_time = None
        except Exception as e:
            self.error_count += 1
            self.last_error_time = datetime.utcnow()
            self.initialization_error = f"AI Service initialization failed: {str(e)}"
            print("✗", self.initialization_error)
            
    def _should_retry(self):
        if self.error_count >= self.max_retries:
            if self.last_error_time and (datetime.utcnow() - self.last_error_time).total_seconds() > self.retry_delay:
                self.error_count = 0  # Reset after delay
                return True
            return False
        return True
    
    def is_available(self) -> bool:
        """Check if AI service is available"""
        return self.model is not None
    
    def generate_quiz_questions(self, topic: str, difficulty: str = 'medium', count: int = 5) -> List[Dict]:
        """Generate quiz questions for a specific topic using AI"""
        if not self.is_available():
            return []
        
        prompt = f"""Generate {count} multiple choice questions about {topic} at {difficulty} difficulty level.

For each question, provide:
1. The question text
2. Exactly 3 answer options
3. The correct answer (must match one of the options exactly)
4. A helpful hint
5. A brief explanation of the correct answer

Format the response as a valid JSON array with this structure:
[
  {{
    "question": "Question text here?",
    "options": ["Option A", "Option B", "Option C"],
    "correct_answer": "Option A",
    "hint": "Helpful hint here",
    "explanation": "Brief explanation of why this is correct"
  }}
]

Make questions educational, clear, and appropriate for {difficulty} level students.
IMPORTANT: Return ONLY the JSON array, no markdown formatting."""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Extract JSON from markdown code blocks if present
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()
            
            questions = json.loads(text)
            
            # Validate and format questions
            formatted_questions = []
            for q in questions:
                if all(key in q for key in ['question', 'options', 'correct_answer']):
                    formatted_questions.append({
                        'topic': topic,
                        'question': q['question'],
                        'options': q['options'],
                        'correct_answer': q['correct_answer'],
                        'difficulty': difficulty,
                        'hint': q.get('hint', ''),
                        'explanation': q.get('explanation', '')
                    })
            
            return formatted_questions
        
        except Exception as e:
            print(f"Error generating questions: {str(e)}")
            return []
    
    def analyze_student_performance(self, quiz_scores: Dict, weak_topics: List[str]) -> Dict:
        """Analyze student performance and provide personalized recommendations"""
        if not self.is_available():
            return {
                'overall_performance': 'N/A - AI service unavailable',
                'recommendations': ['Continue practicing weak topics', 'Review quiz results'],
                'focus_areas': weak_topics,
                'study_strategies': ['Regular practice', 'Seek help when needed']
            }
        
        prompt = f"""Analyze this student's performance and provide personalized recommendations:

Quiz Scores: {json.dumps(quiz_scores)}
Weak Topics: {', '.join(weak_topics) if weak_topics else 'None identified'}

Provide:
1. Overall performance assessment (2-3 sentences)
2. Top 3 specific recommendations for improvement
3. Priority focus areas (ranked)
4. Suggested study strategies

Format as JSON:
{{
  "overall_performance": "Assessment text",
  "recommendations": ["rec1", "rec2", "rec3"],
  "focus_areas": ["topic1", "topic2"],
  "study_strategies": ["strategy1", "strategy2"]
}}

IMPORTANT: Return ONLY the JSON object, no markdown formatting."""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()
            
            analysis = json.loads(text)
            return analysis
        
        except Exception as e:
            print(f"Error analyzing performance: {str(e)}")
            return {
                'overall_performance': 'Analysis unavailable',
                'recommendations': ['Continue practicing', 'Review weak topics', 'Take regular quizzes'],
                'focus_areas': weak_topics,
                'study_strategies': ['Daily practice', 'Study in focused sessions']
            }
    
    def chat_with_tutor(self, message: str, context: Dict, history: List = None) -> str:
        """Have a conversation with the AI tutor"""
        if not self.is_available():
            return "AI tutor is currently unavailable. Please check your API configuration."
        
        system_instruction = f"""You are LearnSphere AI, an expert and encouraging educational tutor.

Student Context:
- Name: {context.get('name', 'Student')}
- Weak Topics: {', '.join(context.get('weak_topics', [])) or 'None'}
- Recent Quiz Scores: {json.dumps(context.get('quiz_scores', {})) or 'No scores yet'}

Guidelines:
1. Be supportive, patient, and encouraging
2. Explain concepts clearly with examples
3. Use simple language appropriate for students
4. Provide step-by-step explanations when needed
5. Ask clarifying questions if needed
6. Keep responses concise (2-4 paragraphs max)
7. Use markdown formatting for better readability (bold, lists, etc.)
8. Focus on helping the student understand, not just giving answers

Current conversation context: The student has asked about their learning topics or needs help with a concept."""

        try:
            # Create or continue chat
            if history:
                # Convert history format if needed
                formatted_history = []
                for msg in history:
                    if isinstance(msg, dict):
                        formatted_history.append(
                            genai.types.Content(
                                role=msg['role'],
                                parts=[genai.types.Part.from_text(p['text']) for p in msg.get('parts', [])]
                            )
                        )
                chat = self.model.start_chat(history=formatted_history)
            else:
                chat = self.model.start_chat()
            
            # Send message
            response = chat.send_message(f"{system_instruction}\n\nStudent: {message}")
            return response.text
        
        except Exception as e:
            print(f"Error in chat: {str(e)}")
            return "I'm having trouble processing your request. Please try rephrasing your question or check back later."
    
    def generate_study_plan(self, weak_topics: List[str], available_hours: int = 10) -> Dict:
        """Generate a personalized study plan"""
        if not self.is_available():
            return {'error': 'AI service unavailable'}
        
        prompt = f"""Create a personalized weekly study plan for a student.

Weak Topics: {', '.join(weak_topics)}
Available Study Time: {available_hours} hours per week

Provide a structured plan with:
1. Daily study schedule (which topics on which days)
2. Time allocation per topic
3. Specific learning activities
4. Milestones and checkpoints

Format as JSON:
{{
  "weekly_schedule": [
    {{"day": "Monday", "topic": "Algebra", "duration": 2, "activities": ["Review formulas", "Practice problems"]}},
    ...
  ],
  "milestones": ["Complete 10 practice problems", "Score 80% on quiz"],
  "tips": ["Study at the same time each day", "Take breaks every 25 minutes"]
}}

IMPORTANT: Return ONLY the JSON object, no markdown formatting."""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()
            
            plan = json.loads(text)
            return plan
        
        except Exception as e:
            print(f"Error generating study plan: {str(e)}")
            return {
                'error': str(e),
                'weekly_schedule': [
                    {
                        'day': 'Daily',
                        'topic': ', '.join(weak_topics),
                        'duration': available_hours // 7,
                        'activities': ['Review concepts', 'Practice problems']
                    }
                ],
                'milestones': ['Complete daily practice'],
                'tips': ['Stay consistent', 'Ask for help when needed']
            }
    
    def explain_concept(self, topic: str, concept: str, difficulty: str = 'beginner') -> str:
        """Get a detailed explanation of a concept"""
        if not self.is_available():
            return "AI explanation service is unavailable. Please check your API configuration."
        
        prompt = f"""Explain the concept of "{concept}" in {topic} at {difficulty} level.

Requirements:
1. Start with a simple definition
2. Provide a real-world analogy or example
3. Explain the key principles
4. Give 2-3 practice examples if applicable
5. Use clear, simple language
6. Use markdown formatting (bold, lists, etc.)

Keep the explanation concise but comprehensive (3-5 paragraphs)."""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        
        except Exception as e:
            print(f"Error explaining concept: {str(e)}")
            return f"Unable to generate explanation for {concept}. Please try again or consult your textbook."


# Singleton instance
_ai_service_instance = None

def get_ai_service() -> AIService:
    """Get the global AI service instance"""
    global _ai_service_instance
    if _ai_service_instance is None:
        _ai_service_instance = AIService()
    return _ai_service_instance
    
    def generate_quiz_questions(self, topic: str, difficulty: str = 'medium', count: int = 5) -> List[Dict]:
        """
        Generate quiz questions for a specific topic using AI
        
        Args:
            topic: The subject topic (e.g., 'Algebra', 'Calculus')
            difficulty: Question difficulty ('easy', 'medium', 'hard')
            count: Number of questions to generate
            
        Returns:
            List of question dictionaries
        """
        if not self.is_available():
            return []
        
        prompt = f"""Generate {count} multiple choice questions about {topic} at {difficulty} difficulty level.

For each question, provide:
1. The question text
2. Exactly 3 answer options
3. The correct answer (must match one of the options exactly)
4. A helpful hint
5. A brief explanation of the correct answer

Format the response as a valid JSON array with this structure:
[
  {{
    "question": "Question text here?",
    "options": ["Option A", "Option B", "Option C"],
    "correct_answer": "Option A",
    "hint": "Helpful hint here",
    "explanation": "Brief explanation of why this is correct"
  }}
]

Make questions educational, clear, and appropriate for {difficulty} level students."""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Extract JSON from markdown code blocks if present
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()
            
            questions = json.loads(text)
            
            # Validate and format questions
            formatted_questions = []
            for q in questions:
                if all(key in q for key in ['question', 'options', 'correct_answer']):
                    formatted_questions.append({
                        'topic': topic,
                        'question': q['question'],
                        'options': q['options'],
                        'correct_answer': q['correct_answer'],
                        'difficulty': difficulty,
                        'hint': q.get('hint', ''),
                        'explanation': q.get('explanation', '')
                    })
            
            return formatted_questions
        
        except Exception as e:
            print(f"Error generating questions: {str(e)}")
            return []
    
    def analyze_student_performance(self, quiz_scores: Dict, weak_topics: List[str]) -> Dict:
        """
        Analyze student performance and provide personalized recommendations
        
        Args:
            quiz_scores: Dictionary of topic -> score (0-1)
            weak_topics: List of topics student struggles with
            
        Returns:
            Dictionary with analysis and recommendations
        """
        if not self.is_available():
            return {
                'overall_performance': 'N/A',
                'recommendations': ['AI analysis unavailable'],
                'focus_areas': weak_topics
            }
        
        prompt = f"""Analyze this student's performance and provide personalized recommendations:

Quiz Scores: {json.dumps(quiz_scores)}
Weak Topics: {', '.join(weak_topics)}

Provide:
1. Overall performance assessment (2-3 sentences)
2. Top 3 specific recommendations for improvement
3. Priority focus areas (ranked)
4. Suggested study strategies

Format as JSON:
{{
  "overall_performance": "Assessment text",
  "recommendations": ["rec1", "rec2", "rec3"],
  "focus_areas": ["topic1", "topic2"],
  "study_strategies": ["strategy1", "strategy2"]
}}"""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()
            
            analysis = json.loads(text)
            return analysis
        
        except Exception as e:
            print(f"Error analyzing performance: {str(e)}")
            return {
                'overall_performance': 'Analysis unavailable',
                'recommendations': ['Continue practicing weak topics'],
                'focus_areas': weak_topics,
                'study_strategies': ['Regular review', 'Practice problems']
            }
    
    def chat_with_tutor(self, message: str, context: Dict, history: List = None) -> str:
        """
        Have a conversation with the AI tutor
        
        Args:
            message: User's message
            context: Student context (weak_topics, quiz_scores, etc.)
            history: Previous conversation history
            
        Returns:
            AI tutor's response
        """
        if not self.is_available():
            return "AI tutor is currently unavailable. Please try again later."
        
        system_prompt = f"""You are LearnSphere AI, an expert and encouraging educational tutor.

Student Context:
- Name: {context.get('name', 'Student')}
- Weak Topics: {', '.join(context.get('weak_topics', []))}
- Quiz Scores: {json.dumps(context.get('quiz_scores', {}))}

Guidelines:
1. Be supportive, patient, and encouraging
2. Explain concepts clearly with examples
3. Use simple language appropriate for students
4. Provide step-by-step explanations when needed
5. Ask clarifying questions if needed
6. Keep responses concise (2-4 paragraphs max)
7. Use markdown formatting for better readability"""

        try:
            # Create or continue chat
            if history:
                chat = self.model.start_chat(history=history)
            else:
                chat = self.model.start_chat()
            
            # Send message with context
            full_message = f"{system_prompt}\n\nStudent: {message}"
            response = chat.send_message(full_message)
            
            return response.text
        
        except Exception as e:
            print(f"Error in chat: {str(e)}")
            return "I'm having trouble processing your request. Please try rephrasing your question."
    
    def generate_study_plan(self, weak_topics: List[str], available_hours: int = 10) -> Dict:
        """
        Generate a personalized study plan
        
        Args:
            weak_topics: Topics student needs to improve
            available_hours: Hours available for study per week
            
        Returns:
            Structured study plan
        """
        if not self.is_available():
            return {'error': 'AI service unavailable'}
        
        prompt = f"""Create a personalized weekly study plan for a student.

Weak Topics: {', '.join(weak_topics)}
Available Study Time: {available_hours} hours per week

Provide a structured plan with:
1. Daily study schedule (which topics on which days)
2. Time allocation per topic
3. Specific learning activities
4. Milestones and checkpoints

Format as JSON:
{{
  "weekly_schedule": [
    {{"day": "Monday", "topic": "Algebra", "duration": 2, "activities": ["activity1", "activity2"]}},
    ...
  ],
  "milestones": ["milestone1", "milestone2"],
  "tips": ["tip1", "tip2"]
}}"""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()
            
            plan = json.loads(text)
            return plan
        
        except Exception as e:
            print(f"Error generating study plan: {str(e)}")
            return {'error': str(e)}
    
    def explain_concept(self, topic: str, concept: str, difficulty: str = 'beginner') -> str:
        """
        Get a detailed explanation of a concept
        
        Args:
            topic: Subject area (e.g., 'Calculus')
            concept: Specific concept to explain (e.g., 'derivatives')
            difficulty: Explanation level ('beginner', 'intermediate', 'advanced')
            
        Returns:
            Detailed explanation text
        """
        if not self.is_available():
            return "AI explanation service is unavailable."
        
        prompt = f"""Explain the concept of "{concept}" in {topic} at {difficulty} level.

Requirements:
1. Start with a simple definition
2. Provide a real-world analogy or example
3. Explain the key principles
4. Give 2-3 practice examples if applicable
5. Use clear, simple language
6. Use markdown formatting

Keep the explanation concise but comprehensive (3-5 paragraphs)."""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        
        except Exception as e:
            print(f"Error explaining concept: {str(e)}")
            return f"Unable to generate explanation for {concept}. Please try again."


# Singleton instance
_ai_service = None

def get_ai_service() -> AIService:
    """Get the global AI service instance"""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service