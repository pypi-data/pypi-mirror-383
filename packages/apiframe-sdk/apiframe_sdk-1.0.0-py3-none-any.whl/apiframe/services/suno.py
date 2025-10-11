"""
Suno Service - Suno AI music generation
"""

from typing import TYPE_CHECKING

from ..types import (
    SunoExtendParams,
    SunoGenerateParams,
    SunoLyricsParams,
    SunoUploadParams,
    TaskResponse,
)

if TYPE_CHECKING:
    from ..http_client import HttpClient


class Suno:
    """Service for Suno AI music generation"""

    def __init__(self, http_client: "HttpClient") -> None:
        """
        Initialize Suno service

        Args:
            http_client: HTTP client instance
        """
        self.http_client = http_client

    def generate(self, params: SunoGenerateParams) -> TaskResponse:
        """
        Generate a song with a lyrics video clip
        This endpoint generates TWO songs with the same lyrics

        Args:
            params: Parameters for music generation

        Returns:
            Task response with task ID

        Example:
            >>> task = client.suno.generate({
            ...     'prompt': 'an upbeat electronic track',
            ...     'lyrics': 'Verse 1: Dancing through the night...',
            ...     'tags': 'electronic, dance, upbeat'
            ... })
        """
        return self.http_client.post("/suno-imagine", params)  # type: ignore

    def upload(self, params: SunoUploadParams) -> TaskResponse:
        """
        Upload an audio file and turn it into an extendable song

        Args:
            params: Parameters including audio_url

        Returns:
            Task response with task ID and song_id

        Example:
            >>> task = client.suno.upload({
            ...     'audio_url': 'https://your-audio-url.mp3'
            ... })
        """
        return self.http_client.post("/suno-upload", params)  # type: ignore

    def extend(self, params: SunoExtendParams) -> TaskResponse:
        """
        Extend a previously generated song or an uploaded audio

        Args:
            params: Parameters including parent_task_id or song_id and continue_at timestamp

        Returns:
            Task response with task ID

        Example:
            >>> task = client.suno.extend({
            ...     'song_id': 'upload_result_song_id',
            ...     'continue_at': 30,
            ...     'from_upload': True,
            ...     'prompt': 'continue with more energy'
            ... })
        """
        return self.http_client.post("/suno-extend", params)  # type: ignore

    def generate_lyrics(self, params: SunoLyricsParams) -> TaskResponse:
        """
        Generate song lyrics based on a prompt

        Args:
            params: Parameters including prompt

        Returns:
            Task response with generated lyrics

        Example:
            >>> task = client.suno.generate_lyrics({
            ...     'prompt': 'a song about summer adventures'
            ... })
        """
        return self.http_client.post("/suno-lyrics", params)  # type: ignore

