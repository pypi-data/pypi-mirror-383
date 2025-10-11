"""
Runway Service - Runway ML video generation
"""

from typing import TYPE_CHECKING, Any, Dict, Optional

from ..types import RunwayGenerateParams, TaskResponse

if TYPE_CHECKING:
    from ..http_client import HttpClient


class Runway:
    """Service for Runway ML video generation"""

    def __init__(self, http_client: "HttpClient") -> None:
        """
        Initialize Runway service

        Args:
            http_client: HTTP client instance
        """
        self.http_client = http_client

    def generate(self, params: RunwayGenerateParams) -> TaskResponse:
        """
        Generate video (text2video, image2video, or video2video)

        Args:
            params: Parameters for video generation

        Returns:
            Task response with task ID

        Example:
            >>> task = client.runway.generate({
            ...     'prompt': 'a drone shot flying over mountains',
            ...     'generation_type': 'text2video',
            ...     'model': 'gen3',
            ...     'aspect_ratio': '16:9'
            ... })
        """
        return self.http_client.post("/runway-imagine", params)  # type: ignore

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
            >>> task = client.runway.text_to_video(
            ...     'a drone shot flying over mountains',
            ...     {'model': 'gen3a_turbo', 'duration': 5}
            ... )
        """
        params: RunwayGenerateParams = {
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
            >>> task = client.runway.image_to_video(
            ...     'https://image-url.jpg',
            ...     'add cinematic motion to this scene',
            ...     {'duration': 10}
            ... )
        """
        params: RunwayGenerateParams = {
            "prompt": prompt,
            "generation_type": "image2video",
            "image_url": image_url,
            **(options or {}),  # type: ignore
        }
        return self.generate(params)

    def video_to_video(
        self, video_url: str, prompt: str, options: Optional[Dict[str, Any]] = None
    ) -> TaskResponse:
        """
        Convenience method: Video to video

        Args:
            video_url: URL of the video to transform
            prompt: Text prompt for video transformation
            options: Optional additional parameters

        Returns:
            Task response with task ID

        Example:
            >>> task = client.runway.video_to_video(
            ...     'https://video-url.mp4',
            ...     'transform with sunset atmosphere',
            ...     {'model': 'gen3', 'duration': 5}
            ... )
        """
        params: RunwayGenerateParams = {
            "prompt": prompt,
            "generation_type": "video2video",
            "video_url": video_url,
            **(options or {}),  # type: ignore
        }
        return self.generate(params)

