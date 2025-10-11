"""
Luma Service - Luma AI video generation
"""

from typing import TYPE_CHECKING

from ..types import LumaExtendParams, LumaGenerateParams, TaskResponse

if TYPE_CHECKING:
    from ..http_client import HttpClient


class Luma:
    """Service for Luma AI video generation"""

    def __init__(self, http_client: "HttpClient") -> None:
        """
        Initialize Luma service

        Args:
            http_client: HTTP client instance
        """
        self.http_client = http_client

    def generate(self, params: LumaGenerateParams) -> TaskResponse:
        """
        Generate a video based on a prompt and/or an image input

        Args:
            params: Parameters for video generation

        Returns:
            Task response with task ID

        Example:
            >>> task = client.luma.generate({
            ...     'prompt': 'a serene beach with waves',
            ...     'aspect_ratio': '16:9',
            ...     'enhance_prompt': True
            ... })
        """
        return self.http_client.post("/luma-imagine", params)  # type: ignore

    def extend(self, params: LumaExtendParams) -> TaskResponse:
        """
        Extend a previously generated video based on a prompt and/or an image input

        Args:
            params: Parameters including parent_task_id and prompt

        Returns:
            Task response with task ID

        Example:
            >>> task = client.luma.extend({
            ...     'parent_task_id': 'previous_task_id',
            ...     'prompt': 'continue the scene with more action'
            ... })
        """
        return self.http_client.post("/luma-extend", params)  # type: ignore

