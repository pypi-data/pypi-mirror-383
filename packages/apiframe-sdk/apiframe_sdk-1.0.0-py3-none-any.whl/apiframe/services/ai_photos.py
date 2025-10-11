"""
AI Photos Service - AI Photos generation and training
"""

from typing import TYPE_CHECKING

from ..types import (
    AIPhotosGenerateParams,
    AIPhotosTrainParams,
    AIPhotosUploadParams,
    TaskResponse,
)

if TYPE_CHECKING:
    from ..http_client import HttpClient


class AIPhotos:
    """Service for AI Photos generation and training"""

    def __init__(self, http_client: "HttpClient") -> None:
        """
        Initialize AIPhotos service

        Args:
            http_client: HTTP client instance
        """
        self.http_client = http_client

    def upload(self, params: AIPhotosUploadParams) -> TaskResponse:
        """
        Upload and prepare 10-30 images for training

        Args:
            params: Parameters including images array and subject details

        Returns:
            Task response with task ID

        Example:
            >>> task = client.ai_photos.upload({
            ...     'images': ['base64_image_1', 'base64_image_2', '...'],  # 10-30 images
            ...     'ethnicity': 'white',
            ...     'gender': 'male',
            ...     'age': 30
            ... })
        """
        return self.http_client.post("/ai-photos/upload", params)  # type: ignore

    def train(self, params: AIPhotosTrainParams) -> TaskResponse:
        """
        Train AI on the subject

        Args:
            params: Parameters including training_images_id and trigger_word

        Returns:
            Task response with task ID

        Example:
            >>> task = client.ai_photos.train({
            ...     'training_images_id': upload_task_id,
            ...     'trigger_word': 'TOKMSN'
            ... })
        """
        return self.http_client.post("/ai-photos/train", params)  # type: ignore

    def generate(self, params: AIPhotosGenerateParams) -> TaskResponse:
        """
        Generate photos using the trained model

        Args:
            params: Parameters including training_id and prompt

        Returns:
            Task response with task ID

        Example:
            >>> task = client.ai_photos.generate({
            ...     'training_id': train_task_id,
            ...     'prompt': 'a realistic portrait of TOKMSN black man wearing a suit',
            ...     'aspect_ratio': '1:1',
            ...     'number_of_images': '4'
            ... })
        """
        return self.http_client.post("/ai-photos/generate", params)  # type: ignore

