"""
Main Apiframe SDK Client
"""

from typing import Optional

from .http_client import HttpClient
from .services import (
    AIPhotos,
    Flux,
    Ideogram,
    Kling,
    Luma,
    Media,
    Midjourney,
    MidjourneyAlt,
    Runway,
    Suno,
    Tasks,
    Udio,
)


class Apiframe:
    """
    Main Apiframe SDK client

    Example:
        >>> from apiframe import Apiframe
        >>>
        >>> client = Apiframe(api_key='your_api_key_here')
        >>>
        >>> # Create an image generation task
        >>> task = client.midjourney.imagine({
        ...     'prompt': 'a beautiful sunset',
        ...     'aspect_ratio': '16:9'
        ... })
        >>>
        >>> # Wait for completion with progress updates
        >>> result = client.tasks.wait_for(
        ...     task['id'],
        ...     on_progress=lambda p: print(f'Progress: {p}%')
        ... )
        >>>
        >>> print(result['image_urls'])  # imagine returns 4 images
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.apiframe.ai",
        timeout: int = 300,
    ) -> None:
        """
        Create a new Apiframe client

        Args:
            api_key: Your Apiframe API key (required)
            base_url: Custom API endpoint (optional, default: https://api.apiframe.ai)
            timeout: Request timeout in seconds (optional, default: 300 = 5 minutes)

        Example:
            >>> client = Apiframe(
            ...     api_key='your_api_key',
            ...     base_url='https://api.apiframe.ai',  # optional
            ...     timeout=300  # optional
            ... )
        """
        self._http_client = HttpClient(api_key=api_key, base_url=base_url, timeout=timeout)

        # Initialize all service modules
        self.tasks = Tasks(self._http_client)
        self.midjourney = Midjourney(self._http_client)
        self.midjourney_alt = MidjourneyAlt(self._http_client)
        self.flux = Flux(self._http_client)
        self.ideogram = Ideogram(self._http_client)
        self.luma = Luma(self._http_client)
        self.suno = Suno(self._http_client)
        self.udio = Udio(self._http_client)
        self.runway = Runway(self._http_client)
        self.kling = Kling(self._http_client)
        self.ai_photos = AIPhotos(self._http_client)
        self.media = Media(self._http_client)

    def close(self) -> None:
        """
        Close the HTTP client session

        Example:
            >>> client.close()
        """
        self._http_client.close()

    def __enter__(self) -> "Apiframe":
        """Context manager entry"""
        return self

    def __exit__(self, *args: object) -> None:
        """Context manager exit"""
        self.close()

