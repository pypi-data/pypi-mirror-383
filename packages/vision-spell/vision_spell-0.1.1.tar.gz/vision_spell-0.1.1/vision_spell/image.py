from enum import StrEnum
from pathlib import Path
from typing import Any, Sequence, TypedDict
from typing_extensions import Literal
import fal_client
import base64
from io import BytesIO
from vision_spell.types import Image, ImageLike, Lora, LoraLike
from google.genai import types as google_genai_types


def load(path: str | Path) -> Image:
    """Load an image from a file path or URL."""
    return Image.load(path)


class ImageSize(TypedDict):
    width: int
    height: int


def __process_image_falai(image: ImageLike) -> str:
    """Process the input image and return its URL."""
    img = Image.load(image)
    image_url = fal_client.upload(img.bytes, content_type=img.mime)
    return image_url


def __process_image_google(im: ImageLike) -> google_genai_types.Image | None:
    if im is None:
        return None
    if isinstance(im, Image):
        return google_genai_types.Image(
            image_bytes=im.bytes,
            mime_type=im.mime,
        )
    return google_genai_types.Image.from_file(location=str(im))


def __fal_ai_image_model(model: str, prompt: str, **kwargs: Any) -> Image:
    kwargs = {k: v for k, v in kwargs.items() if v is not None}
    handler = fal_client.submit(
        model,
        arguments={
            "prompt": prompt,
            "sync_mode": True,
            **kwargs,
        },
    )
    response = handler.get()
    images = response.get("images", [])
    assert len(images) == 1, f"Expected 1 image, got {len(images)}"
    image_url = images[0].get("url")
    if image_url.startswith("http"):
        return Image.load(image_url)
    else:
        base64_data = image_url.split(",")[1]  # Extract the base64 data part
        mime_type = image_url.split(";")[0].split(":")[1]  # Extract the MIME type
        return Image(
            bytes=BytesIO(base64.b64decode(base64_data)).getvalue(),
            mime=mime_type or "image/png",
        )


def flex_1d(
    prompt: str,
    *,
    # square_hd, square, portrait_4_3, portrait_16_9, landscape_4_3, landscape_16_9
    image_size: (
        ImageSize
        | Literal[
            "square_hd",
            "square",
            "portrait_4_3",
            "portrait_16_9",
            "landscape_4_3",
            "landscape_16_9",
        ]
        | None
    ) = None,
    steps: int | None = None,
    seed: int | None = None,
    loras: Sequence[LoraLike] | None = None,
    guidance_scale: int | None = None,
    image: ImageLike | None = None,
) -> Image:
    """
    flex-1-dev

    # Input Schema:

    https://fal.ai/models/fal-ai/flux-lora/api#schema-input
    """
    model: str
    image_url = None
    if not image:
        model = "fal-ai/flux-lora"
        image_url = None
    else:
        model = "fal-ai/flux-lora/image-to-image"
        image_url = __process_image_falai(image)
    return __fal_ai_image_model(
        model=model,
        prompt=prompt,
        image_size=image_size,
        num_inference_steps=steps,
        seed=seed,
        loras=Lora.process(loras) if loras else None,
        guidance_scale=guidance_scale,
        image_url=image_url,
        num_images=1,
        enable_safety_checker=False,
        output_format="png",
    )


def flex_kontext(
    prompt: str,
    *,
    negative_prompt: str | None = None,
    image: ImageLike | list[ImageLike] | None = None,
    steps: int | None = None,
    guidance_scale: int | None = None,
    loras: Sequence[LoraLike] | None = None,
) -> Image:
    """
    flex-kontext

    # Input Schema:

    https://fal.ai/models/fal-ai/flux-pro/kontext/max/api#schema-input

    https://fal.ai/models/fal-ai/flux-pro/kontext/max/multi/api#schema-input

    https://fal.ai/models/fal-ai/flux-pro/kontext/max/text-to-image/api#schema-input
    """
    model: str
    image_url, image_urls = None, None
    match image:
        case _ if isinstance(image, list) and not loras:
            model = "fal-ai/flux-pro/kontext/max/multi"
            image_urls = [__process_image_falai(img) for img in image]
        case _ if image is not None and not isinstance(image, list) and not loras:
            model = "fal-ai/flux-pro/kontext/max"
            image_url = __process_image_falai(image)
        case _ if not loras:
            model = "fal-ai/flux-pro/kontext/max/text-to-image"
        case _ if not image and loras:
            model = "fal-ai/flux-kontext-lora/text-to-image"
        case _ if image and loras:
            model = "fal-ai/flux-kontext-lora"
            assert not isinstance(
                image, list
            ), "Only single image is supported with loras"
            image_url = __process_image_falai(image)
        case _:
            raise ValueError("Invalid combination of image and loras")
    return __fal_ai_image_model(
        model=model,
        prompt=prompt,
        negative_prompt=negative_prompt,
        image_url=image_url,
        image_urls=image_urls,
        num_inference_steps=steps,
        num_images=1,
        safety_tolerance=6,
        enable_safety_checker=False,
        guidance_scale=guidance_scale,
        output_format="png",
        loras=Lora.process(loras) if loras else None,
    )


def flex_kera(
    prompt: str,
    *,
    image_size: (
        Literal[
            "square_hd",
            "square",
            "portrait_4_3",
            "portrait_16_9",
            "landscape_4_3",
            "landscape_16_9",
        ]
        | ImageSize
        | None
    ) = None,
    image: ImageLike | None = None,
    strength: float | None = None,
    steps: int | None = None,
    guidance_scale: float | None = None,
    acceleration: Literal["none", "regular", "high"] | None = None,
    loras: Sequence[LoraLike] | None = None,
) -> Image:
    """
    flex-kera

    # Input Schema:

    https://fal.ai/models/fal-ai/flux/krea/api#schema-input

    https://fal.ai/models/fal-ai/flux/krea/image-to-image/api#schema-input
    """
    model: str
    image_url = None
    match image:
        case _ if image is not None and not loras:
            model = "fal-ai/flux/krea/image-to-image"
            image_url = __process_image_falai(image)
        case _ if not loras:
            model = "fal-ai/flux/krea"
        case _ if not image and loras:
            model = "fal-ai/flux-krea-lora"
        case _ if image and loras:
            model = "fal-ai/flux-krea-lora/image-to-image"
            image_url = __process_image_falai(image)
        case _:
            raise ValueError("Invalid combination of image and loras")
    return __fal_ai_image_model(
        model=model,
        prompt=prompt,
        image_url=image_url,
        num_inference_steps=steps,
        num_images=1,
        image_size=image_size,
        strength=strength,
        enable_safety_checker=False,
        guidance_scale=guidance_scale,
        acceleration=acceleration,
        output_format="png",
        loras=Lora.process(loras) if loras else None,
    )


class SDModel(StrEnum):
    SD_1_5 = "stable-diffusion-v1-5/stable-diffusion-v1-5"
    SD_2 = "stabilityai/stable-diffusion-2"
    SD_2_1 = "stabilityai/stable-diffusion-2-1"
    SD_3_5_LARGE = "stabilityai/stable-diffusion-3.5-large"
    XL_BASE_1_0 = "stabilityai/stable-diffusion-xl-base-1.0"
    XLL_DREAM_SHAPER = "Lykon/dreamshaper-xl-lightning"
    XLL_REAL_VIS = "SG161222/RealVisXL_V4.0_Lightning"

    def is_lightning(self) -> bool:
        return self in {SDModel.XLL_DREAM_SHAPER, SDModel.XLL_REAL_VIS}


def stable_diffusion(
    prompt: str,
    *,
    model: str | SDModel,
    negative_prompt: str | None = None,
    image: ImageLike | None = None,
    mask: ImageLike | None = None,
    noise_strength: float | None = None,
    loras: Sequence[LoraLike] | None = None,
    seed: int | None = None,
    # square_hd, square, portrait_4_3, portrait_16_9, landscape_4_3, landscape_16_9
    image_size: (
        Literal[
            "square_hd",
            "square",
            "portrait_4_3",
            "portrait_16_9",
            "landscape_4_3",
            "landscape_16_9",
        ]
        | ImageSize
        | None
    ) = None,
    steps: int | None = None,
    guidance_scale: float | None = None,
    clip_skip: int | None = None,
    scheduler: (
        Literal[
            "DPM++ 2M",
            "DPM++ 2M Karras",
            "DPM++ 2M SDE",
            "DPM++ 2M SDE Karras",
            "Euler",
            "Euler A",
            "Euler (trailing timesteps)",
            "LCM",
            "LCM (trailing timesteps)",
            "DDIM",
            "TCD",
        ]
        | None
    ) = None,
    sdxl_lightning: bool = False,
) -> Image:
    """
    stable-diffusion

    # Input Schema:

    https://fal.ai/models/fal-ai/lora/api#schema-input

    https://fal.ai/models/fal-ai/lora/image-to-image/api#schema-input
    """
    if sdxl_lightning:
        assert image is None, "image not supported with sdxl_lightning"
        assert mask is None, "mask not supported with sdxl_lightning"
        if isinstance(model, SDModel):
            assert model.is_lightning(), "model must be a lightning model"
        falai_model = "fal-ai/lightning-models"
    elif image is None:
        assert mask is None, "mask requires image to be provided"
        assert noise_strength is None, "noise_strength requires image to be provided"
        falai_model = "fal-ai/lora"
    elif mask is None:
        falai_model = "fal-ai/lora/image-to-image"
    else:
        falai_model = "fal-ai/lora/inpaint"
    model = model.value if isinstance(model, SDModel) else model
    if isinstance(model, str) and model.startswith("civitai:"):
        parts = model.split(":")
        assert len(parts) == 2, f"Invalid civitai model format: {model}"
        model_id = parts[1]
        model = f"https://civitai-models.0xdead.dev/{model_id}"
    return __fal_ai_image_model(
        model=falai_model,
        model_name=model,
        prompt=prompt,
        negative_prompt=negative_prompt,
        prompt_weighting=True,
        loras=Lora.process(loras) if loras else None,
        seed=seed,
        image_url=__process_image_falai(image) if image else None,
        mask_url=__process_image_falai(mask) if mask else None,
        noise_strength=noise_strength,
        image_size=image_size,
        num_inference_steps=steps,
        guidance_scale=guidance_scale,
        clip_skip=clip_skip,
        scheduler=scheduler,
        num_images=1,
        image_format="png",
        enable_safety_checker=False,
    )


def nano_banana(
    prompt: str,
    *,
    image: ImageLike | list[ImageLike] | None = None,
    aspect_ratio: Literal[
        "21:9", "1:1", "4:3", "3:2", "2:3", "5:4", "4:5", "3:4", "16:9", "9:16"
    ] = "1:1",
) -> Image:
    """
    gemini-2.5-flash-image

    # Input Schema:

    https://fal.ai/models/fal-ai/gemini-25-flash-image/api#schema-input

    https://fal.ai/models/fal-ai/gemini-25-flash-image/edit/api#schema-input
    """
    model: str
    if image is None:
        model = "fal-ai/gemini-25-flash-image"
        image_urls = None
    else:
        model = "fal-ai/gemini-25-flash-image/edit"
        if isinstance(image, list):
            image_urls = [__process_image_falai(img) for img in image]
        else:
            image_urls = [__process_image_falai(image)]
    return __fal_ai_image_model(
        model=model,
        prompt=prompt,
        image_urls=image_urls,
        num_images=1,
        output_format="png",
        aspect_ratio=aspect_ratio,
    )


__all__ = [
    "load",
    "SDModel",
    "flex_1d",
    "flex_kontext",
    "flex_kera",
    "nano_banana",
    "stable_diffusion",
]
