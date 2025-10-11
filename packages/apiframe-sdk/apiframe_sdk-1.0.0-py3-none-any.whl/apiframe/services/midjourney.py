"""
Midjourney Service - Original Midjourney API
"""

from typing import TYPE_CHECKING

from ..types import (
    MidjourneyBlendParams,
    MidjourneyDescribeParams,
    MidjourneyExtendVideoParams,
    MidjourneyFaceSwapParams,
    MidjourneyImagineParams,
    MidjourneyImagineVideoParams,
    MidjourneyInpaintParams,
    MidjourneyOutpaintParams,
    MidjourneyPanParams,
    MidjourneyRerollParams,
    MidjourneySeedParams,
    MidjourneyShortenParams,
    MidjourneyUpscale1xParams,
    MidjourneyUpscaleAltParams,
    MidjourneyUpscaleHighresParams,
    MidjourneyUpscaleParams,
    MidjourneyVariationsParams,
    MidjourneyVaryParams,
    MidjourneyZoomParams,
    TaskResponse,
)

if TYPE_CHECKING:
    from ..http_client import HttpClient


class Midjourney:
    """
    Midjourney - Original Midjourney API

    See: https://docs.apiframe.ai/api-endpoints
    """

    def __init__(self, http_client: "HttpClient") -> None:
        """
        Initialize Midjourney service

        Args:
            http_client: HTTP client instance
        """
        self.http_client = http_client

    def imagine(self, params: MidjourneyImagineParams) -> TaskResponse:
        """
        Create a new image generation task

        Args:
            params: Parameters for the imagine request

        Returns:
            Task response with task ID

        Example:
            >>> task = client.midjourney.imagine({
            ...     'prompt': 'a serene mountain landscape at sunset',
            ...     'aspect_ratio': '16:9'
            ... })
            >>> print(task['id'])
        """
        return self.http_client.post("/imagine", params)  # type: ignore

    def imagine_video(self, params: MidjourneyImagineVideoParams) -> TaskResponse:
        """
        Create a video generation task using a text prompt and image URL

        Args:
            params: Parameters including prompt and image_url

        Returns:
            Task response with task ID

        Example:
            >>> task = client.midjourney.imagine_video({
            ...     'prompt': 'cinematic mountain landscape',
            ...     'image_url': 'https://example.com/start-frame.jpg',
            ...     'motion': 'high'
            ... })
        """
        return self.http_client.post("/imagine-video", params)  # type: ignore

    def extend_video(self, params: MidjourneyExtendVideoParams) -> TaskResponse:
        """
        Extend previously generated videos

        Args:
            params: Parameters including parent_task_id, index, prompt, and optional image_url

        Returns:
            Task response with task ID

        Example:
            >>> task = client.midjourney.extend_video({
            ...     'parent_task_id': 'original_task_id',
            ...     'index': '1',
            ...     'prompt': 'continue the scene'
            ... })
        """
        return self.http_client.post("/imagine-video-extend", params)  # type: ignore

    def upscale(self, params: MidjourneyUpscaleParams) -> TaskResponse:
        """
        Upscale a specific image from a generation (legacy method)

        Args:
            params: Parameters including taskId and index

        Returns:
            Task response with task ID

        Note:
            Deprecated. Use upscale_1x, upscale_alt, or upscale_highres instead
        """
        return self.http_client.post("/midjourney/upscale", params)  # type: ignore

    def upscale_1x(self, params: MidjourneyUpscale1xParams) -> TaskResponse:
        """
        Upscale one of the 4 generated images to get a single image

        Args:
            params: Parameters including parent_task_id and index

        Returns:
            Task response with task ID

        Example:
            >>> task = client.midjourney.upscale_1x({
            ...     'parent_task_id': 'original_task_id',
            ...     'index': '1'
            ... })
        """
        return self.http_client.post("/upscale-1x", params)  # type: ignore

    def upscale_alt(self, params: MidjourneyUpscaleAltParams) -> TaskResponse:
        """
        Upscale with Subtle or Creative mode
        Subtle doubles the size keeping details similar to original, Creative adds details

        Args:
            params: Parameters including parent_task_id and type

        Returns:
            Task response with task ID

        Example:
            >>> task = client.midjourney.upscale_alt({
            ...     'parent_task_id': 'upscale1x_task_id',
            ...     'type': 'subtle'
            ... })
        """
        return self.http_client.post("/upscale-alt", params)  # type: ignore

    def upscale_highres(self, params: MidjourneyUpscaleHighresParams) -> TaskResponse:
        """
        Upscale any image to higher resolution (2x or 4x) - not from Midjourney
        Image must not be larger than 2048x2048

        Args:
            params: Parameters including parent_task_id or image_url, and type

        Returns:
            Task response with task ID

        Example:
            >>> task = client.midjourney.upscale_highres({
            ...     'image_url': 'https://example.com/image.jpg',
            ...     'type': '2x'
            ... })
        """
        return self.http_client.post("/upscale-highres", params)  # type: ignore

    def vary(self, params: MidjourneyVaryParams) -> TaskResponse:
        """
        Create variations of a specific image (legacy method)

        Args:
            params: Parameters including taskId, index, and optional strength

        Returns:
            Task response with task ID
        """
        return self.http_client.post("/midjourney/vary", params)  # type: ignore

    def inpaint(self, params: MidjourneyInpaintParams) -> TaskResponse:
        """
        Inpaint (Vary Region) - Redraw a selected area of an image

        Args:
            params: Parameters including parent_task_id, mask, and prompt

        Returns:
            Task response with task ID

        Example:
            >>> task = client.midjourney.inpaint({
            ...     'parent_task_id': 'upscale1x_task_id',
            ...     'mask': 'base64_encoded_mask_image',
            ...     'prompt': 'a red sports car'
            ... })
        """
        return self.http_client.post("/inpaint", params)  # type: ignore

    def outpaint(self, params: MidjourneyOutpaintParams) -> TaskResponse:
        """
        Outpaint (Zoom Out) - Enlarges an image's canvas beyond its original size

        Args:
            params: Parameters including parent_task_id and zoom_ratio

        Returns:
            Task response with task ID

        Example:
            >>> task = client.midjourney.outpaint({
            ...     'parent_task_id': 'upscale1x_task_id',
            ...     'zoom_ratio': 2,
            ...     'prompt': 'expand the scene'
            ... })
        """
        return self.http_client.post("/outpaint", params)  # type: ignore

    def pan(self, params: MidjourneyPanParams) -> TaskResponse:
        """
        Pan - Broadens the image canvas in a specific direction

        Args:
            params: Parameters including parent_task_id and direction

        Returns:
            Task response with task ID

        Example:
            >>> task = client.midjourney.pan({
            ...     'parent_task_id': 'upscale1x_task_id',
            ...     'direction': 'left'
            ... })
        """
        return self.http_client.post("/pan", params)  # type: ignore

    def describe(self, params: MidjourneyDescribeParams) -> TaskResponse:
        """
        Describe an image with prompts - Writes four example prompts based on an image

        Args:
            params: Parameters including image_url

        Returns:
            Task response with task ID

        Example:
            >>> task = client.midjourney.describe({
            ...     'image_url': 'https://example.com/image.jpg'
            ... })
        """
        return self.http_client.post("/describe", params)  # type: ignore

    def blend(self, params: MidjourneyBlendParams) -> TaskResponse:
        """
        Blend multiple images into one image

        Args:
            params: Parameters including array of image URLs (2-5 images)

        Returns:
            Task response with task ID

        Example:
            >>> task = client.midjourney.blend({
            ...     'image_urls': [
            ...         'https://example.com/image1.jpg',
            ...         'https://example.com/image2.jpg'
            ...     ],
            ...     'dimension': 'landscape'
            ... })
        """
        return self.http_client.post("/blend", params)  # type: ignore

    def shorten(self, params: MidjourneyShortenParams) -> TaskResponse:
        """
        Shorten a prompt - Analyzes and suggests optimizations for your prompt

        Args:
            params: Parameters including the prompt to shorten

        Returns:
            Task response with task ID

        Example:
            >>> task = client.midjourney.shorten({
            ...     'prompt': 'a very beautiful and amazing sunset over mountains'
            ... })
        """
        return self.http_client.post("/shorten", params)  # type: ignore

    def seed(self, params: MidjourneySeedParams) -> TaskResponse:
        """
        Get the seed of a generated image

        Args:
            params: Parameters including task_id

        Returns:
            Task response with seed information

        Example:
            >>> task = client.midjourney.seed({
            ...     'task_id': 'original_task_id'
            ... })
        """
        return self.http_client.post("/seed", params)  # type: ignore

    def zoom(self, params: MidjourneyZoomParams) -> TaskResponse:
        """
        Zoom out from an image (legacy method)

        Args:
            params: Parameters including taskId and zoom level

        Returns:
            Task response with task ID

        Note:
            Deprecated. Use outpaint instead
        """
        return self.http_client.post("/midjourney/zoom", params)  # type: ignore

    def reroll(self, params: MidjourneyRerollParams) -> TaskResponse:
        """
        Reroll to create new images from a previous Imagine task

        Args:
            params: Parameters including parent_task_id

        Returns:
            Task response with task ID

        Example:
            >>> task = client.midjourney.reroll({
            ...     'parent_task_id': 'original_task_id'
            ... })
        """
        return self.http_client.post("/reroll", params)  # type: ignore

    def variations(self, params: MidjourneyVariationsParams) -> TaskResponse:
        """
        Create 4 new variations of one of the 4 generated images

        Args:
            params: Parameters including parent_task_id and index

        Returns:
            Task response with task ID

        Example:
            >>> task = client.midjourney.variations({
            ...     'parent_task_id': 'original_task_id',
            ...     'index': '1'
            ... })
        """
        return self.http_client.post("/variations", params)  # type: ignore

    def face_swap(self, params: MidjourneyFaceSwapParams) -> TaskResponse:
        """
        Face swap between two images

        Args:
            params: Parameters including target_image_url and swap_image_url

        Returns:
            Task response with task ID

        Example:
            >>> task = client.midjourney.face_swap({
            ...     'target_image_url': 'https://example.com/target.jpg',
            ...     'swap_image_url': 'https://example.com/face.jpg'
            ... })
        """
        return self.http_client.post("/faceswap", params)  # type: ignore

