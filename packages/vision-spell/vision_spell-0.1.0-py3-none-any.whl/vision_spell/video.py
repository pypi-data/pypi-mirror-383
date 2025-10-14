import os
import time
from typing import Any, Literal, Sequence
from pathlib import Path
import fal_client
from google import genai
from vision_spell.types import Video, ImageLike, VideoLike, Lora, LoraLike
from google.genai import types
from .image import __process_image_google, __process_image_falai


def load(path: str | Path) -> Video:
    """Load a video from a file path or URL."""
    return Video.load(path)


def __fal_ai_video_model(model: str, prompt: str, **kwargs: Any) -> Video:
    kwargs = {k: v for k, v in kwargs.items() if v is not None}
    handler = fal_client.subscribe(
        model,
        arguments={
            "prompt": prompt,
            "enable_safety_checker": False,
            "enable_output_safety_checker": False,
            **kwargs,
        },
    )
    url = handler["video"]["url"]
    return Video.load(url)


def hunyuan(
    prompt: str,
    *,
    image: ImageLike | None = None,
    seed: int | None = None,
    pro_mode: bool = False,
    aspect_ratio: Literal["16:9", "9:16"] | None = None,
    resolution: Literal["480p", "580p", "720p"] | None = None,
    num_frames: Literal[129, 85] | None = None,
    i2v_stability: bool | None = None,
    loras: Sequence[LoraLike] | None = None,
) -> Video:
    """
    wan2.2-a14b

    # Input Schema:

    https://fal.ai/models/fal-ai/wan-t2v/api#schema-input

    https://fal.ai/models/fal-ai/wan-i2v/api#schema-input
    """
    if image is None and not loras:
        model = "fal-ai/hunyuan-video"
    elif image and not loras:
        model = "fal-ai/hunyuan-video-image-to-video"
    elif image is None and loras:
        model = "fal-ai/hunyuan-video-lora"
    else:
        model = "fal-ai/hunyuan-video-img2vid-lora"
    image_url = __process_image_falai(image) if image else None
    return __fal_ai_video_model(
        model=model,
        prompt=prompt,
        image_url=image_url,
        seed=seed,
        pro_mode=pro_mode,
        aspect_ratio=aspect_ratio,
        resolution=resolution,
        num_frames=num_frames,
        i2v_stability=i2v_stability,
        loras=Lora.process(loras) if loras else None,
    )


def wan21(
    prompt: str,
    *,
    negative_prompt: str | None = None,
    image: ImageLike | None = None,
    num_frames: int | None = None,
    frames_per_second: int | None = None,
    seed: int | None = None,
    resolution: Literal["480p", "720p"] | None = None,
    steps: int | None = None,
    guide_scale: float | None = None,
    shift: float | None = None,
    enable_prompt_expansion: bool | None = None,
    acceleration: Literal["none", "regular"] | None = None,
    aspect_ratio: Literal["auto", "16:9", "9:16", "1:1"] | None = None,
    loras: Sequence[LoraLike] | None = None,
) -> Video:
    """
    wan2.2-a14b

    # Input Schema:

    https://fal.ai/models/fal-ai/wan-t2v/api#schema-input

    https://fal.ai/models/fal-ai/wan-i2v/api#schema-input
    """
    if image is None and not loras:
        model = "fal-ai/wan-t2v"
    elif image and not loras:
        model = "fal-ai/wan-i2v"
    elif image is None and loras:
        model = "fal-ai/wan-t2v-lora"
    else:
        model = "fal-ai/wan-i2v-lora"
    image_url = __process_image_falai(image) if image else None
    return __fal_ai_video_model(
        model=model,
        prompt=prompt,
        negative_prompt=negative_prompt,
        image_url=image_url,
        num_frames=num_frames,
        frames_per_second=frames_per_second,
        seed=seed,
        resolution=resolution,
        num_inference_steps=steps,
        guidance_scale=guide_scale,
        shift=shift,
        enable_prompt_expansion=enable_prompt_expansion,
        acceleration=acceleration,
        aspect_ratio=aspect_ratio,
        loras=Lora.process(loras) if loras else None,
    )


def wan22(
    prompt: str,
    *,
    negative_prompt: str | None = None,
    image: ImageLike | None = None,
    num_frames: int | None = None,
    frames_per_second: int | None = None,
    seed: int | None = None,
    resolution: Literal["480p", "580p", "720p"] | None = None,
    aspect_ratio: Literal["auto", "16:9", "9:16", "1:1"] | None = None,
    steps: int | None = None,
    enable_prompt_expansion: bool | None = None,
    acceleration: Literal["none", "regular"] | None = None,
    guidance_scale: float | None = None,
    guidance_scale_2: float | None = None,
    shift: float | None = None,
    interpolator_model: Literal["none", "film", "rife"] | None = None,
    num_interpolated_frames: Literal[0, 1, 2, 3, 4] | None = None,
    adjust_fps_for_interpolation: bool | None = None,
    video_quality: Literal["low", "medium", "high", "maximum"] | None = None,
    video_write_mode: Literal["fast", "balanced", "small"] | None = None,
    end_image: ImageLike | None = None,
    loras: Sequence[LoraLike] | None = None,
) -> Video:
    """
    wan2.2-a14b

    # Input Schema:

    https://fal.ai/models/fal-ai/wan/v2.2-a14b/text-to-video/api#schema-input

    https://fal.ai/models/fal-ai/wan/v2.2-a14b/image-to-video/api#schema-input
    """
    if end_image:
        assert image is not None, "end_image requires image to be provided"
    model = "fal-ai/wan/v2.2-a14b/" + (
        "text-to-video" if image is None else "image-to-video"
    )
    if loras:
        model += "/lora"
    image_url = __process_image_falai(image) if image else None
    end_image_url = __process_image_falai(end_image) if end_image else None
    return __fal_ai_video_model(
        model=model,
        prompt=prompt,
        negative_prompt=negative_prompt,
        image_url=image_url,
        num_frames=num_frames,
        frames_per_second=frames_per_second,
        seed=seed,
        resolution=resolution,
        aspect_ratio=aspect_ratio,
        num_inference_steps=steps,
        enable_prompt_expansion=enable_prompt_expansion,
        acceleration=acceleration,
        guidance_scale=guidance_scale,
        guidance_scale_2=guidance_scale_2,
        shift=shift,
        interpolator_model=interpolator_model,
        num_interpolated_frames=num_interpolated_frames,
        adjust_fps_for_interpolation=adjust_fps_for_interpolation,
        video_quality=video_quality,
        video_write_mode=video_write_mode,
        end_image_url=end_image_url,
        loras=Lora.process(loras) if loras else None,
    )


def wan25(
    prompt: str,
    *,
    negative_prompt: str | None = None,
    image: ImageLike | None = None,
    aspect_ratio: Literal["16:9", "9:16", "1:1"] | None = None,
    resolution: Literal["480p", "720p", "1080p"] | None = None,
    duration: Literal[5, 10] | None = None,
    enable_prompt_expansion: bool | None = None,
    seed: int | None = None,
) -> Video:
    """
    wan2.2-a14b

    # Input Schema:

    https://fal.ai/models/fal-ai/wan-25-preview/text-to-video/api#schema-input

    https://fal.ai/models/fal-ai/wan-25-preview/image-to-video/api#schema-input
    """
    model = "fal-ai/wan-25-preview/" + (
        "text-to-video" if image is None else "image-to-video"
    )
    if image is not None:
        assert not aspect_ratio, "aspect_ratio is not supported with image input"
    image_url = __process_image_falai(image) if image else None
    return __fal_ai_video_model(
        model=model,
        prompt=prompt,
        negative_prompt=negative_prompt,
        image_url=image_url,
        aspect_ratio=aspect_ratio,
        resolution=resolution,
        duration=duration,
        enable_prompt_expansion=enable_prompt_expansion,
        seed=seed,
    )


def sora2(
    prompt: str,
    *,
    image: ImageLike | None = None,
    resolution: Literal["720p"] | None = None,
    aspect_ratio: Literal["16:9", "9:16"] | None = None,
    duration: Literal[4, 8, 12] | None = None,
) -> Video:
    """
    sora-2

    # Input Schema:

    https://fal.ai/models/fal-ai/sora-2/text-to-video/api#schema-input

    https://fal.ai/models/fal-ai/sora-2/image-to-video/api#schema-input
    """
    model = (
        "fal-ai/sora-2/text-to-video"
        if image is None
        else "fal-ai/sora-2/image-to-video"
    )
    return __fal_ai_video_model(
        model=model,
        prompt=prompt,
        image_url=__process_image_falai(image) if image else None,
        resolution=resolution,
        aspect_ratio=aspect_ratio,
        duration=duration,
    )


def sora2_pro(
    prompt: str,
    *,
    image: ImageLike | None = None,
    resolution: Literal["720p", "1080p"] | None = None,
    aspect_ratio: Literal["16:9", "9:16"] | None = None,
    duration: Literal[4, 8, 12] | None = None,
) -> Video:
    """
    sora-2/pro

    # Input Schema:

    https://fal.ai/models/fal-ai/sora-2/text-to-video/pro/api#schema-input

    https://fal.ai/models/fal-ai/sora-2/image-to-video/pro/api#schema-input
    """
    model = (
        "fal-ai/sora-2/text-to-video/pro"
        if image is None
        else "fal-ai/sora-2/image-to-video/pro"
    )
    return __fal_ai_video_model(
        model=model,
        prompt=prompt,
        image_url=__process_image_falai(image) if image else None,
        resolution=resolution,
        aspect_ratio=aspect_ratio,
        duration=duration,
    )


def __veo3(
    prompt: str,
    *,
    negative_prompt: str | None = None,
    image: ImageLike | None = None,
    last_frame: ImageLike | None = None,
    video: VideoLike | None = None,
    fast: bool = False,
) -> Video:
    """
    Generate an image based on the provided prompt using Google's VEO3 model.
    """
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    _image = __process_image_google(image) if image else None
    _last_frame = __process_image_google(last_frame) if last_frame else None

    video = Video.load(video) if isinstance(video, (str, Path)) else video
    video_data = (
        types.Video(video_bytes=video.bytes, mime_type=video.mime)
        if isinstance(video, Video)
        else None
    )

    operation = client.models.generate_videos(
        model=(
            "veo-3.0-generate-preview" if not fast else "veo-3.0-fast-generate-preview"
        ),
        prompt=prompt,
        image=_image,
        video=video_data,
        config=types.GenerateVideosConfig(
            aspect_ratio="16:9",  # "16:9" or "9:16",
            negative_prompt=negative_prompt,
            last_frame=_last_frame,
        ),
    )

    while not operation.done:
        time.sleep(20)
        operation = client.operations.get(operation)

    if not operation.response or not operation.response.generated_videos:
        print("RESPONSE:", operation.response)
        print("ERROR:", operation.error)
        raise RuntimeError("Video generation failed")

    v = operation.response.generated_videos[0].video
    assert v, "No video generated"
    client.files.download(file=v)
    assert v.video_bytes, "No video generated"
    return Video(bytes=v.video_bytes)


def veo3(
    prompt: str,
    *,
    negative_prompt: str | None = None,
    image: ImageLike | None = None,
    last_frame: ImageLike | None = None,
    video: VideoLike | None = None,
) -> Video:
    """
    Generate an image based on the provided prompt using Google's VEO3 model.
    """
    return __veo3(
        prompt,
        negative_prompt=negative_prompt,
        image=image,
        last_frame=last_frame,
        video=video,
        fast=False,
    )


def veo3_fast(
    prompt: str,
    *,
    negative_prompt: str | None = None,
    image: ImageLike | None = None,
    last_frame: ImageLike | None = None,
    video: VideoLike | None = None,
) -> Video:
    """
    Generate an image based on the provided prompt using Google's VEO3 model.
    """
    return __veo3(
        prompt,
        negative_prompt=negative_prompt,
        image=image,
        last_frame=last_frame,
        video=video,
        fast=True,
    )


__all__ = [
    "load",
    "hunyuan",
    "wan21",
    "wan22",
    "wan25",
    "veo3",
    "veo3_fast",
]
