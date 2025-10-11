"""
Udio Service - Udio AI music generation
"""

from typing import TYPE_CHECKING

from ..types import TaskResponse, UdioGenerateParams

if TYPE_CHECKING:
    from ..http_client import HttpClient


class Udio:
    """Service for Udio AI music generation"""

    def __init__(self, http_client: "HttpClient") -> None:
        """
        Initialize Udio service

        Args:
            http_client: HTTP client instance
        """
        self.http_client = http_client

    def generate(self, params: UdioGenerateParams) -> TaskResponse:
        """
        Generate music (creates TWO songs with lyrics)

        Args:
            params: Parameters for music generation

        Returns:
            Task response with task ID

        Example:
            >>> task = client.udio.generate({
            ...     'prompt': 'a calm ambient soundtrack',
            ...     'lyrics': 'Verse 1: Under the stars...',
            ...     'tags': 'ambient, calm, instrumental'
            ... })
        """
        return self.http_client.post("/udio-imagine", params)  # type: ignore

