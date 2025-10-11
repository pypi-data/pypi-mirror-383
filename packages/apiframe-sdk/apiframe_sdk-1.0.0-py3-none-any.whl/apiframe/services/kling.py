"""
Kling Service - Kling AI video generation
"""

from typing import TYPE_CHECKING, Any, Dict, Optional

from ..types import KlingGenerateParams, KlingTryonParams, TaskResponse

if TYPE_CHECKING:
    from ..http_client import HttpClient


class Kling:
    """Service for Kling AI video generation"""

    def __init__(self, http_client: "HttpClient") -> None:
        """
        Initialize Kling service

        Args:
            http_client: HTTP client instance
        """
        self.http_client = http_client

    def generate(self, params: KlingGenerateParams) -> TaskResponse:
        """
        Generate video (text2video or image2video)

        Args:
            params: Parameters for video generation

        Returns:
            Task response with task ID

        Example:
            >>> task = client.kling.generate({
            ...     'prompt': 'a time-lapse of a flower blooming',
            ...     'generation_type': 'text2video',
            ...     'model': 'kling-v1-5',
            ...     'mode': 'pro'
            ... })
        """
        return self.http_client.post("/kling-imagine", params)  # type: ignore

    def text_to_video(
        self, prompt: str, options: Optional[Dict[str, Any]] = None
    ) -> TaskResponse:
        """
        Convenience method: Text to video

        Args:
            prompt: Text prompt for video generation
            options: Optional additional parameters

        Returns:
            Task response with task ID

        Example:
            >>> task = client.kling.text_to_video(
            ...     'a time-lapse of a flower blooming',
            ...     {'duration': 10, 'aspect_ratio': '16:9'}
            ... )
        """
        params: KlingGenerateParams = {
            "prompt": prompt,
            "generation_type": "text2video",
            **(options or {}),  # type: ignore
        }
        return self.generate(params)

    def image_to_video(
        self, image_url: str, prompt: str, options: Optional[Dict[str, Any]] = None
    ) -> TaskResponse:
        """
        Convenience method: Image to video

        Args:
            image_url: URL of the image to animate
            prompt: Text prompt for video generation
            options: Optional additional parameters

        Returns:
            Task response with task ID

        Example:
            >>> task = client.kling.image_to_video(
            ...     'https://image-url.jpg',
            ...     'animate this image with smooth motion',
            ...     {'mode': 'pro', 'duration': 5}
            ... )
        """
        params: KlingGenerateParams = {
            "prompt": prompt,
            "generation_type": "image2video",
            "image_url": image_url,
            **(options or {}),  # type: ignore
        }
        return self.generate(params)

    def tryon(self, params: KlingTryonParams) -> TaskResponse:
        """
        Virtual Try On

        Args:
            params: Parameters including human_image_url and cloth_image_url

        Returns:
            Task response with task ID

        Example:
            >>> task = client.kling.tryon({
            ...     'human_image_url': 'https://person-image.jpg',
            ...     'cloth_image_url': 'https://clothing-image.jpg'
            ... })
        """
        return self.http_client.post("/kling-tryon", params)  # type: ignore

