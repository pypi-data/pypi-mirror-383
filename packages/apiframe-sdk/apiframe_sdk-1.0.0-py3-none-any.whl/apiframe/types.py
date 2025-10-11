"""
Type definitions for Apiframe SDK
"""

from typing import Any, Callable, Dict, List, Literal, Optional, TypedDict, Union


class ApiframeConfig(TypedDict, total=False):
    """Configuration for Apiframe client"""

    api_key: str
    base_url: Optional[str]
    timeout: Optional[int]


class TaskResponse(TypedDict, total=False):
    """Response from task operations"""

    id: str
    status: Literal["pending", "processing", "completed", "failed"]
    progress: Optional[int]
    result: Optional[Any]
    error: Optional[str]
    message: Optional[str]
    createdAt: Optional[str]
    updatedAt: Optional[str]
    imageUrl: Optional[str]
    image_urls: Optional[List[str]]
    original_image_url: Optional[str]
    downloadUrl: Optional[str]
    videoUrl: Optional[str]
    video_urls: Optional[List[str]]
    actions: Optional[List[str]]
    task_type: Optional[str]


class WaitForOptions(TypedDict, total=False):
    """Options for waiting for task completion"""

    on_progress: Optional[Callable[[int], None]]
    interval: Optional[int]
    timeout: Optional[int]


class AccountInfo(TypedDict, total=False):
    """Account information"""

    email: str
    credits: int
    total_images: int
    plan: str


# Midjourney Original API Types
class MidjourneyImagineParams(TypedDict, total=False):
    """Parameters for Midjourney imagine endpoint"""

    prompt: str
    aspect_ratio: Optional[str]
    webhook_url: Optional[str]
    webhook_secret: Optional[str]


class MidjourneyImagineVideoParams(TypedDict, total=False):
    """Parameters for Midjourney imagine video endpoint"""

    prompt: str
    image_url: str
    motion: Optional[Literal["low", "high"]]
    webhook_url: Optional[str]
    webhook_secret: Optional[str]


class MidjourneyExtendVideoParams(TypedDict, total=False):
    """Parameters for Midjourney extend video endpoint"""

    parent_task_id: str
    index: Union[str, int]
    prompt: str
    image_url: Optional[str]
    motion: Optional[Literal["low", "high"]]
    webhook_url: Optional[str]
    webhook_secret: Optional[str]


class MidjourneyRerollParams(TypedDict, total=False):
    """Parameters for Midjourney reroll endpoint"""

    parent_task_id: str
    prompt: Optional[str]
    webhook_url: Optional[str]
    webhook_secret: Optional[str]


class MidjourneyVariationsParams(TypedDict, total=False):
    """Parameters for Midjourney variations endpoint"""

    parent_task_id: str
    index: Union[str, int]
    webhook_url: Optional[str]
    webhook_secret: Optional[str]


class MidjourneyFaceSwapParams(TypedDict, total=False):
    """Parameters for Midjourney face swap endpoint"""

    target_image_url: str
    swap_image_url: str
    webhook_url: Optional[str]
    webhook_secret: Optional[str]


class MidjourneyUpscaleParams(TypedDict, total=False):
    """Parameters for Midjourney upscale endpoint (legacy)"""

    taskId: str
    index: Union[str, int]


class MidjourneyUpscale1xParams(TypedDict, total=False):
    """Parameters for Midjourney upscale 1x endpoint"""

    parent_task_id: str
    index: Union[str, int]
    webhook_url: Optional[str]
    webhook_secret: Optional[str]


class MidjourneyUpscaleAltParams(TypedDict, total=False):
    """Parameters for Midjourney upscale alt endpoint"""

    parent_task_id: str
    type: Literal["subtle", "creative"]
    webhook_url: Optional[str]
    webhook_secret: Optional[str]


class MidjourneyUpscaleHighresParams(TypedDict, total=False):
    """Parameters for Midjourney upscale highres endpoint"""

    parent_task_id: Optional[str]
    image_url: Optional[str]
    type: Literal["2x", "4x"]
    index: Optional[str]
    webhook_url: Optional[str]
    webhook_secret: Optional[str]


class MidjourneyVaryParams(TypedDict, total=False):
    """Parameters for Midjourney vary endpoint (legacy)"""

    taskId: str
    index: Union[str, int]
    strength: Optional[int]


class MidjourneyInpaintParams(TypedDict, total=False):
    """Parameters for Midjourney inpaint endpoint"""

    parent_task_id: str
    mask: str
    prompt: str
    webhook_url: Optional[str]
    webhook_secret: Optional[str]


class MidjourneyOutpaintParams(TypedDict, total=False):
    """Parameters for Midjourney outpaint endpoint"""

    parent_task_id: str
    zoom_ratio: float
    aspect_ratio: Optional[str]
    prompt: Optional[str]
    webhook_url: Optional[str]
    webhook_secret: Optional[str]


class MidjourneyPanParams(TypedDict, total=False):
    """Parameters for Midjourney pan endpoint"""

    parent_task_id: str
    direction: Literal["up", "down", "left", "right"]
    webhook_url: Optional[str]
    webhook_secret: Optional[str]


class MidjourneyShortenParams(TypedDict, total=False):
    """Parameters for Midjourney shorten endpoint"""

    prompt: str
    webhook_url: Optional[str]
    webhook_secret: Optional[str]


class MidjourneyDescribeParams(TypedDict, total=False):
    """Parameters for Midjourney describe endpoint"""

    image_url: str
    webhook_url: Optional[str]
    webhook_secret: Optional[str]


class MidjourneyBlendParams(TypedDict, total=False):
    """Parameters for Midjourney blend endpoint"""

    image_urls: List[str]
    dimension: Optional[Literal["square", "portrait", "landscape"]]
    webhook_url: Optional[str]
    webhook_secret: Optional[str]


class MidjourneySeedParams(TypedDict, total=False):
    """Parameters for Midjourney seed endpoint"""

    task_id: str
    webhook_url: Optional[str]
    webhook_secret: Optional[str]


class MidjourneyZoomParams(TypedDict, total=False):
    """Parameters for Midjourney zoom endpoint (legacy)"""

    taskId: str
    zoom: Optional[int]


# Midjourney Pro API Types (MidjourneyAlt)
class MidjourneyAltImagineParams(TypedDict, total=False):
    """Parameters for Midjourney Pro imagine endpoint"""

    prompt: str
    mode: Optional[Literal["fast", "turbo"]]
    webhook_url: Optional[str]
    webhook_secret: Optional[str]


class MidjourneyAltUpscaleParams(TypedDict, total=False):
    """Parameters for Midjourney Pro upscale endpoint"""

    parent_task_id: str
    index: Union[str, int]
    type: Literal["subtle", "creative"]
    webhook_url: Optional[str]
    webhook_secret: Optional[str]


class MidjourneyAltVaryParams(TypedDict, total=False):
    """Parameters for Midjourney Pro vary endpoint"""

    parent_task_id: str
    index: Union[str, int]
    type: Literal["strong", "subtle"]
    webhook_url: Optional[str]
    webhook_secret: Optional[str]


class MidjourneyAltVariationsParams(TypedDict, total=False):
    """Parameters for Midjourney Pro variations endpoint"""

    parent_task_id: str
    index: Union[str, int]
    webhook_url: Optional[str]
    webhook_secret: Optional[str]


class MidjourneyAltZoomParams(TypedDict, total=False):
    """Parameters for Midjourney Pro zoom endpoint"""

    parent_task_id: str
    index: Union[str, int]
    type: str
    webhook_url: Optional[str]
    webhook_secret: Optional[str]


class MidjourneyAltPanParams(TypedDict, total=False):
    """Parameters for Midjourney Pro pan endpoint"""

    parent_task_id: str
    index: Union[str, int]
    type: Literal["up", "down", "left", "right"]
    webhook_url: Optional[str]
    webhook_secret: Optional[str]


# Flux Types
class FluxGenerateParams(TypedDict, total=False):
    """Parameters for Flux generate endpoint"""

    model: str
    prompt: str
    image_prompt: Optional[str]
    image_prompt_strength: Optional[float]
    prompt_upsampling: Optional[bool]
    width: Optional[int]
    height: Optional[int]
    aspect_ratio: Optional[str]
    steps: Optional[int]
    guidance: Optional[float]
    interval: Optional[int]
    seed: Optional[int]
    safety_tolerance: Optional[int]
    raw: Optional[bool]
    webhook_url: Optional[str]
    webhook_secret: Optional[str]


# Ideogram Types
class IdeogramGenerateParams(TypedDict, total=False):
    """Parameters for Ideogram generate endpoint"""

    prompt: str
    style_type: Optional[str]
    negative_prompt: Optional[str]
    seed: Optional[int]
    magic_prompt_option: Optional[str]
    aspect_ratio: Optional[str]
    resolution: Optional[str]


class IdeogramUpscaleParams(TypedDict, total=False):
    """Parameters for Ideogram upscale endpoint"""

    image_url: str
    prompt: str
    resemblance: int
    detail: Optional[int]
    seed: Optional[int]
    magic_prompt_option: Optional[str]


class IdeogramRemixParams(TypedDict, total=False):
    """Parameters for Ideogram remix endpoint"""

    image_url: str
    prompt: str
    image_weight: int
    style_type: Optional[str]
    negative_prompt: Optional[str]
    seed: Optional[int]
    magic_prompt_option: Optional[str]
    aspect_ratio: Optional[str]
    resolution: Optional[str]


class IdeogramDescribeParams(TypedDict, total=False):
    """Parameters for Ideogram describe endpoint"""

    image_url: str


# Luma Types
class LumaGenerateParams(TypedDict, total=False):
    """Parameters for Luma generate endpoint"""

    prompt: str
    image_url: Optional[str]
    end_image_url: Optional[str]
    enhance_prompt: Optional[bool]
    aspect_ratio: Optional[str]
    loop: Optional[bool]
    webhook_url: Optional[str]
    webhook_secret: Optional[str]


class LumaExtendParams(TypedDict, total=False):
    """Parameters for Luma extend endpoint"""

    parent_task_id: str
    prompt: str
    image_url: Optional[str]
    end_image_url: Optional[str]
    enhance_prompt: Optional[bool]
    aspect_ratio: Optional[str]
    webhook_url: Optional[str]
    webhook_secret: Optional[str]


# Suno Types
class SunoGenerateParams(TypedDict, total=False):
    """Parameters for Suno generate endpoint"""

    prompt: str
    lyrics: Optional[str]
    model: Optional[str]
    make_instrumental: Optional[bool]
    title: Optional[str]
    tags: Optional[str]
    webhook_url: Optional[str]
    webhook_secret: Optional[str]


class SunoUploadParams(TypedDict, total=False):
    """Parameters for Suno upload endpoint"""

    audio_url: str


class SunoExtendParams(TypedDict, total=False):
    """Parameters for Suno extend endpoint"""

    parent_task_id: Optional[str]
    song_id: Optional[str]
    continue_at: int
    from_upload: Optional[bool]
    prompt: Optional[str]
    lyrics: Optional[str]
    title: Optional[str]
    tags: Optional[str]
    webhook_url: Optional[str]
    webhook_secret: Optional[str]


class SunoLyricsParams(TypedDict, total=False):
    """Parameters for Suno lyrics endpoint"""

    prompt: str


# Udio Types
class UdioGenerateParams(TypedDict, total=False):
    """Parameters for Udio generate endpoint"""

    prompt: str
    lyrics: Optional[str]
    model: Optional[str]
    bypass_prompt_optimization: Optional[bool]
    prompt_strength: Optional[float]
    clarity_strength: Optional[float]
    lyrics_strength: Optional[float]
    generation_quality: Optional[float]
    negative_prompt: Optional[str]
    lyrics_placement_start: Optional[int]
    lyrics_placement_end: Optional[int]
    tags: Optional[str]
    webhook_url: Optional[str]
    webhook_secret: Optional[str]


# Runway Types
class RunwayGenerateParams(TypedDict, total=False):
    """Parameters for Runway generate endpoint"""

    prompt: str
    generation_type: Literal["text2video", "image2video", "video2video"]
    image_url: Optional[str]
    end_image_url: Optional[str]
    video_url: Optional[str]
    aspect_ratio: Optional[str]
    model: Optional[str]
    duration: Optional[int]
    flip: Optional[bool]
    webhook_url: Optional[str]
    webhook_secret: Optional[str]


# Kling Types
class KlingGenerateParams(TypedDict, total=False):
    """Parameters for Kling generate endpoint"""

    prompt: str
    generation_type: Literal["text2video", "image2video"]
    negative_prompt: Optional[str]
    image_url: Optional[str]
    end_image_url: Optional[str]
    mode: Optional[str]
    aspect_ratio: Optional[str]
    model: Optional[str]
    duration: Optional[int]
    cfg_scale: Optional[float]
    webhook_url: Optional[str]
    webhook_secret: Optional[str]


class KlingTryonParams(TypedDict, total=False):
    """Parameters for Kling tryon endpoint"""

    human_image_url: str
    cloth_image_url: str
    model: Optional[str]
    webhook_url: Optional[str]
    webhook_secret: Optional[str]


# AI Photos Types
class AIPhotosUploadParams(TypedDict, total=False):
    """Parameters for AI Photos upload endpoint"""

    images: List[str]
    ethnicity: str
    gender: str
    age: int
    webhook_url: Optional[str]
    webhook_secret: Optional[str]


class AIPhotosTrainParams(TypedDict, total=False):
    """Parameters for AI Photos train endpoint"""

    training_images_id: str
    trigger_word: str
    webhook_url: Optional[str]
    webhook_secret: Optional[str]


class AIPhotosGenerateParams(TypedDict, total=False):
    """Parameters for AI Photos generate endpoint"""

    training_id: str
    prompt: str
    aspect_ratio: Optional[str]
    width: Optional[str]
    height: Optional[str]
    number_of_images: Optional[str]
    seed: Optional[int]


# Media Upload Types
class MediaUploadResponse(TypedDict):
    """Response from media upload"""

    imageURL: str


class MediaUploadAudioResponse(TypedDict):
    """Response from audio upload"""

    audioURL: str

