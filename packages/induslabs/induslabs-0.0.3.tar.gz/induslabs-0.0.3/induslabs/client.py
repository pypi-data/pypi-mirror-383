"""
IndusLabs Voice API SDK
A Python client for text-to-speech and speech-to-text services.
"""

import os
import aiohttp
import requests
from typing import Optional, Union, AsyncIterator, Iterator, BinaryIO, List
from pathlib import Path
import io


__version__ = "0.0.3"


class Voice:
    """Represents a single voice."""

    def __init__(self, name: str, voice_id: str, gender: str, language: str):
        self.name = name
        self.voice_id = voice_id
        self.gender = gender
        self.language = language

    def __repr__(self) -> str:
        return (
            f"Voice(name='{self.name}', voice_id='{self.voice_id}', "
            f"gender='{self.gender}', language='{self.language}')"
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "voice_id": self.voice_id,
            "gender": self.gender,
            "language": self.language,
        }


class VoiceResponse:
    """Response object for voice listing requests."""

    def __init__(self, data: dict):
        self.status_code = data.get("status_code")
        self.message = data.get("message")
        self.error = data.get("error")
        self._raw_data = data.get("data", {})
        self.voices = self._parse_voices()

    def _parse_voices(self) -> List[Voice]:
        """Parse voice data into Voice objects."""
        voices = []
        for language, voice_list in self._raw_data.items():
            for voice_data in voice_list:
                voices.append(
                    Voice(
                        name=voice_data["name"],
                        voice_id=voice_data["voice_id"],
                        gender=voice_data["gender"],
                        language=language,
                    )
                )
        return voices

    def get_voices_by_language(self, language: str) -> List[Voice]:
        """Get all voices for a specific language."""
        return [v for v in self.voices if v.language == language]

    def get_voices_by_gender(self, gender: str) -> List[Voice]:
        """Get all voices for a specific gender."""
        return [v for v in self.voices if v.gender == gender]

    def get_voice_by_id(self, voice_id: str) -> Optional[Voice]:
        """Get a specific voice by ID."""
        for v in self.voices:
            if v.voice_id == voice_id:
                return v
        return None

    def list_voice_ids(self) -> List[str]:
        """Get list of all voice IDs."""
        return [v.voice_id for v in self.voices]

    def to_dict(self) -> dict:
        """Return raw response data as dictionary."""
        return {
            "status_code": self.status_code,
            "message": self.message,
            "error": self.error,
            "data": self._raw_data,
        }

    def __repr__(self) -> str:
        return f"VoiceResponse(voices={len(self.voices)})"


class TTSResponse:
    """Response object for TTS requests."""

    def __init__(self, content: bytes, headers: dict, request_id: str):
        self.content = content
        self.headers = headers
        self.request_id = request_id
        self.sample_rate = int(headers.get("x-sample-rate", 24000))
        self.channels = int(headers.get("x-channels", 1))
        self.bit_depth = int(headers.get("x-bit-depth", 16))
        self.format = headers.get("x-format", "wav")

    def save(self, filepath: Union[str, Path]) -> None:
        """Save audio to file."""
        with open(filepath, "wb") as f:
            f.write(self.content)

    def stream_to_file(self, filepath: Union[str, Path]) -> None:
        """Alias for save() for consistency."""
        self.save(filepath)

    def get_audio_data(self) -> bytes:
        """Get raw audio bytes."""
        return self.content

    def to_file_object(self) -> BinaryIO:
        """Return audio as a file-like object."""
        return io.BytesIO(self.content)


class TTSStreamResponse:
    """Streaming response object for TTS requests."""

    def __init__(self, response, headers: dict, request_id: str):
        self._response = response
        self.headers = headers
        self.request_id = request_id
        self.sample_rate = int(headers.get("x-sample-rate", 24000))
        self.channels = int(headers.get("x-channels", 1))
        self.bit_depth = int(headers.get("x-bit-depth", 16))
        self.format = headers.get("x-format", "wav")

    def iter_bytes(self, chunk_size: int = 8192) -> Iterator[bytes]:
        """Iterate over audio bytes as they arrive."""
        for chunk in self._response.iter_content(chunk_size=chunk_size):
            if chunk:
                yield chunk

    def save(self, filepath: Union[str, Path], chunk_size: int = 8192) -> None:
        """Save streamed audio to file."""
        with open(filepath, "wb") as f:
            for chunk in self.iter_bytes(chunk_size=chunk_size):
                f.write(chunk)

    def to_file_object(self, chunk_size: int = 8192) -> BinaryIO:
        """Convert stream to file-like object by reading all chunks."""
        buffer = io.BytesIO()
        for chunk in self.iter_bytes(chunk_size=chunk_size):
            buffer.write(chunk)
        buffer.seek(0)
        return buffer


class AsyncTTSStreamResponse:
    """Async streaming response object for TTS requests."""

    def __init__(self, response: aiohttp.ClientResponse, headers: dict, request_id: str):
        self._response = response
        self.headers = headers
        self.request_id = request_id
        self.sample_rate = int(headers.get("x-sample-rate", 24000))
        self.channels = int(headers.get("x-channels", 1))
        self.bit_depth = int(headers.get("x-bit-depth", 16))
        self.format = headers.get("x-format", "wav")

    async def iter_bytes(self, chunk_size: int = 8192) -> AsyncIterator[bytes]:
        """Async iterate over audio bytes as they arrive."""
        async for chunk in self._response.content.iter_chunked(chunk_size):
            if chunk:
                yield chunk

    async def save(self, filepath: Union[str, Path], chunk_size: int = 8192) -> None:
        """Save streamed audio to file asynchronously."""
        with open(filepath, "wb") as f:
            async for chunk in self.iter_bytes(chunk_size=chunk_size):
                f.write(chunk)

    async def to_file_object(self, chunk_size: int = 8192) -> BinaryIO:
        """Convert stream to file-like object by reading all chunks."""
        buffer = io.BytesIO()
        async for chunk in self.iter_bytes(chunk_size=chunk_size):
            buffer.write(chunk)
        buffer.seek(0)
        return buffer


class STTResponse:
    """Response object for STT requests."""

    def __init__(self, data: dict):
        self.request_id = data.get("request_id")
        self.text = data.get("text")
        self.language_detected = data.get("language_detected")
        self.audio_duration_seconds = data.get("audio_duration_seconds")
        self.processing_time_seconds = data.get("processing_time_seconds")
        self.first_token_time_seconds = data.get("first_token_time_seconds")
        self.credits_used = data.get("credits_used")
        self._raw_data = data

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return f"STTResponse(text='{self.text[:50]}...', language='{self.language_detected}')"

    def to_dict(self) -> dict:
        """Return raw response data as dictionary."""
        return self._raw_data


class Voices:
    """Voice management interface."""

    def __init__(self, api_key: str, voices_base_url: str = "https://api.indusai.app"):
        self.api_key = api_key
        self.voices_base_url = voices_base_url.rstrip("/")
        self._session: Optional[aiohttp.ClientSession] = None

    def list(self) -> VoiceResponse:
        """
        Get all available voices (synchronous).

        Returns:
            VoiceResponse object containing all available voices

        Example:
            >>> voices = client.voices.list()
            >>> for voice in voices.voices:
            ...     print(f"{voice.name} ({voice.voice_id}) - {voice.language}")
            >>>
            >>> # Get voice IDs for a specific language
            >>> hindi_voices = voices.get_voices_by_language("hindi")
        """
        url = f"{self.voices_base_url}/api/voice/get-voices"

        response = requests.post(url, headers={"accept": "application/json"})
        response.raise_for_status()

        return VoiceResponse(response.json())

    async def list_async(self) -> VoiceResponse:
        """
        Get all available voices (asynchronous).

        Returns:
            VoiceResponse object containing all available voices

        Example:
            >>> voices = await client.voices.list_async()
            >>> for voice in voices.voices:
            ...     print(f"{voice.name} ({voice.voice_id}) - {voice.language}")
        """
        url = f"{self.voices_base_url}/api/voice/get-voices"

        if self._session is None:
            self._session = aiohttp.ClientSession()

        async with self._session.post(url, headers={"accept": "application/json"}) as response:
            response.raise_for_status()
            data = await response.json()
            return VoiceResponse(data)

    async def close(self):
        """Close async session."""
        if self._session:
            await self._session.close()
            self._session = None


class TTS:
    """Text-to-Speech interface."""

    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self._session: Optional[aiohttp.ClientSession] = None

    def speak(
        self,
        text: str,
        voice: str = "Indus-hi-Urvashi",
        language: Optional[str] = None,
        output_format: str = "wav",
        stream: bool = False,
        model: str = "orpheus-3b",
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Union[TTSResponse, TTSStreamResponse]:
        """
        Synchronous text-to-speech conversion.

        Args:
            text: Text to convert to speech
            voice: Voice to use (default: "Indus-hi-Urvashi")
            language: Language code (optional, e.g., "hi-IN")
            output_format: Audio format - "wav", "mp3", or "pcm" (default: "wav")
            stream: Enable streaming response (default: False)
            model: TTS model to use (default: "orpheus-3b")
            temperature: Sampling temperature (optional)
            max_tokens: Maximum tokens to generate (optional)

        Returns:
            TTSResponse or TTSStreamResponse object
        """
        if output_format not in ["wav", "mp3", "pcm"]:
            raise ValueError("output_format must be 'wav', 'mp3', or 'pcm'")

        url = f"{self.base_url}/v1/audio/speech"

        payload = {
            "text": text,
            "voice": voice,
            "output_format": output_format,
            "stream": stream,
            "model": model,
            "api_key": self.api_key,
            "normalize": True,
            "read_urls_as": "verbatim",
        }

        if language:
            payload["language"] = language
        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        response = requests.post(url, json=payload, stream=stream)
        response.raise_for_status()

        request_id = response.headers.get("x-request-id", "")

        if stream:
            return TTSStreamResponse(response, dict(response.headers), request_id)
        else:
            return TTSResponse(response.content, dict(response.headers), request_id)

    async def speak_async(
        self,
        text: str,
        voice: str = "Indus-hi-Urvashi",
        language: Optional[str] = None,
        output_format: str = "wav",
        stream: bool = False,
        model: str = "orpheus-3b",
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Union[TTSResponse, AsyncTTSStreamResponse]:
        """
        Asynchronous text-to-speech conversion.

        Args:
            text: Text to convert to speech
            voice: Voice to use (default: "Indus-hi-Urvashi")
            language: Language code (optional, e.g., "hi-IN")
            output_format: Audio format - "wav", "mp3", or "pcm" (default: "wav")
            stream: Enable streaming response (default: False)
            model: TTS model to use (default: "orpheus-3b")
            temperature: Sampling temperature (optional)
            max_tokens: Maximum tokens to generate (optional)

        Returns:
            TTSResponse or AsyncTTSStreamResponse object
        """
        if output_format not in ["wav", "mp3", "pcm"]:
            raise ValueError("output_format must be 'wav', 'mp3', or 'pcm'")

        url = f"{self.base_url}/v1/audio/speech"

        payload = {
            "text": text,
            "voice": voice,
            "output_format": output_format,
            "stream": stream,
            "model": model,
            "api_key": self.api_key,
            "normalize": True,
            "read_urls_as": "verbatim",
        }

        if language:
            payload["language"] = language
        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        if self._session is None:
            self._session = aiohttp.ClientSession()

        async with self._session.post(url, json=payload) as response:
            response.raise_for_status()
            request_id = response.headers.get("x-request-id", "")

            if stream:
                return AsyncTTSStreamResponse(response, dict(response.headers), request_id)
            else:
                content = await response.read()
                return TTSResponse(content, dict(response.headers), request_id)

    async def close(self):
        """Close async session."""
        if self._session:
            await self._session.close()
            self._session = None


class STT:
    """Speech-to-Text interface."""

    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self._session: Optional[aiohttp.ClientSession] = None

    def transcribe(
        self,
        file: Union[str, Path, BinaryIO],
        language: Optional[str] = None,
        chunk_length_s: float = 6,
        stride_s: float = 5.9,
        overlap_words: int = 7,
    ) -> STTResponse:
        """
        Synchronous speech-to-text transcription.

        Args:
            file: Audio file path or file-like object
            language: Language code (e.g., "hi", "en")
            chunk_length_s: Chunk length in seconds (default: 6)
            stride_s: Stride length in seconds (default: 5.9)
            overlap_words: Number of overlapping words (default: 7)

        Returns:
            STTResponse object
        """
        url = f"{self.base_url}/v1/audio/transcribe/file"

        # Prepare file
        if isinstance(file, (str, Path)):
            file_path = Path(file)
            files = {"file": (file_path.name, open(file_path, "rb"), "audio/wav")}
            should_close = True
        else:
            # File-like object
            filename = getattr(file, "name", "audio.wav")
            files = {"file": (filename, file, "audio/wav")}
            should_close = False

        data = {
            "api_key": self.api_key,
            "chunk_length_s": chunk_length_s,
            "stride_s": stride_s,
            "overlap_words": overlap_words,
        }

        if language:
            data["language"] = language

        try:
            response = requests.post(url, files=files, data=data)
            response.raise_for_status()
            return STTResponse(response.json())
        finally:
            if should_close:
                files["file"][1].close()

    async def transcribe_async(
        self,
        file: Union[str, Path, BinaryIO],
        language: Optional[str] = None,
        chunk_length_s: float = 6,
        stride_s: float = 5.9,
        overlap_words: int = 7,
    ) -> STTResponse:
        """
        Asynchronous speech-to-text transcription.

        Args:
            file: Audio file path or file-like object
            language: Language code (e.g., "hi", "en")
            chunk_length_s: Chunk length in seconds (default: 6)
            stride_s: Stride length in seconds (default: 5.9)
            overlap_words: Number of overlapping words (default: 7)

        Returns:
            STTResponse object
        """
        url = f"{self.base_url}/v1/audio/transcribe/file"

        # Prepare file
        if isinstance(file, (str, Path)):
            file_path = Path(file)
            with open(file_path, "rb") as f:
                file_data = f.read()
            filename = file_path.name
        else:
            file_data = file.read()
            filename = getattr(file, "name", "audio.wav")

        data = aiohttp.FormData()
        data.add_field("file", file_data, filename=filename, content_type="audio/wav")
        data.add_field("api_key", self.api_key)
        data.add_field("chunk_length_s", str(chunk_length_s))
        data.add_field("stride_s", str(stride_s))
        data.add_field("overlap_words", str(overlap_words))

        if language:
            data.add_field("language", language)

        if self._session is None:
            self._session = aiohttp.ClientSession()

        async with self._session.post(url, data=data) as response:
            response.raise_for_status()
            result = await response.json()
            return STTResponse(result)

    async def close(self):
        """Close async session."""
        if self._session:
            await self._session.close()
            self._session = None


class Client:
    """
    Main client for IndusLabs Voice API.

    Example:
        >>> from induslabs import Client
        >>> client = Client(api_key="your_api_key")
        >>>
        >>> # List available voices
        >>> voices_response = client.voices.list()
        >>> for voice in voices_response.voices:
        ...     print(f"{voice.name}: {voice.voice_id}")
        >>>
        >>> # Text-to-Speech
        >>> response = client.tts.speak(
        ...     text="Hello world",
        ...     voice="Indus-hi-Indus-hi-Urvashi",
        ...     language="hi-IN"
        ... )
        >>> response.save("output.wav")
        >>>
        >>> # Speech-to-Text
        >>> result = client.stt.transcribe("audio.wav", language="hi")
        >>> print(result.text)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://voice.induslabs.io",
        voices_base_url: str = "https://api.indusai.app",
    ):
        """
        Initialize IndusLabs client.

        Args:
            api_key: API key (can also be set via INDUSLABS_API_KEY env variable)
            base_url: Base URL for TTS/STT API (default: https://voice.induslabs.io)
            voices_base_url: Base URL for voices API (default: https://api.indusai.app)
        """
        self.api_key = api_key or os.environ.get("INDUSLABS_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key must be provided either as argument or via "
                "INDUSLABS_API_KEY environment variable"
            )

        self.base_url = base_url.rstrip("/")
        self.voices_base_url = voices_base_url.rstrip("/")

        self.tts = TTS(self.api_key, self.base_url)
        self.stt = STT(self.api_key, self.base_url)
        self.voices = Voices(self.api_key, self.voices_base_url)

    async def close(self):
        """Close all async sessions."""
        await self.tts.close()
        await self.stt.close()
        await self.voices.close()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
