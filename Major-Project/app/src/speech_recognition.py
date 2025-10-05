import asyncio
import aiohttp
import json
import base64
import os
import logging
from typing import Optional, Dict, Any
import tempfile

logger = logging.getLogger(__name__)


class AssemblyAIRecognizer:
    def __init__(self):
        # Try common environment variable names
        self.api_key = (
            os.getenv("ASSEMBLY_AI")
            or os.getenv("ASSEMBLY_AI_API_KEY")
            or os.getenv("ASSEMBLY_AI_KEY")
        )

        # Fallback to app.config if it's available in the import path
        if not self.api_key:
            try:
                from app.config import ASSEMBLY_AI as CONFIG_ASSEMBLY

                if CONFIG_ASSEMBLY:
                    self.api_key = CONFIG_ASSEMBLY
            except Exception:
                pass

        if not self.api_key:
            logger.warning(
                "Assembly AI API key not found in environment variables or config"
            )

        self.upload_url = "https://api.assemblyai.com/v2/upload"
        self.transcript_url = "https://api.assemblyai.com/v2/transcript"

        self.headers = {
            "authorization": self.api_key,
            "content-type": "application/json",
        }

        self.upload_headers = {"authorization": self.api_key}

    def is_available(self) -> bool:
        """Check if Assembly AI is properly configured"""
        return bool(self.api_key)

    async def upload_audio(self, audio_data: bytes) -> str:
        """Upload audio file to Assembly AI and return the upload URL"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.upload_url, headers=self.upload_headers, data=audio_data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["upload_url"]
                    else:
                        error_text = await response.text()
                        raise Exception(
                            f"Upload failed with status {response.status}: {error_text}"
                        )
        except Exception as e:
            logger.error(f"Error uploading audio: {e}")
            raise

    async def transcribe_audio(
        self, audio_url: str, config: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Transcribe audio using Assembly AI"""
        try:
            # Default configuration optimized for interviews
            transcript_config = {
                "audio_url": audio_url,
                "speech_model": "best",
                "language_detection": True,
                "punctuate": True,
                "format_text": True,
                "speaker_labels": False,
                "sentiment_analysis": True,
                "entity_detection": False,
                "auto_highlights": False,
                "content_safety": False,
                "boost_param": "high",
                "redact_pii": False,
            }

            # Update with custom config if provided
            if config:
                transcript_config.update(config)

            async with aiohttp.ClientSession() as session:
                # Submit transcription request
                async with session.post(
                    self.transcript_url, headers=self.headers, json=transcript_config
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        transcript_id = result["id"]
                        logger.info(f"Transcription submitted with ID: {transcript_id}")
                    else:
                        error_text = await response.text()
                        raise Exception(
                            f"Transcription request failed with status {response.status}: {error_text}"
                        )

                # Poll for completion
                polling_url = f"{self.transcript_url}/{transcript_id}"
                max_attempts = 60  # 3 minutes max wait time
                attempt = 0

                while attempt < max_attempts:
                    await asyncio.sleep(3)  # Wait 3 seconds between polls
                    attempt += 1

                    async with session.get(
                        polling_url, headers=self.headers
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            status = result["status"]

                            if status == "completed":
                                logger.info(f"Transcription completed successfully")
                                return result
                            elif status == "error":
                                error_msg = result.get("error", "Unknown error")
                                raise Exception(f"Transcription failed: {error_msg}")
                            else:
                                logger.debug(
                                    f"Transcription status: {status} (attempt {attempt}/{max_attempts})"
                                )
                        else:
                            error_text = await response.text()
                            logger.warning(
                                f"Polling attempt {attempt} failed: {error_text}"
                            )

                raise Exception("Transcription timed out - exceeded maximum wait time")

        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise

    async def transcribe_file(
        self, file_path: str, config: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Transcribe audio file"""
        try:
            # Read audio file
            with open(file_path, "rb") as audio_file:
                audio_data = audio_file.read()

            logger.info(f"Transcribing file: {file_path} ({len(audio_data)} bytes)")

            # Upload and transcribe
            upload_url = await self.upload_audio(audio_data)
            return await self.transcribe_audio(upload_url, config)

        except Exception as e:
            logger.error(f"Error transcribing file {file_path}: {e}")
            raise

    async def transcribe_bytes(
        self, audio_bytes: bytes, config: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Transcribe audio from bytes"""
        try:
            logger.info(f"Transcribing audio bytes ({len(audio_bytes)} bytes)")

            # Upload and transcribe
            upload_url = await self.upload_audio(audio_bytes)
            return await self.transcribe_audio(upload_url, config)

        except Exception as e:
            logger.error(f"Error transcribing audio bytes: {e}")
            raise

    async def transcribe_base64(
        self, audio_base64: str, config: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Transcribe base64 encoded audio"""
        try:
            # Remove data URL prefix if present
            if "," in audio_base64:
                audio_base64 = audio_base64.split(",", 1)[1]

            # Decode base64
            audio_bytes = base64.b64decode(audio_base64)

            return await self.transcribe_bytes(audio_bytes, config)

        except Exception as e:
            logger.error(f"Error transcribing base64 audio: {e}")
            raise

    def extract_insights(self, transcription_result: Dict) -> Dict[str, Any]:
        """Extract useful insights from transcription result"""
        try:
            insights = {
                "text": transcription_result.get("text", ""),
                "confidence": transcription_result.get("confidence", 0.0),
                "word_count": len(transcription_result.get("text", "").split()),
                "duration": transcription_result.get("audio_duration", 0),
                "language": transcription_result.get("language_code", "en"),
            }

            # Add sentiment analysis if available
            sentiment_results = transcription_result.get(
                "sentiment_analysis_results", []
            )
            if sentiment_results:
                sentiments = [
                    s.get("sentiment") for s in sentiment_results if s.get("sentiment")
                ]
                if sentiments:
                    # Calculate overall sentiment
                    positive_count = sentiments.count("POSITIVE")
                    negative_count = sentiments.count("NEGATIVE")
                    neutral_count = sentiments.count("NEUTRAL")

                    insights["sentiment"] = {
                        "overall": max(
                            ["POSITIVE", "NEGATIVE", "NEUTRAL"],
                            key=lambda x: [
                                positive_count,
                                negative_count,
                                neutral_count,
                            ][["POSITIVE", "NEGATIVE", "NEUTRAL"].index(x)],
                        ),
                        "positive_count": positive_count,
                        "negative_count": negative_count,
                        "neutral_count": neutral_count,
                    }

            return insights

        except Exception as e:
            logger.error(f"Error extracting insights: {e}")
            return {
                "text": transcription_result.get("text", ""),
                "confidence": 0.0,
                "word_count": 0,
                "duration": 0,
            }


# Global recognizer instance
assembly_recognizer = AssemblyAIRecognizer()
