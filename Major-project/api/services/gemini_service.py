"""AIVOX — Gemini Service
Uses google-genai SDK (not LangChain) for cleaner async support.
Handles: question generation + answer evaluation.
"""

import json
import os
from google import genai
from google.genai import types


class GeminiService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY environment variable is not set")
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.5-flash"

    async def generate_questions(self, role: str) -> list[str]:
        """Generate 5 focused interview questions for the given role."""
        prompt = f"""You are an expert technical interviewer hiring for a {role} position.

Generate exactly 5 interview questions. Mix these types:
- 1 behavioral question (Tell me about a time when...)
- 2 technical/skill-based questions specific to {role}
- 1 problem-solving scenario
- 1 motivation/culture-fit question

Rules:
- Questions must be specific to {role}, not generic
- Each question should be answerable in 1-3 minutes verbally
- Avoid yes/no questions

Return ONLY a JSON array of 5 strings. No markdown, no explanation:
["Question 1?", "Question 2?", "Question 3?", "Question 4?", "Question 5?"]"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=500,
                thinking_config=types.ThinkingConfig(thinking_budget=0),
            ),
        )

        print(f"[DEBUG] Gemini raw response: {repr(response.text)}")
        content = response.text.strip()
        # Strip markdown code fences if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()
        
        print(f"[DEBUG] Cleaned content: {repr(content)}")

        try:
            questions = json.loads(content)
        except Exception as e:
            print(f"[ERROR] JSON parse failed: {e}")
            raise e

        if not isinstance(questions, list) or len(questions) != 5:
            raise ValueError("Gemini returned unexpected question format")
        return questions

    async def evaluate_answer(self, question: str, answer: str, role: str) -> dict:
        """Score a single interview answer and provide structured feedback."""
        prompt = f"""You are an expert interviewer evaluating a candidate for a {role} position.

QUESTION: {question}
CANDIDATE'S ANSWER: {answer}

Evaluate based on:
- Content Relevance (25%): Does the answer address the question directly?
- Technical Accuracy (25%): Are concepts correct for a {role}?  
- Communication (25%): Is it clear, structured, and professional?
- Depth & Examples (25%): Does it demonstrate real experience with specifics?

Scoring:
- 90-100: Exceptional — comprehensive, accurate, excellent examples
- 80-89: Strong — good understanding, relevant examples
- 70-79: Satisfactory — adequate but missing depth
- 60-69: Needs Work — basic understanding, lacks specifics
- 0-59: Poor — off-topic, inaccurate, or too vague

Return ONLY valid JSON (no markdown):
{{
  "score": <integer 0-100>,
  "feedback": "<2-3 sentence constructive feedback mentioning specific parts of their answer>",
  "strengths": ["<specific strength 1>", "<specific strength 2>"],
  "improvements": ["<specific actionable improvement 1>", "<specific actionable improvement 2>"]
}}"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,  # Low temp for consistent scoring
                max_output_tokens=400,
                thinking_config=types.ThinkingConfig(thinking_budget=0),
            ),
        )

        content = response.text.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()

        result = json.loads(content)
        # Validate + clamp score
        result["score"] = max(0, min(100, int(result.get("score", 70))))
        result.setdefault("strengths", [])
        result.setdefault("improvements", [])
        return result
