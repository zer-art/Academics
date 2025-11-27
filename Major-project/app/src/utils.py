import json
import asyncio
import queue
import time
import enum
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from threading import Lock
import numpy as np
import cv2
import sounddevice as sd
import soundfile as sf
from gtts import gTTS
import pygame
import tempfile
import os
import torch
import torchaudio
import threading
from groq import Groq
from collections import deque

from app.src.facemesh import facemesh_analyzer
from app.src.llm import llm


class InterviewState(enum.Enum):
    """State machine for interview process to prevent AI self-hearing"""

    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"


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
        self.dtype = "int16"

        # Remove Vosk initialization
        # Remove pygame initialization from here

        # New answer handling
        self.current_answer_parts = []
        self.final_answer = ""
        self.answer_callback = None

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
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
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
                f"Where do you see yourself in 5 years in {self.user_role}?",
            ]
            return self.questions

    def cleanup(self):
        """Clean up resources"""
        # No Vosk cleanup needed
        pass

    def test_audio_devices(self):
        """Test audio devices"""
        try:
            print("🎤 Available Audio Devices:")
            devices = sd.query_devices()
            for i, device in enumerate(devices):
                if device["max_input_channels"] > 0:
                    print(
                        f"  {i}: {device['name']} - Input Channels: {device['max_input_channels']}"
                    )
            return True
        except Exception as e:
            print(f"❌ Audio device test failed: {e}")
            return False


class ModernAudioHandler:
    def __init__(self, session):
        self.session = session
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        # Audio parameters
        self.sample_rate = 16000
        self.channels = 1
        # Silero VAD expects exactly 512 samples for 16kHz (32ms chunks)
        self.vad_chunk_size = 512  # Required by Silero VAD for 16kHz
        self.audio_chunk_size = int(0.1 * self.sample_rate)  # 100ms for audio capture
        self.buffer_duration = 0.5  # 500ms rolling buffer
        self.buffer_size = int(self.buffer_duration * self.sample_rate)

        # VAD setup
        self.vad_model, _ = torch.hub.load(
            repo_or_dir="snakers4/silero-vad", model="silero_vad"
        )
        self.vad_model.eval()

        # State management with thread safety
        self.current_state = InterviewState.IDLE
        self.state_lock = Lock()
        self.is_ai_speaking = False

        # Audio state
        self.is_listening = False
        self.is_recording = False
        self.audio_buffer = deque(maxlen=self.buffer_size)
        self.recording_buffer = []
        self.silence_start = None
        self.last_speech_time = None

        # Thresholds
        self.voice_threshold = 0.5
        self.silence_threshold = 1.0  # 1s silence to stop recording
        self.answer_complete_threshold = 3.0  # 3s to complete answer

        # Threading
        self.audio_queue = queue.Queue()
        self.stop_event = threading.Event()

        # Initialize pygame for TTS
        pygame.mixer.init()

    def set_state(self, new_state: InterviewState):
        """Thread-safe state change with logging"""
        with self.state_lock:
            old_state = self.current_state
            self.current_state = new_state
            print(f"🔄 State: {old_state.value} → {new_state.value}")

            # Clear audio buffer when entering LISTENING state
            if new_state == InterviewState.LISTENING:
                self._flush_audio_buffer()
                self._reset_user_answer()

    def get_state(self) -> InterviewState:
        """Thread-safe state getter"""
        with self.state_lock:
            return self.current_state

    def _flush_audio_buffer(self):
        """Clear audio buffer and recording state to prevent AI echo"""
        print("🧹 Flushing audio buffer to prevent AI echo")
        self.audio_buffer.clear()
        self.recording_buffer = []
        self.is_recording = False
        self.silence_start = None
        self.last_speech_time = None

        # Drain the audio queue
        try:
            while True:
                self.audio_queue.get_nowait()
        except queue.Empty:
            pass

    def _reset_user_answer(self):
        """Reset user answer variables"""
        self.session.current_answer_parts = []
        self.session.final_answer = ""
        print("🔄 User answer reset - ready for input")

    def start_listening(self):
        """Start continuous audio monitoring"""
        if self.is_listening:
            return

        self.is_listening = True
        self.stop_event.clear()

        # Start audio capture thread
        self.audio_thread = threading.Thread(target=self._audio_capture_loop)
        self.audio_thread.daemon = True
        self.audio_thread.start()

        # Start VAD processing thread
        self.vad_thread = threading.Thread(target=self._vad_processing_loop)
        self.vad_thread.daemon = True
        self.vad_thread.start()

        print("🎤 Audio monitoring started...")

    def stop_listening(self):
        """Stop audio monitoring"""
        self.is_listening = False
        self.stop_event.set()

        if hasattr(self, "audio_thread"):
            self.audio_thread.join(timeout=2)
        if hasattr(self, "vad_thread"):
            self.vad_thread.join(timeout=2)

        print("🔇 Audio monitoring stopped")

    def _audio_capture_loop(self):
        """Continuous audio capture with state-aware filtering"""

        def audio_callback(indata, frames, time, status):
            if status:
                print(f"Audio callback status: {status}")

            # CRITICAL: Check if AI is speaking - if so, discard audio immediately
            if self.is_ai_speaking or self.get_state() == InterviewState.SPEAKING:
                # Silently discard audio while AI is speaking to prevent self-hearing
                return

            # Only process audio in LISTENING state
            current_state = self.get_state()
            if current_state != InterviewState.LISTENING:
                return

            # Add to buffer and queue for processing
            audio_chunk = indata[:, 0].copy()  # Take first channel
            self.audio_buffer.extend(audio_chunk)
            self.audio_queue.put(audio_chunk)

        try:
            with sd.InputStream(
                callback=audio_callback,
                channels=self.channels,
                samplerate=self.sample_rate,
                blocksize=self.audio_chunk_size,
                dtype="float32",
            ):
                while not self.stop_event.wait(0.1):
                    pass
        except Exception as e:
            print(f"Audio capture error: {e}")

    def _vad_processing_loop(self):
        """Process audio chunks with state awareness"""
        while not self.stop_event.is_set():
            try:
                # Only process if in LISTENING state and AI not speaking
                if self.get_state() != InterviewState.LISTENING or self.is_ai_speaking:
                    # Drain queue but don't process to prevent echo
                    try:
                        self.audio_queue.get(timeout=0.1)
                    except queue.Empty:
                        pass
                    continue

                # Get audio chunk with timeout
                audio_chunk = self.audio_queue.get(timeout=0.1)

                # Process VAD in smaller chunks that match Silero requirements
                self._process_vad_chunks(audio_chunk)

            except queue.Empty:
                continue
            except Exception as e:
                print(f"VAD processing error: {e}")

    def _process_vad_chunks(self, audio_chunk):
        """Process audio chunk in VAD-compatible sizes"""
        try:
            # Convert audio chunk to smaller VAD chunks
            chunk_length = len(audio_chunk)

            # Process in 512-sample chunks for Silero VAD
            for i in range(0, chunk_length, self.vad_chunk_size):
                end_idx = min(i + self.vad_chunk_size, chunk_length)
                vad_chunk = audio_chunk[i:end_idx]

                # Only process if we have exactly 512 samples
                if len(vad_chunk) == self.vad_chunk_size:
                    # Convert to tensor for VAD
                    audio_tensor = torch.from_numpy(vad_chunk).float()

                    # Run VAD
                    speech_prob = self.vad_model(
                        audio_tensor.unsqueeze(0), self.sample_rate
                    ).item()

                    self._handle_vad_result(speech_prob, vad_chunk)

        except Exception as e:
            print(f"VAD chunk processing error: {e}")

    def _handle_vad_result(self, speech_prob, audio_chunk):
        """Handle VAD detection results with state verification"""
        # CRITICAL: Double check we're in correct state and AI not speaking
        if self.get_state() != InterviewState.LISTENING or self.is_ai_speaking:
            return

        current_time = time.time()
        is_speech = speech_prob > self.voice_threshold

        if is_speech:
            self.last_speech_time = current_time
            self.silence_start = None

            if not self.is_recording:
                # Start recording - include buffer
                self.is_recording = True
                self.recording_buffer = list(self.audio_buffer)
                print("🎤 Started recording USER voice (verified not AI)")

            self.recording_buffer.extend(audio_chunk)

        else:  # Silence detected
            if self.is_recording:
                if self.silence_start is None:
                    self.silence_start = current_time
                elif current_time - self.silence_start >= self.silence_threshold:
                    # Stop recording after silence threshold
                    self._finish_recording()
                else:
                    # Still in silence period, keep adding audio
                    self.recording_buffer.extend(audio_chunk)

    def _finish_recording(self):
        """Finish current recording and send to Groq"""
        if not self.is_recording or not self.recording_buffer:
            return

        self.is_recording = False
        audio_data = np.array(self.recording_buffer, dtype=np.float32)
        self.recording_buffer = []
        self.silence_start = None

        print(f"🎙️ Recording finished - {len(audio_data)/self.sample_rate:.2f}s")

        # Send to Groq in background
        threading.Thread(
            target=self._send_to_groq, args=(audio_data,), daemon=True
        ).start()

    def _send_to_groq(self, audio_data):
        """Send audio to Groq for transcription"""
        try:
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                # Convert float32 to int16 for WAV
                audio_int16 = (audio_data * 32767).astype(np.int16)

                # Save using soundfile (more reliable than torchaudio.save)
                sf.write(temp_file.name, audio_int16, self.sample_rate)

                # Send to Groq
                with open(temp_file.name, "rb") as audio_file:
                    transcript = self.groq_client.audio.transcriptions.create(
                        file=audio_file, model="whisper-large-v3", language="en"
                    )

                text = transcript.text.strip()
                if text:
                    print(f"📝 Transcribed: {text}")
                    self._handle_transcription(text)

            # Clean up temp file
            os.unlink(temp_file.name)

        except Exception as e:
            print(f"Groq transcription error: {e}")

    def _handle_transcription(self, text):
        """Handle transcribed text with state verification"""
        # CRITICAL: Verify we're in the correct state and AI isn't speaking
        if self.is_ai_speaking or self.get_state() != InterviewState.LISTENING:
            print(f"🚫 Discarded transcription (AI echo): '{text}'")
            return

        print(f"📝 Valid user transcription: '{text}'")

        # Add to current answer
        if hasattr(self.session, "current_answer_parts"):
            self.session.current_answer_parts.append(text)
        else:
            self.session.current_answer_parts = [text]

        # Check if answer seems complete
        self._check_answer_completion()

    def _check_answer_completion(self):
        """Check if the answer is complete based on silence duration"""
        if not self.last_speech_time:
            return

        silence_duration = time.time() - self.last_speech_time

        if silence_duration >= self.answer_complete_threshold:
            # Answer is complete
            complete_answer = " ".join(self.session.current_answer_parts)
            self.session.current_answer_parts = []

            print(f"✅ Answer complete: {complete_answer}")

            # Signal completion (could use callback or event)
            if hasattr(self.session, "answer_callback"):
                self.session.answer_callback(complete_answer)

    async def wait_for_user_answer(self, timeout=120) -> str:
        """Wait for complete user answer with state management"""
        print("👂 Waiting for user answer...")

        # CRITICAL: Set to LISTENING state (this flushes buffer and resets answer)
        self.set_state(InterviewState.LISTENING)

        answer_complete = asyncio.Event()

        def answer_callback(answer):
            self.session.final_answer = answer
            answer_complete.set()

        self.session.answer_callback = answer_callback

        try:
            # Wait for answer completion
            await asyncio.wait_for(answer_complete.wait(), timeout=timeout)

            # Set to PROCESSING state
            self.set_state(InterviewState.PROCESSING)

            final_answer = getattr(self.session, "final_answer", "")
            print(f"✅ User answer complete: '{final_answer[:100]}...'")
            return final_answer

        except asyncio.TimeoutError:
            self.set_state(InterviewState.PROCESSING)
            partial_answer = " ".join(self.session.current_answer_parts)
            print(f"⏰ Answer timeout, returning partial: '{partial_answer[:100]}...'")
            return partial_answer
        finally:
            # Ensure we're not stuck in LISTENING state
            if self.get_state() == InterviewState.LISTENING:
                self.set_state(InterviewState.IDLE)

    async def text_to_speech(self, text: str) -> bool:
        """TTS with strict state management to prevent self-hearing"""
        print(f"🔊 AI Speaking: '{text[:50]}...'")

        # CRITICAL: Set state to SPEAKING and flag AI as speaking
        self.set_state(InterviewState.SPEAKING)
        self.is_ai_speaking = True

        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                tts = gTTS(text=text, lang="en", slow=False)
                tts.save(tmp_file.name)

                # Play the audio (blocking)
                pygame.mixer.music.load(tmp_file.name)
                pygame.mixer.music.play()

                # Wait for playback to completely finish
                while pygame.mixer.music.get_busy():
                    await asyncio.sleep(0.1)

                # Additional safety delay for audio system settling
                await asyncio.sleep(0.2)

                # Clean up
                os.unlink(tmp_file.name)

                print("✅ AI finished speaking")
                return True

        except Exception as e:
            print(f"TTS Error: {e}")
            return False
        finally:
            # CRITICAL: Clear AI speaking flag and flush buffer
            self.is_ai_speaking = False
            self.set_state(InterviewState.IDLE)

            # Give a moment for the audio system to settle
            await asyncio.sleep(0.1)


class ConfidenceAnalyzer:
    """Analyze interview confidence using MediaPipe Face Mesh"""

    def __init__(self):
        self.analysis_history = []

    def analyze_webcam_frame(self, frame: np.ndarray) -> Dict:
        """Analyze confidence from webcam frame"""
        result = facemesh_analyzer.analyze_frame(frame)

        if result["success"]:
            analysis_data = {
                "timestamp": datetime.now().isoformat(),
                "confidence": result["confidence"],
                "head_alignment": result["head_alignment"],
                "speaking_engagement": result["speaking_engagement"],
                "positive_expression": result["positive_expression"],
                "feedback": result["feedback"],
            }
            self.analysis_history.append(analysis_data)

        return result

    def get_confidence_summary(self) -> Dict:
        """Get summary of confidence throughout interview"""
        if not self.analysis_history:
            return {
                "average_confidence": 0,
                "peak_confidence": 0,
                "low_points": 0,
                "trend": "stable",
            }

        confidences = [data["confidence"] for data in self.analysis_history]

        avg_confidence = np.mean(confidences)
        peak_confidence = np.max(confidences)
        low_points = sum(1 for c in confidences if c < 50)

        # Calculate trend (improving, declining, stable)
        if len(confidences) >= 10:
            first_half = np.mean(confidences[: len(confidences) // 2])
            second_half = np.mean(confidences[len(confidences) // 2 :])

            if second_half > first_half + 10:
                trend = "improving"
            elif second_half < first_half - 10:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"

        return {
            "average_confidence": round(avg_confidence, 2),
            "peak_confidence": round(peak_confidence, 2),
            "low_points": low_points,
            "total_frames": len(confidences),
            "trend": trend,
            "distribution": {
                "excellent": sum(1 for c in confidences if c >= 80),
                "good": sum(1 for c in confidences if 60 <= c < 80),
                "fair": sum(1 for c in confidences if 40 <= c < 60),
                "poor": sum(1 for c in confidences if c < 40),
            },
        }


class InterviewScorer:
    def __init__(self):
        self.emotion_weight = 0.2
        self.answer_weight = 0.8

    def score_answer(self, question: str, answer: str, user_role: str) -> Dict:
        """Score individual answer using LLM"""
        prompt = f"""
        As an expert interviewer for {user_role} positions, evaluate this interview response:
        
        🔍 QUESTION: {question}
        💬 ANSWER: {answer}
        
        EVALUATION CRITERIA:
        ✓ Content Relevance (25%): Does the answer directly address the question?
        ✓ Technical Accuracy (25%): Are technical concepts correct and appropriate?
        ✓ Communication Quality (25%): Is the response clear, well-structured, and professional?
        ✓ Depth & Examples (25%): Does the answer demonstrate understanding with specific examples?
        
        SCORING GUIDELINES:
        🏆 90-100: Exceptional - Comprehensive, accurate, well-articulated with excellent examples
        🥇 80-89: Strong - Good understanding, clear communication, relevant examples
        🥈 70-79: Satisfactory - Adequate response, some clarity issues or missing details
        🥉 60-69: Needs Work - Basic understanding but lacks depth or has inaccuracies
        ❌ Below 60: Poor - Irrelevant, inaccurate, or unclear response
        
        Return ONLY a JSON object with this exact structure:
        {{
            "score": [0-100],
            "feedback": "Professional, constructive feedback that highlights both positive aspects and areas for improvement. Use specific examples from the answer.",
            "strengths": ["Specific positive aspects demonstrated in the response", "Another strength with context"],
            "improvements": ["Actionable suggestions for enhancement", "Specific areas that need development"]
        }}
        """

        try:
            response = llm.invoke(prompt)
            content = response.content.strip()

            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]

            return json.loads(content)
        except:
            return {
                "score": 70,
                "feedback": "Answer received and processed.",
                "strengths": ["Responded to question"],
                "improvements": ["Could provide more detail"],
            }

    def calculate_final_score(
        self, answer_scores: List[int], confidence_summary: Dict
    ) -> Dict:
        """Calculate final interview score"""
        # Calculate average answer score
        avg_answer_score = np.mean(answer_scores) if answer_scores else 0

        # Calculate confidence score
        confidence_score = self.calculate_confidence_score(confidence_summary)

        # Weighted final score
        final_score = (avg_answer_score * self.answer_weight) + (
            confidence_score * self.emotion_weight
        )

        return {
            "final_score": round(final_score, 2),
            "answer_score": round(avg_answer_score, 2),
            "confidence_score": round(confidence_score, 2),
            "breakdown": {
                "answers": f"{self.answer_weight * 100}%",
                "confidence": f"{self.emotion_weight * 100}%",
            },
        }

    def calculate_confidence_score(self, confidence_summary: Dict) -> float:
        """Calculate score based on confidence analysis"""
        # Get average confidence from the summary
        avg_confidence = confidence_summary.get("average_confidence", 0)
        trend = confidence_summary.get("trend", "stable")

        # Base score from average confidence
        base_score = avg_confidence

        # Adjust based on trend
        if trend == "improving":
            trend_bonus = 5
        elif trend == "declining":
            trend_bonus = -5
        else:
            trend_bonus = 0

        adjusted_score = base_score + trend_bonus

        return min(max(adjusted_score, 0), 100)


class ReportGenerator:
    def __init__(self):
        self.scorer = InterviewScorer()

    def generate_comprehensive_report(
        self,
        session: InterviewSession,
        answer_scores: List[Dict],
        confidence_summary: Dict,
    ) -> Dict:
        """Generate final interview report"""

        # Calculate scores
        score_values = [score["score"] for score in answer_scores]
        final_scoring = self.scorer.calculate_final_score(
            score_values, confidence_summary
        )

        # Calculate interview duration
        duration = datetime.now() - session.session_start_time

        report = {
            "interview_summary": {
                "user_role": session.user_role,
                "date": session.session_start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "duration": str(duration).split(".")[0],
                "questions_answered": len(session.answers),
            },
            "scoring": final_scoring,
            "question_analysis": [
                {
                    "question": session.questions[i],
                    "answer": session.answers[i],
                    "score": answer_scores[i]["score"],
                    "feedback": answer_scores[i]["feedback"],
                    "strengths": answer_scores[i]["strengths"],
                    "improvements": answer_scores[i]["improvements"],
                }
                for i in range(len(session.answers))
            ],
            "confidence_analysis": confidence_summary,
            "recommendations": self.generate_recommendations(
                final_scoring, confidence_summary
            ),
        }

        return report

    def generate_overall_feedback(
        self,
        session: InterviewSession,
        answer_scores: List[Dict],
        confidence_summary: Dict,
    ) -> str:
        """Generate overall interview feedback using LLM"""

        qa_summary = "\n".join(
            [
                f"Q: {session.questions[i]}\nA: {session.answers[i]}\nScore: {answer_scores[i]['score']}"
                for i in range(len(session.answers))
            ]
        )

        prompt = f"""
        As an expert interview coach, provide comprehensive feedback for this {session.user_role} candidate:
        
        📊 INTERVIEW SUMMARY:
        {qa_summary}
        
        🎯 CONFIDENCE & PRESENCE:
        • Average Confidence: {confidence_summary.get('average_confidence', 0):.1f}%
        • Peak Confidence: {confidence_summary.get('peak_confidence', 0):.1f}%
        • Trend: {confidence_summary.get('trend', 'stable').title()}
        • Performance Distribution: {confidence_summary.get('distribution', {})}
        
        Generate a well-structured, professional interview feedback report covering:
        
        🌟 OVERALL PERFORMANCE SUMMARY:
        - Opening statement highlighting key strengths and overall impression
        
        💪 KEY STRENGTHS:
        - Specific achievements and positive behaviors observed
        - Technical competencies demonstrated
        - Communication effectiveness
        
        🎯 AREAS FOR DEVELOPMENT:
        - Constructive suggestions for improvement
        - Specific skills to focus on
        - Actionable next steps
        
        🧠 TECHNICAL COMPETENCY:
        - Knowledge depth assessment
        - Problem-solving approach evaluation
        
        💬 COMMUNICATION & PRESENCE:
        - Verbal communication effectiveness
        - Emotional intelligence and composure
        - Professional demeanor assessment
        
        🚀 RECOMMENDATIONS FOR SUCCESS:
        - Specific preparation strategies
        - Practice areas to focus on
        
        Format the response as clear, structured text with section headers. Use bullet points and professional language. Be encouraging while providing actionable insights.
        """

        try:
            response = llm.invoke(prompt)
            return response.content
        except:
            return "Interview completed successfully. Continue practicing to improve your skills."

    def generate_recommendations(
        self, scoring: Dict, confidence_summary: Dict
    ) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        final_score = scoring["final_score"]
        answer_score = scoring.get("answer_score", 0)
        confidence_score = scoring.get("confidence_score", 0)
        avg_confidence = confidence_summary.get("average_confidence", 0)
        trend = confidence_summary.get("trend", "stable")

        # Performance-based recommendations with specific actions
        if final_score >= 90:
            recommendations.append(
                "🏆 Outstanding Performance: You demonstrated exceptional interview skills. Continue this excellence and consider mentoring others preparing for similar roles."
            )
        elif final_score >= 80:
            recommendations.append(
                "🌟 Strong Performance: Excellent foundation with room for refinement. Focus on adding more quantified achievements and industry-specific examples to your responses."
            )
        elif final_score >= 70:
            recommendations.append(
                "💪 Good Foundation: Solid understanding demonstrated. Enhance your responses by providing more specific examples and addressing all parts of multi-faceted questions."
            )
        elif final_score >= 60:
            recommendations.append(
                "📈 Room for Growth: Basic competency shown. Focus on deepening your technical knowledge and practicing structured response frameworks (STAR method)."
            )
        else:
            recommendations.append(
                "🎯 Focused Improvement Needed: Invest time in fundamental preparation - research the role, practice common questions, and strengthen core competencies."
            )

        # Content quality recommendations
        if answer_score < 70:
            recommendations.append(
                "📚 Content Enhancement: Practice the STAR method (Situation, Task, Action, Result) for behavioral questions and prepare 3-5 detailed examples from your experience."
            )

        # Confidence and presence recommendations
        if confidence_score < 70:
            if avg_confidence < 50:
                recommendations.append(
                    "🎯 Camera Presence: Practice maintaining eye contact with the camera. Sit up straight and position yourself at eye level with the lens."
                )
            if trend == "declining":
                recommendations.append(
                    "💪 Stamina Building: Your confidence decreased during the interview. Practice longer mock interviews to build endurance and maintain energy."
                )
            recommendations.append(
                "😊 Engagement Enhancement: Speak more expressively and maintain positive facial expressions. Show enthusiasm for the role through your body language."
            )
        else:
            recommendations.append(
                "✨ Excellent Emotional Intelligence: Your professional demeanor and emotional presence were well-calibrated for the interview context."
            )

        # Technical skill recommendations
        if final_score < 75:
            recommendations.append(
                "🔧 Technical Preparation: Review job requirements, practice explaining complex concepts simply, and prepare questions that show your genuine interest in the role."
            )

        # Communication enhancement
        recommendations.append(
            "🗣️ Communication Mastery: Continue practicing clear, concise responses. Record yourself answering questions to identify speech patterns and areas for improvement."
        )

        return recommendations


# Main Interview Controller
class InterviewController:
    def __init__(self, user_role: str):
        self.session = InterviewSession(user_role)
        self.audio_handler = ModernAudioHandler(self.session)  # Use new handler
        self.confidence_analyzer = ConfidenceAnalyzer()
        self.report_generator = ReportGenerator()
        self.answer_scores = []

    async def generate_adaptive_question(self) -> Optional[str]:
        """Generate adaptive follow-up question based on previous answers"""
        if len(self.session.answers) < 2:
            return None

        context = "\n".join(
            [
                f"Q: {self.session.questions[i]}\nA: {self.session.answers[i]}"
                for i in range(len(self.session.answers))
            ]
        )

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

    def add_confidence_data(self, frame: np.ndarray):
        """Add confidence analysis for current frame"""
        result = self.confidence_analyzer.analyze_webcam_frame(frame)
        return result

    async def run_interview_loop(self):
        """Main interview loop with strict state management"""
        print("🎬 Starting AI Interview with State Machine Protection")

        # Start audio monitoring
        self.audio_handler.start_listening()

        try:
            questions = self.session.initialize_questions()

            for i, question in enumerate(questions):
                print(f"\n=== Question {i+1}/{len(questions)} ===")

                # AI asks question (SPEAKING state)
                await self.ask_question(question)

                # Wait for user answer (LISTENING state)
                answer = await self.get_user_answer()

                # Process answer (PROCESSING state)
                await self.process_answer(question, answer)

                # Brief pause between questions
                await asyncio.sleep(1)

        finally:
            self.audio_handler.stop_listening()

    async def ask_question(self, question: str):
        """Ask question with state management"""
        print(f"🤖 AI asking: {question}")

        # Ensure we start in correct state
        self.audio_handler.set_state(InterviewState.IDLE)

        # AI speaks (automatically sets SPEAKING state)
        success = await self.audio_handler.text_to_speech(question)

        if not success:
            print("❌ Failed to ask question via TTS")

        # Short pause after AI finishes speaking
        await asyncio.sleep(0.5)

    async def get_user_answer(self) -> str:
        """Get user answer with echo prevention"""
        print("👤 User turn to answer...")

        # This automatically sets LISTENING state and flushes buffers
        answer = await self.audio_handler.wait_for_user_answer()

        if not answer or answer.strip() == "":
            print("⚠️ No answer detected")
            return "No answer provided"

        return answer.strip()

    async def process_answer(self, question: str, answer: str):
        """Process and score the answer"""
        print(f"📊 Processing answer: '{answer[:50]}...'")

        # Ensure we're in processing state
        self.audio_handler.set_state(InterviewState.PROCESSING)

        # Score the answer
        score_result = self.report_generator.scorer.score_answer(
            question, answer, self.session.user_role
        )

        # Store results
        self.session.answers.append(answer)
        self.answer_scores.append(score_result)

        print(f"Score: {score_result['score']}/100")
        print(f"Feedback: {score_result['feedback'][:100]}...")

        # Set back to idle
        self.audio_handler.set_state(InterviewState.IDLE)
