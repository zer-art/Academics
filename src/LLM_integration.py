import os
import json
import time
from datetime import datetime
from typing import List, Dict
import requests
from dotenv import load_dotenv

load_dotenv()

class InterviewConductor:
    """
    A class to conduct AI-powered interviews for specific job titles.
    """
    
    def __init__(self):
        self.gemini_api_key = os.getenv('GEMINI')
        self.gemini_api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
        self.interview_data = {
            'job_title': '',
            'candidate_name': '',
            'questions': [],
            'responses': [],
            'scores': [],
            'feedback': [],
            'start_time': '',
            'end_time': '',
            'overall_score': 0
        }
    
    def generate_job_specific_questions(self, job_title: str, experience_level: str = "mid-level", num_questions: int = 15) -> List[str]:
        """
        Generate interview questions specific to a job title and experience level.
        """
        if not self.gemini_api_key:
            raise ValueError("Gemini API key not found in environment variables.")
        
        prompt = f"""
        Generate exactly {num_questions} professional interview questions for a {experience_level} {job_title} position.
        
        Please include:
        - 3-4 technical questions specific to the role
        - 2-3 behavioral questions
        - 2-3 situational questions
        - 2-3 problem-solving questions
        - 1-2 questions about experience and background
        - 1-2 questions about career goals and motivation
        
        Format each question as a numbered list (1., 2., etc.).
        Make questions challenging but fair for a {experience_level} candidate.
        """
        
        headers = {"Content-Type": "application/json"}
        params = {"key": self.gemini_api_key}
        data = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        
        try:
            response = requests.post(self.gemini_api_url, headers=headers, params=params, json=data)
            response.raise_for_status()
            result = response.json()
            
            text = result['candidates'][0]['content']['parts'][0]['text']
            # Extract questions from numbered list
            questions = []
            for line in text.split('\n'):
                line = line.strip()
                if line and any(line.startswith(f"{i}.") for i in range(1, num_questions + 1)):
                    # Remove the number and clean up
                    question = line.split('.', 1)[1].strip()
                    if question:
                        questions.append(question)
            
            return questions[:num_questions]  # Ensure we don't exceed the requested number
            
        except Exception as e:
            print(f"Error generating questions: {e}")
            return self._get_fallback_questions(job_title)
    
    def evaluate_response(self, question: str, response: str, job_title: str) -> Dict:
        """
        Evaluate a candidate's response to an interview question.
        """
        if not response.strip():
            return {
                'score': 0,
                'feedback': 'No response provided.',
                'strengths': [],
                'areas_for_improvement': ['Provide a complete response to the question.']
            }
        
        prompt = f"""
        You are an experienced interviewer evaluating a candidate for a {job_title} position.
        
        Question: {question}
        Candidate's Response: {response}
        
        Please evaluate this response and provide:
        1. A score from 0-10 (10 being excellent)
        2. Brief feedback (2-3 sentences)
        3. Key strengths demonstrated (if any)
        4. Areas for improvement (if any)
        
        Format your response as JSON:
        {{
            "score": <number>,
            "feedback": "<feedback>",
            "strengths": ["<strength1>", "<strength2>"],
            "areas_for_improvement": ["<area1>", "<area2>"]
        }}
        """
        
        headers = {"Content-Type": "application/json"}
        params = {"key": self.gemini_api_key}
        data = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        
        try:
            response_api = requests.post(self.gemini_api_url, headers=headers, params=params, json=data)
            response_api.raise_for_status()
            result = response_api.json()
            
            text = result['candidates'][0]['content']['parts'][0]['text']
            # Try to extract JSON from the response
            try:
                # Find JSON in the response
                start = text.find('{')
                end = text.rfind('}') + 1
                if start != -1 and end != 0:
                    json_str = text[start:end]
                    evaluation = json.loads(json_str)
                    return evaluation
            except json.JSONDecodeError:
                pass
            
            # Fallback if JSON parsing fails
            return {
                'score': 5,
                'feedback': 'Response evaluated. Could not parse detailed feedback.',
                'strengths': [],
                'areas_for_improvement': []
            }
            
        except Exception as e:
            print(f"Error evaluating response: {e}")
            return {
                'score': 5,
                'feedback': 'Unable to evaluate response due to technical issues.',
                'strengths': [],
                'areas_for_improvement': []
            }
    
    def start_interview(self, job_title: str, candidate_name: str, experience_level: str = "mid-level"):
        """
        Start a new interview session.
        """
        self.interview_data = {
            'job_title': job_title,
            'candidate_name': candidate_name,
            'experience_level': experience_level,
            'questions': [],
            'responses': [],
            'scores': [],
            'feedback': [],
            'start_time': datetime.now().isoformat(),
            'end_time': '',
            'overall_score': 0
        }
        
        print(f"Welcome to the AI Interview System!")
        print(f"Candidate: {candidate_name}")
        print(f"Position: {job_title} ({experience_level})")
        print(f"Generating interview questions...")
        
        questions = self.generate_job_specific_questions(job_title, experience_level)
        self.interview_data['questions'] = questions
        
        print(f"Generated {len(questions)} questions for the interview.")
        return questions
    
    def conduct_interview(self, questions: List[str] = None):
        """
        Conduct the interview by asking questions and collecting responses.
        """
        if questions is None:
            questions = self.interview_data['questions']
        
        if not questions:
            raise ValueError("No questions available. Please start an interview first.")
        
        print("\n" + "="*50)
        print("INTERVIEW STARTED")
        print("="*50)
        
        for i, question in enumerate(questions, 1):
            print(f"\nQuestion {i}/{len(questions)}:")
            print(f"{question}")
            print("\nPlease provide your response:")
            
            response = input("> ")
            
            # Evaluate the response
            evaluation = self.evaluate_response(question, response, self.interview_data['job_title'])
            
            # Store the data
            self.interview_data['responses'].append(response)
            self.interview_data['scores'].append(evaluation['score'])
            self.interview_data['feedback'].append(evaluation)
            
            print(f"Response recorded. Moving to next question...")
            time.sleep(1)  # Brief pause between questions
        
        # Calculate overall score
        if self.interview_data['scores']:
            self.interview_data['overall_score'] = sum(self.interview_data['scores']) / len(self.interview_data['scores'])
        
        self.interview_data['end_time'] = datetime.now().isoformat()
        
        print("\n" + "="*50)
        print("INTERVIEW COMPLETED")
        print("="*50)
        
        return self.interview_data
    
    def generate_final_report(self) -> str:
        """
        Generate a comprehensive interview report.
        """
        if not self.interview_data['questions']:
            return "No interview data available."
        
        report = f"""
INTERVIEW REPORT
================

Candidate: {self.interview_data['candidate_name']}
Position: {self.interview_data['job_title']} ({self.interview_data.get('experience_level', 'N/A')})
Date: {self.interview_data['start_time'][:10]}
Duration: {self._calculate_duration()}

OVERALL PERFORMANCE
==================
Overall Score: {self.interview_data['overall_score']:.1f}/10
Performance Level: {self._get_performance_level(self.interview_data['overall_score'])}

QUESTION-BY-QUESTION ANALYSIS
============================
"""
        
        for i, (question, response, score, feedback) in enumerate(zip(
            self.interview_data['questions'],
            self.interview_data['responses'],
            self.interview_data['scores'],
            self.interview_data['feedback']
        ), 1):
            report += f"""
Question {i}: {question}
Response: {response[:100]}{'...' if len(response) > 100 else ''}
Score: {score}/10
Feedback: {feedback.get('feedback', 'No feedback available')}
Strengths: {', '.join(feedback.get('strengths', [])) or 'None identified'}
Areas for Improvement: {', '.join(feedback.get('areas_for_improvement', [])) or 'None identified'}

{'-'*50}
"""
        
        # Overall recommendations
        report += self._generate_recommendations()
        
        return report
    
    def save_interview_data(self, filename: str = None):
        """
        Save interview data to a JSON file.
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"interview_{self.interview_data['candidate_name']}_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.interview_data, f, indent=2)
        
        return filename
    
    def _get_fallback_questions(self, job_title: str) -> List[str]:
        """
        Provide fallback questions if API fails.
        """
        general_questions = [
            "Tell me about yourself and your experience.",
            "Why are you interested in this position?",
            "What are your greatest strengths?",
            "Describe a challenging project you worked on.",
            "How do you handle tight deadlines?",
            "Where do you see yourself in 5 years?",
            "Why are you leaving your current position?",
            "Describe a time when you had to learn something new quickly.",
            "How do you handle criticism?",
            "What motivates you in your work?",
            "Describe a time when you worked in a team.",
            "How do you prioritize your tasks?",
            "What is your biggest weakness?",
            "Tell me about a time you failed and what you learned.",
            "Do you have any questions for us?"
        ]
        return general_questions
    
    def _calculate_duration(self) -> str:
        """
        Calculate interview duration.
        """
        try:
            start = datetime.fromisoformat(self.interview_data['start_time'])
            end = datetime.fromisoformat(self.interview_data['end_time'])
            duration = end - start
            minutes = int(duration.total_seconds() / 60)
            return f"{minutes} minutes"
        except:
            return "Duration not available"
    
    def _get_performance_level(self, score: float) -> str:
        """
        Convert numeric score to performance level.
        """
        if score >= 8.5:
            return "Excellent"
        elif score >= 7.0:
            return "Good"
        elif score >= 5.5:
            return "Average"
        elif score >= 3.0:
            return "Below Average"
        else:
            return "Poor"
    
    def _generate_recommendations(self) -> str:
        """
        Generate hiring recommendations based on performance.
        """
        score = self.interview_data['overall_score']
        
        if score >= 8.0:
            recommendation = "STRONGLY RECOMMEND for hire. Candidate demonstrated excellent skills and knowledge."
        elif score >= 6.5:
            recommendation = "RECOMMEND for hire. Candidate shows good potential with some areas for development."
        elif score >= 5.0:
            recommendation = "CONSIDER for hire. Candidate has basic qualifications but may need additional training."
        else:
            recommendation = "DO NOT RECOMMEND for hire. Candidate does not meet the minimum requirements."
        
        return f"""
HIRING RECOMMENDATION
====================
{recommendation}

Note: This assessment is based on AI evaluation and should be used as a supplementary tool alongside human judgment.
"""
