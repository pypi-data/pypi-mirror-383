# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-10-10

### Added
- Initial release of the Apiframe Python SDK
- Support for Midjourney Original API
  - Image generation (imagine)
  - Video generation (imagine_video, extend_video)
  - Upscaling (upscale_1x, upscale_alt, upscale_highres)
  - Variations and reroll
  - Face swap
  - Inpaint and outpaint
  - Pan, describe, blend, shorten, seed
- Support for Midjourney Pro API (MidjourneyAlt)
  - Fast and Turbo modes
  - All standard operations with improved performance
- Support for Flux AI
  - Multiple models (flux-schnell, flux-pro, flux-dev, flux-pro-1.1, flux-pro-1.1-ultra)
  - Convenience methods for each model
- Support for Ideogram
  - Generate, upscale, describe, remix
- Support for Luma AI video generation
  - Text to video
  - Image to video
  - Video extension
- Support for Suno AI music generation
  - Song generation with lyrics
  - Audio upload and extension
  - Lyrics generation
- Support for Udio AI music generation
- Support for Runway ML video generation
  - Text to video, image to video, video to video
  - Gen-3 and Gen-3 Turbo models
- Support for Kling AI video generation
  - Text to video, image to video
  - Virtual try-on feature
- Support for AI Photos
  - Training image upload
  - Model training
  - Photo generation
- Support for Media Upload
  - Image upload
  - Audio upload
- Task management
  - Task status checking
  - Batch task retrieval
  - Wait for completion with progress tracking
  - Account info retrieval
- Comprehensive error handling
  - ApiframeError base exception
  - AuthenticationError
  - RateLimitError
  - TimeoutError
  - ValidationError
- Type hints for better IDE support
- Context manager support for automatic cleanup
- Complete examples for all major features
- Comprehensive documentation

[1.0.0]: https://github.com/apiframe-ai/apiframe-python-sdk/releases/tag/v1.0.0

