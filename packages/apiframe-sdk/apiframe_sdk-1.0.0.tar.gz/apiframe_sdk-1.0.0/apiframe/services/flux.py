"""
Flux Service - Flux AI image generation
"""

from typing import TYPE_CHECKING, Any, Dict

from ..types import FluxGenerateParams, TaskResponse

if TYPE_CHECKING:
    from ..http_client import HttpClient


class Flux:
    """Service for Flux AI image generation"""

    def __init__(self, http_client: "HttpClient") -> None:
        """
        Initialize Flux service

        Args:
            http_client: HTTP client instance
        """
        self.http_client = http_client

    def generate(self, params: FluxGenerateParams) -> TaskResponse:
        """
        Generate images using Flux AI

        Args:
            params: Parameters for image generation including model selection

        Returns:
            Task response with task ID

        Example:
            >>> task = client.flux.generate({
            ...     'model': 'flux-pro',
            ...     'prompt': 'a futuristic cityscape',
            ...     'width': 1024,
            ...     'height': 1024
            ... })
        """
        return self.http_client.post("/flux-imagine", params)  # type: ignore

    def generate_pro(self, params: Dict[str, Any]) -> TaskResponse:
        """
        Generate images using Flux Pro
        Convenience method that sets model to 'flux-pro'

        Args:
            params: Parameters for image generation (model will be set to 'flux-pro')

        Returns:
            Task response with task ID

        Example:
            >>> task = client.flux.generate_pro({
            ...     'prompt': 'a futuristic cityscape',
            ...     'width': 1024,
            ...     'height': 1024
            ... })
        """
        full_params = {**params, "model": params.get("model", "flux-pro")}
        return self.generate(full_params)  # type: ignore

    def generate_dev(self, params: Dict[str, Any]) -> TaskResponse:
        """
        Generate images using Flux Dev
        Convenience method that sets model to 'flux-dev'

        Args:
            params: Parameters for image generation (model will be set to 'flux-dev')

        Returns:
            Task response with task ID

        Example:
            >>> task = client.flux.generate_dev({
            ...     'prompt': 'a landscape',
            ...     'aspect_ratio': '16:9'
            ... })
        """
        full_params = {**params, "model": params.get("model", "flux-dev")}
        return self.generate(full_params)  # type: ignore

    def generate_schnell(self, params: Dict[str, Any]) -> TaskResponse:
        """
        Generate images using Flux Schnell (fast mode)
        Convenience method that sets model to 'flux-schnell'

        Args:
            params: Parameters for image generation (model will be set to 'flux-schnell')

        Returns:
            Task response with task ID

        Example:
            >>> task = client.flux.generate_schnell({
            ...     'prompt': 'quick sketch',
            ...     'width': 512,
            ...     'height': 512
            ... })
        """
        full_params = {**params, "model": params.get("model", "flux-schnell")}
        return self.generate(full_params)  # type: ignore

