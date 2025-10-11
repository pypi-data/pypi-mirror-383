"""
Ideogram Service - Ideogram image generation
"""

from typing import TYPE_CHECKING

from ..types import (
    IdeogramDescribeParams,
    IdeogramGenerateParams,
    IdeogramRemixParams,
    IdeogramUpscaleParams,
    TaskResponse,
)

if TYPE_CHECKING:
    from ..http_client import HttpClient


class Ideogram:
    """Service for Ideogram image generation"""

    def __init__(self, http_client: "HttpClient") -> None:
        """
        Initialize Ideogram service

        Args:
            http_client: HTTP client instance
        """
        self.http_client = http_client

    def generate(self, params: IdeogramGenerateParams) -> TaskResponse:
        """
        Generate image

        Args:
            params: Parameters for image generation

        Returns:
            Task response with task ID

        Example:
            >>> task = client.ideogram.generate({
            ...     'prompt': 'a logo design',
            ...     'aspect_ratio': 'ASPECT_1_1',
            ...     'style_type': 'DESIGN'
            ... })
        """
        return self.http_client.post("/ideogram-imagine", params)  # type: ignore

    def upscale(self, params: IdeogramUpscaleParams) -> TaskResponse:
        """
        Upscale image

        Args:
            params: Parameters for image upscaling

        Returns:
            Task response with task ID

        Example:
            >>> task = client.ideogram.upscale({
            ...     'image_url': 'https://...',
            ...     'prompt': 'enhance this image',
            ...     'resemblance': 80
            ... })
        """
        return self.http_client.post("/ideogram-upscale", params)  # type: ignore

    def describe(self, params: IdeogramDescribeParams) -> TaskResponse:
        """
        Describe image

        Args:
            params: Parameters including image_url

        Returns:
            Task response with task ID

        Example:
            >>> task = client.ideogram.describe({
            ...     'image_url': 'https://...'
            ... })
        """
        return self.http_client.post("/ideogram-describe", params)  # type: ignore

    def remix(self, params: IdeogramRemixParams) -> TaskResponse:
        """
        Remix (image-to-image)

        Args:
            params: Parameters for image remixing

        Returns:
            Task response with task ID

        Example:
            >>> task = client.ideogram.remix({
            ...     'image_url': 'https://...',
            ...     'prompt': 'transform this image...',
            ...     'image_weight': 70
            ... })
        """
        return self.http_client.post("/ideogram-remix", params)  # type: ignore

