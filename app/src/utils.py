import json
import asyncio
import queue
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import numpy as np
import cv2
import sounddevice as sd
import soundfile as sf
from vosk import Model, KaldiRecognizer
from gtts import gTTS
import pygame
import tempfile
import os
import wave

from app.src.deepface import deepface_analyzer
from app.src.llm import llm
from langchain.prompts import PromptTemplate

class InterviewSession:
    def __init__(self, user_role: str):
        self.user_role = user_role
        self.questions = []
        self.answers = []
        self.emotion_data = []
        self.current_question_index = 0
        self.session_start_time = datetime.now()
        self.is_active = False
        
        # Audio parameters
        self.sample_rate = 16000
        self.channels = 1
        self.dtype = 'int16'
        
        # Initialize components
        self.stt_model = Model("app/models/vosk-model-small-en-us-0.15")
        self.stt_recognizer = KaldiRecognizer(self.stt_model, self.sample_rate)
        self.audio_queue = queue.Queue()
        
        # Initialize pygame for audio playback
        pygame.mixer.init()
        
    def initialize_questions(self) -> List[str]:
        """Generate initial set of core questions"""
        prompt = f"""
        Generate 5 core interview questions for {self.user_role} position.
        Focus on fundamental skills, experience, and behavioral aspects.
        Return ONLY a JSON array of questions like this:
        ["Question 1?", "Question 2?", "Question 3?", "Question 4?", "Question 5?"]
        """
        
        response = llm.invoke(prompt)
        try:
            # Clean the response and parse JSON
            content = response.content.strip()
            if content.startswith('```json'):
                content = content[7:-3]
            elif content.startswith('```'):
                content = content[3:-3]
            
            self.questions = json.loads(content)
            return self.questions
        except:
            # Fallback questions
            self.questions = [
                f"Tell me about yourself and your experience in {self.user_role}.",
                f"What are your key strengths for this {self.user_role} position?",
                f"Describe a challenging project you worked on in {self.user_role}.",
                f"How do you stay updated with the latest trends in {self.user_role}?",
                f"Where do you see yourself in 5 years in {self.user_role}?"
            ]
            return self.questions
    
    def cleanup(self):
        """Clean up audio resources"""
        # No explicit cleanup needed for sounddevice
        pass
    
    def test_audio_devices(self):
        """Test and list available audio devices"""
        try:
            print("🎤 Available Audio Devices:")
            devices = sd.query_devices()
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:  # Only show input devices
                    print(f"  {i}: {device['name']} - Input Channels: {device['max_input_channels']}")
            return True
        except Exception as e:
            print(f"❌ Audio device test failed: {e}")
            return False

class AudioHandler:
    def __init__(self, session: InterviewSession):
        self.session = session
        self.is_recording = False
        self.current_answer = ""
        self.silence_threshold = 3.0
        self.last_speech_time = None
    
    async def text_to_speech(self, text: str) -> bool:
        """Convert text to speech and play it"""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tts = gTTS(text=text, lang='en', slow=False)
                tts.save(tmp_file.name)
                
                # Play the audio
                pygame.mixer.music.load(tmp_file.name)
                pygame.mixer.music.play()
                
                # Wait for playback to finish
                while pygame.mixer.music.get_busy():
                    await asyncio.sleep(0.1)
                
                # Clean up
                os.unlink(tmp_file.name)
                return True
        except Exception as e:
            print(f"TTS Error: {e}")
            return False
    
    async def speech_to_text(self, max_duration: int = 120) -> str:
        """Record and convert speech to text with silence detection using sounddevice"""
        self.is_recording = True
        self.current_answer = ""
        silence_start = None
        answer_parts = []
        
        print("🎤 Recording... (3 seconds of silence to finish)")
        
        # Audio recording parameters
        chunk_duration = 0.5  # Record in 0.5 second chunks
        sample_rate = self.session.sample_rate
        channels = self.session.channels
        
        try:
            start_time = time.time()
            
            while self.is_recording and (time.time() - start_time) < max_duration:
                try:
                    # Record a chunk using sounddevice
                    audio_chunk = sd.rec(
                        int(chunk_duration * sample_rate),
                        samplerate=sample_rate,
                        channels=channels,
                        dtype=self.session.dtype
                    )
                    sd.wait()  # Wait for recording to complete
                    
                    # Convert to bytes for Vosk
                    audio_bytes = audio_chunk.tobytes()
                    
                    if self.session.stt_recognizer.AcceptWaveform(audio_bytes):
                        result = json.loads(self.session.stt_recognizer.Result())
                        text = result.get("text", "").strip()
                        
                        if text:
                            answer_parts.append(text)
                            print(f"✅ Recognized: {text}")
                            silence_start = None
                    else:
                        partial = json.loads(self.session.stt_recognizer.PartialResult())
                        partial_text = partial.get("partial", "")
                        
                        if partial_text:
                            print(f"⏳ Speaking: {partial_text}")
                            silence_start = None
                        else:
                            # No speech detected
                            if silence_start is None:
                                silence_start = time.time()
                            elif time.time() - silence_start >= self.silence_threshold:
                                print("🔇 Silence detected. Finishing recording...")
                                break
                                
                except Exception as e:
                    print(f"STT Error: {e}")
                    break
                    
        finally:
            # No explicit cleanup needed for sounddevice
            pass
        
        self.is_recording = False
        self.current_answer = " ".join(answer_parts)
        return self.current_answer

class EmotionAnalyzer:
    def __init__(self):
        self.emotion_history = []
        
    def analyze_webcam_frame(self, frame: np.ndarray) -> Dict:
        """Analyze emotion from webcam frame"""
        result = deepface_analyzer.analyze_frame(frame)
        
        if result['success']:
            emotion_data = {
                'timestamp': datetime.now().isoformat(),
                'emotion': result['emotion'],
                'confidence': result['confidence'],
                'emotion_scores': result['emotion_scores']
            }
            self.emotion_history.append(emotion_data)
            
        return result
    
    def get_emotion_summary(self) -> Dict:
        """Get summary of emotions throughout interview"""
        if not self.emotion_history:
            return {'dominant_emotion': 'neutral', 'confidence': 0, 'distribution': {}}
        
        emotions = [data['emotion'] for data in self.emotion_history]
        emotion_counts = {}
        
        for emotion in emotions:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        total_frames = len(emotions)
        emotion_distribution = {
            emotion: (count / total_frames) * 100 
            for emotion, count in emotion_counts.items()
        }
        
        dominant_emotion = max(emotion_counts.keys(), key=lambda x: emotion_counts[x]) if emotion_counts else 'neutral'
        avg_confidence = np.mean([data['confidence'] for data in self.emotion_history])
        
        return {
            'dominant_emotion': dominant_emotion,
            'confidence': avg_confidence,
            'distribution': emotion_distribution,
            'total_frames': total_frames
        }

class InterviewScorer:
    def __init__(self):
        self.emotion_weight = 0.3
        self.answer_weight = 0.7
        
    def score_answer(self, question: str, answer: str, user_role: str) -> Dict:
        """Score individual answer using LLM"""
        prompt = f"""
        Evaluate this interview answer for a {user_role} position:
        
        Question: {question}
        Answer: {answer}
        
        Provide a score from 0-100 and brief feedback. Consider:
        - Relevance to the question
        - Technical accuracy (if applicable)
        - Communication clarity
        - Depth of response
        
        Return ONLY a JSON object like this:
        {{
            "score": 85,
            "feedback": "Good technical knowledge but could provide more specific examples.",
            "strengths": ["Clear communication", "Relevant experience"],
            "improvements": ["Add specific examples", "More detail needed"]
        }}
        """
        
        try:
            response = llm.invoke(prompt)
            content = response.content.strip()
            
            if content.startswith('```json'):
                content = content[7:-3]
            elif content.startswith('```'):
                content = content[3:-3]
                
            return json.loads(content)
        except:
            return {
                "score": 70,
                "feedback": "Answer received and processed.",
                "strengths": ["Responded to question"],
                "improvements": ["Could provide more detail"]
            }
    
    def calculate_final_score(self, answer_scores: List[int], emotion_summary: Dict) -> Dict:
        """Calculate final interview score"""
        # Calculate average answer score
        avg_answer_score = np.mean(answer_scores) if answer_scores else 0
        
        # Calculate emotion score
        emotion_score = self.calculate_emotion_score(emotion_summary)
        
        # Weighted final score
        final_score = (avg_answer_score * self.answer_weight) + (emotion_score * self.emotion_weight)
        
        return {
            'final_score': round(final_score, 2),
            'answer_score': round(avg_answer_score, 2),
            'emotion_score': round(emotion_score, 2),
            'breakdown': {
                'answers': f"{self.answer_weight * 100}%",
                'emotions': f"{self.emotion_weight * 100}%"
            }
        }
    
    def calculate_emotion_score(self, emotion_summary: Dict) -> float:
        """Calculate score based on emotion analysis"""
        emotion_scores = {
            'happy': 100,
            'neutral': 85,
            'surprise': 75,
            'sad': 60,
            'fear': 50,
            'angry': 40,
            'disgust': 35
        }
        
        dominant_emotion = emotion_summary.get('dominant_emotion', 'neutral')
        confidence = emotion_summary.get('confidence', 0)
        
        base_score = emotion_scores.get(dominant_emotion, 70)
        
        # Adjust based on confidence
        confidence_factor = min(confidence / 100, 1.0)
        adjusted_score = base_score * (0.8 + 0.2 * confidence_factor)
        
        return min(adjusted_score, 100)

class ReportGenerator:
    def __init__(self):
        self.scorer = InterviewScorer()
    
    def generate_comprehensive_report(self, session: InterviewSession, 
                                    answer_scores: List[Dict], 
                                    emotion_summary: Dict) -> Dict:
        """Generate final interview report"""
        
        # Calculate scores
        score_values = [score['score'] for score in answer_scores]
        final_scoring = self.scorer.calculate_final_score(score_values, emotion_summary)
        
        # Generate overall feedback
        overall_feedback = self.generate_overall_feedback(session, answer_scores, emotion_summary)
        
        # Calculate interview duration
        duration = datetime.now() - session.session_start_time
        
        report = {
            'interview_summary': {
                'user_role': session.user_role,
                'date': session.session_start_time.strftime('%Y-%m-%d %H:%M:%S'),
                'duration': str(duration).split('.')[0],
                'questions_answered': len(session.answers)
            },
            'scoring': final_scoring,
            'question_analysis': [
                {
                    'question': session.questions[i],
                    'answer': session.answers[i],
                    'score': answer_scores[i]['score'],
                    'feedback': answer_scores[i]['feedback'],
                    'strengths': answer_scores[i]['strengths'],
                    'improvements': answer_scores[i]['improvements']
                }
                for i in range(len(session.answers))
            ],
            'emotion_analysis': emotion_summary,
            'overall_feedback': overall_feedback,
            'recommendations': self.generate_recommendations(final_scoring, emotion_summary)
        }
        
        return report
    
    def generate_overall_feedback(self, session: InterviewSession, 
                                answer_scores: List[Dict], 
                                emotion_summary: Dict) -> str:
        """Generate overall interview feedback using LLM"""
        
        qa_summary = "\n".join([
            f"Q: {session.questions[i]}\nA: {session.answers[i]}\nScore: {answer_scores[i]['score']}"
            for i in range(len(session.answers))
        ])
        
        prompt = f"""
        Generate overall interview feedback for a {session.user_role} candidate:
        
        Q&A Summary:
        {qa_summary}
        
        Emotion Analysis:
        - Dominant emotion: {emotion_summary.get('dominant_emotion', 'neutral')}
        - Emotion distribution: {emotion_summary.get('distribution', {})}
        
        Provide constructive feedback focusing on:
        1. Overall performance
        2. Communication skills
        3. Technical competency
        4. Areas for improvement
        5. Positive aspects
        
        Keep it professional and encouraging.
        """
        
        try:
            response = llm.invoke(prompt)
            return response.content
        except:
            return "Interview completed successfully. Continue practicing to improve your skills."
    
    def generate_recommendations(self, scoring: Dict, emotion_summary: Dict) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        # Score-based recommendations
        if scoring['final_score'] < 60:
            recommendations.append("Focus on improving technical knowledge and providing more detailed answers")
        elif scoring['final_score'] < 80:
            recommendations.append("Good foundation - work on providing specific examples and deeper insights")
        else:
            recommendations.append("Excellent performance - maintain this level of preparation")
        
        # Emotion-based recommendations
        dominant_emotion = emotion_summary.get('dominant_emotion', 'neutral')
        
        if dominant_emotion in ['fear', 'sad']:
            recommendations.append("Practice relaxation techniques before interviews to appear more confident")
        elif dominant_emotion == 'angry':
            recommendations.append("Work on maintaining composure and positive body language")
        elif dominant_emotion == 'happy':
            recommendations.append("Great emotional presence - maintain this positive energy")
        
        return recommendations

# Main Interview Controller
class InterviewController:
    def __init__(self, user_role: str):
        self.session = InterviewSession(user_role)
        self.audio_handler = AudioHandler(self.session)
        self.emotion_analyzer = EmotionAnalyzer()
        self.report_generator = ReportGenerator()
        self.answer_scores = []
        
    async def start_interview(self) -> Dict:
        """Start the complete interview process"""
        try:
            # Initialize questions
            questions = self.session.initialize_questions()
            print(f"✅ Generated {len(questions)} questions for {self.session.user_role}")
            
            self.session.is_active = True
            
            # Conduct interview
            for i, question in enumerate(questions):
                print(f"\n🎯 Question {i+1}/{len(questions)}")
                
                # Ask question using TTS
                await self.audio_handler.text_to_speech(question)
                
                # Record answer using STT
                answer = await self.audio_handler.speech_to_text()
                self.session.answers.append(answer)
                
                # Score the answer
                score_result = self.report_generator.scorer.score_answer(
                    question, answer, self.session.user_role
                )
                self.answer_scores.append(score_result)
                
                print(f"📝 Answer recorded: {answer[:100]}...")
                print(f"📊 Score: {score_result['score']}/100")
                
                # Generate adaptive follow-up if needed
                if i < len(questions) - 1:
                    follow_up = await self.generate_adaptive_question()
                    if follow_up:
                        questions.append(follow_up)
            
            # Generate final report
            emotion_summary = self.emotion_analyzer.get_emotion_summary()
            final_report = self.report_generator.generate_comprehensive_report(
                self.session, self.answer_scores, emotion_summary
            )
            
            self.session.is_active = False
            return final_report
            
        except Exception as e:
            print(f"❌ Interview error: {e}")
            return {'error': str(e)}
    
    async def generate_adaptive_question(self) -> Optional[str]:
        """Generate adaptive follow-up question based on previous answers"""
        if len(self.session.answers) < 2:
            return None
            
        context = "\n".join([
            f"Q: {self.session.questions[i]}\nA: {self.session.answers[i]}"
            for i in range(len(self.session.answers))
        ])
        
        prompt = f"""
        Based on the previous Q&A for {self.session.user_role}:
        {context}
        
        Generate 1 relevant follow-up question to explore deeper or cover different aspects.
        Make it specific to their answers and role.
        Return only the question, no explanations.
        """
        
        try:
            response = llm.invoke(prompt)
            return response.content.strip()
        except:
            return None
    
    def add_emotion_data(self, frame: np.ndarray):
        """Add emotion analysis for current frame"""
        result = self.emotion_analyzer.analyze_webcam_frame(frame)
        return result