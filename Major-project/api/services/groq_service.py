"""AIVOX — Groq Whisper STT Service
Receives raw audio bytes from the client browser (MediaRecorder output)
and transcribes using Groq's ultra-fast Whisper API.
"""

import os
import io
from groq import AsyncGroq


class GroqService:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY environment variable is not set")
        self.client = AsyncGroq(api_key=api_key)

    async def transcribe(self, audio_bytes: bytes, content_type: str) -> dict:
        """
        Transcribe audio bytes using Groq Whisper.

        Args:
            audio_bytes: Raw audio file bytes from browser MediaRecorder
            content_type: MIME type (e.g. 'audio/webm', 'audio/wav')

        Returns:
            { transcript: str, duration_seconds: float }
        """
        # Map MIME type to file extension for Groq API
        ext_map = {
            "audio/webm": "webm",
            "audio/wav": "wav",
            "audio/ogg": "ogg",
            "audio/mp4": "mp4",
            "audio/mpeg": "mp3",
        }
        ext = ext_map.get(content_type, "webm")
        filename = f"recording.{ext}"

        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = filename

        transcription = await self.client.audio.transcriptions.create(
            file=(filename, audio_bytes, content_type),
            model="whisper-large-v3-turbo",  # Fastest Groq Whisper model
            response_format="verbose_json",   # Includes duration
            language="en",
            temperature=0.0,
        )

        return {
            "transcript": transcription.text.strip(),
            "duration_seconds": getattr(transcription, "duration", 0.0),
        }
