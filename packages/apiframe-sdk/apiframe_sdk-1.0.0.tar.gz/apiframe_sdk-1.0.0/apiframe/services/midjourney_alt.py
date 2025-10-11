"""
Midjourney Alt Service - Pro Midjourney API
"""

from typing import TYPE_CHECKING

from ..types import (
    MidjourneyAltImagineParams,
    MidjourneyAltPanParams,
    MidjourneyAltUpscaleParams,
    MidjourneyAltVariationsParams,
    MidjourneyAltVaryParams,
    MidjourneyAltZoomParams,
    TaskResponse,
)

if TYPE_CHECKING:
    from ..http_client import HttpClient


class MidjourneyAlt:
    """
    Midjourney Pro API - Fast & Turbo modes for better performance

    See: https://docs.apiframe.ai/pro-midjourney-api/api-endpoints
    """

    def __init__(self, http_client: "HttpClient") -> None:
        """
        Initialize MidjourneyAlt service

        Args:
            http_client: HTTP client instance
        """
        self.http_client = http_client

    def imagine(self, params: MidjourneyAltImagineParams) -> TaskResponse:
        """
        Create a new image with Pro API (supports Fast and Turbo modes)

        Args:
            params: Parameters for the imagine request

        Returns:
            Task response with task ID

        Example:
            >>> task = client.midjourney_alt.imagine({
            ...     'prompt': 'a serene mountain landscape',
            ...     'mode': 'turbo'  # 'fast' or 'turbo'
            ... })
        """
        return self.http_client.post("/pro/midjourney/imagine", params)  # type: ignore

    def upscale(self, params: MidjourneyAltUpscaleParams) -> TaskResponse:
        """
        Upscale a specific image from a Pro API generation

        Args:
            params: Parameters including parent_task_id, index, and type

        Returns:
            Task response with task ID

        Example:
            >>> task = client.midjourney_alt.upscale({
            ...     'parent_task_id': 'parent_task_id',
            ...     'index': '1',
            ...     'type': 'subtle'
            ... })
        """
        return self.http_client.post("/pro/midjourney/upscale", params)  # type: ignore

    def vary(self, params: MidjourneyAltVaryParams) -> TaskResponse:
        """
        Create variations with strong/subtle control

        Args:
            params: Parameters including parent_task_id, index, and type

        Returns:
            Task response with task ID

        Example:
            >>> task = client.midjourney_alt.vary({
            ...     'parent_task_id': 'parent_task_id',
            ...     'index': '1',
            ...     'type': 'subtle'
            ... })
        """
        return self.http_client.post("/pro/midjourney/vary", params)  # type: ignore

    def variations(self, params: MidjourneyAltVariationsParams) -> TaskResponse:
        """
        Generate 4 variations of an image

        Args:
            params: Parameters including parent_task_id and index

        Returns:
            Task response with task ID

        Example:
            >>> task = client.midjourney_alt.variations({
            ...     'parent_task_id': 'parent_task_id',
            ...     'index': '1'
            ... })
        """
        return self.http_client.post("/pro/midjourney/variations", params)  # type: ignore

    def pan(self, params: MidjourneyAltPanParams) -> TaskResponse:
        """
        Pan in a specific direction

        Args:
            params: Parameters including parent_task_id, index, and type

        Returns:
            Task response with task ID

        Example:
            >>> task = client.midjourney_alt.pan({
            ...     'parent_task_id': 'parent_task_id',
            ...     'index': '1',
            ...     'type': 'up'
            ... })
        """
        return self.http_client.post("/pro/midjourney/pan", params)  # type: ignore

    def zoom(self, params: MidjourneyAltZoomParams) -> TaskResponse:
        """
        Zoom out from an image

        Args:
            params: Parameters including parent_task_id, index, and type

        Returns:
            Task response with task ID

        Example:
            >>> task = client.midjourney_alt.zoom({
            ...     'parent_task_id': 'parent_task_id',
            ...     'index': '1',
            ...     'type': '2'  # '1.5', '2', '{1, 2}', '1'
            ... })
        """
        return self.http_client.post("/pro/midjourney/zoom", params)  # type: ignore

    def get_generation(self, generation_id: str) -> TaskResponse:
        """
        Get generation info

        Args:
            generation_id: The generation ID

        Returns:
            Task response with generation details
        """
        return self.http_client.get(f"/pro/midjourney/generation/{generation_id}")  # type: ignore

    def get_account_info(self) -> dict:
        """
        Get Pro API account info

        Returns:
            Account information
        """
        return self.http_client.get("/pro/midjourney/account")  # type: ignore

