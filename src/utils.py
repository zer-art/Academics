import os
import requests
from dotenv import load_dotenv
from google.cloud import texttospeech, speech

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI')
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

def generate_interview_questions(topic, num_questions=10, job_level="mid-level"):
	"""
	Generate interview questions for a specific topic/job title.
	
	Args:
		topic (str): The job title or topic for questions
		num_questions (int): Number of questions to generate
		job_level (str): Experience level (entry-level, mid-level, senior-level)
	
	Returns:
		list: List of interview questions
	"""
	if not GEMINI_API_KEY:
		raise ValueError("Gemini API key not found in environment variables.")
	
	prompt = f"""
	Generate exactly {num_questions} professional interview questions for a {job_level} {topic} position.
	
	Include a mix of:
	- Technical questions specific to the role
	- Behavioral questions
	- Situational questions
	- Problem-solving scenarios
	
	Format each question clearly and make them appropriate for a {job_level} candidate.
	Number each question (1., 2., etc.).
	"""
	
	headers = {"Content-Type": "application/json"}
	params = {"key": GEMINI_API_KEY}
	data = {
		"contents": [{"parts": [{"text": prompt}]}]
	}
	
	try:
		response = requests.post(GEMINI_API_URL, headers=headers, params=params, json=data)
		response.raise_for_status()
		result = response.json()
		
		text = result['candidates'][0]['content']['parts'][0]['text']
		questions = []
		
		# Extract numbered questions
		for line in text.split('\n'):
			line = line.strip()
			if line and any(line.startswith(f"{i}.") for i in range(1, num_questions + 1)):
				question = line.split('.', 1)[1].strip()
				if question:
					questions.append(question)
		
		# Fallback to splitting by lines if numbered extraction fails
		if len(questions) < num_questions // 2:
			questions = [q.strip() for q in text.split('\n') if q.strip() and len(q.strip()) > 10]
		
		return questions[:num_questions]
		
	except Exception as e:
		print(f"Error generating questions: {e}")
		return get_fallback_questions(topic, num_questions)

def get_fallback_questions(job_title, num_questions=10):
	"""
	Provide fallback questions when API is unavailable.
	"""
	general_questions = [
		"Tell me about yourself and your professional background.",
		f"Why are you interested in this {job_title} position?",
		"What are your greatest professional strengths?",
		"Describe a challenging project you worked on recently.",
		"How do you handle working under pressure and tight deadlines?",
		"Where do you see yourself professionally in 5 years?",
		"Describe a time when you had to learn a new skill quickly.",
		"How do you approach problem-solving in your work?",
		"Tell me about a time you worked effectively in a team.",
		"How do you stay updated with industry trends and developments?",
		"Describe a situation where you had to handle criticism.",
		"What motivates you most in your professional work?",
		"Tell me about a time you had to make a difficult decision.",
		"How do you prioritize multiple tasks and projects?",
		"Do you have any questions about our company or this role?"
	]
	
	return general_questions[:num_questions]


def text_to_speech(text, output_path):
	client = texttospeech.TextToSpeechClient()
	synthesis_input = texttospeech.SynthesisInput(text=text)
	voice = texttospeech.VoiceSelectionParams(
		language_code="en-US",
		ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
	)
	audio_config = texttospeech.AudioConfig(
		audio_encoding=texttospeech.AudioEncoding.MP3
	)
	response = client.synthesize_speech(
		input=synthesis_input,
		voice=voice,
		audio_config=audio_config
	)
	with open(output_path, "wb") as out:
		out.write(response.audio_content)
	return output_path

def speech_to_text(audio_path):
	client = speech.SpeechClient()
	with open(audio_path, "rb") as audio_file:
		content = audio_file.read()
	audio = speech.RecognitionAudio(content=content)
	config = speech.RecognitionConfig(
		encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
		sample_rate_hertz=16000,
		language_code="en-US"
	)
	response = client.recognize(config=config, audio=audio)
	transcript = " ".join([result.alternatives[0].transcript for result in response.results])
	return transcript
