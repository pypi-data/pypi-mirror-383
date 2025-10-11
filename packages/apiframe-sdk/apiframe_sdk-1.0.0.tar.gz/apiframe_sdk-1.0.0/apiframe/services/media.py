"""
Media Service - Media upload operations
"""

import os
from typing import TYPE_CHECKING, Optional, Union

from ..types import MediaUploadAudioResponse, MediaUploadResponse

if TYPE_CHECKING:
    from ..http_client import HttpClient


class Media:
    """Service for media upload operations"""

    def __init__(self, http_client: "HttpClient") -> None:
        """
        Initialize Media service

        Args:
            http_client: HTTP client instance
        """
        self.http_client = http_client

    def upload(
        self, file: Optional[Union[str, bytes]] = None, filename: Optional[str] = None
    ) -> MediaUploadResponse:
        """
        Upload an image file (max 2MB)

        Args:
            file: File path (str) or file bytes
            filename: Filename for the upload (used if file is bytes)

        Returns:
            Upload response with imageURL

        Example:
            >>> # Upload from file path
            >>> upload = client.media.upload(file='./path/to/image.jpg')
            >>> print(upload['imageURL'])
            >>>
            >>> # Upload from bytes
            >>> with open('./path/to/image.jpg', 'rb') as f:
            ...     file_data = f.read()
            >>> upload = client.media.upload(file=file_data, filename='image.jpg')
        """
        if file is None:
            raise ValueError("'file' parameter is required")

        if isinstance(file, str):
            # File path provided
            file_path = file
            file_data = open(file_path, "rb")
            file_name = filename or os.path.basename(file_path)
        else:
            # Bytes provided
            file_data = file  # type: ignore
            file_name = filename or "upload.png"

        try:
            files = {"image": (file_name, file_data)}
            return self.http_client.post("/upload", data=None, files=files)  # type: ignore
        finally:
            # Close file if we opened it
            if isinstance(file, str) and hasattr(file_data, "close"):
                file_data.close()  # type: ignore

    def upload_audio(
        self, file: Optional[Union[str, bytes]] = None, filename: Optional[str] = None
    ) -> MediaUploadAudioResponse:
        """
        Upload an audio file (max 2MB and 60 seconds)

        Args:
            file: File path (str) or file bytes
            filename: Filename for the upload (used if file is bytes)

        Returns:
            Upload response with audioURL

        Example:
            >>> # Upload from file path
            >>> upload = client.media.upload_audio(file='./path/to/audio.mp3')
            >>> print(upload['audioURL'])
            >>>
            >>> # Upload from bytes
            >>> with open('./path/to/audio.mp3', 'rb') as f:
            ...     file_data = f.read()
            >>> upload = client.media.upload_audio(file=file_data, filename='audio.mp3')
        """
        if file is None:
            raise ValueError("'file' parameter is required")

        if isinstance(file, str):
            # File path provided
            file_path = file
            file_data = open(file_path, "rb")
            file_name = filename or os.path.basename(file_path)
        else:
            # Bytes provided
            file_data = file  # type: ignore
            file_name = filename or "upload.mp3"

        try:
            files = {"audio": (file_name, file_data)}
            return self.http_client.post("/upload-audio", data=None, files=files)  # type: ignore
        finally:
            # Close file if we opened it
            if isinstance(file, str) and hasattr(file_data, "close"):
                file_data.close()  # type: ignore

