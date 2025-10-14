from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Any, Literal, Sequence, Union, TypeGuard
from IPython.display import display, Video as IPVideo, Image as IPImage
import PIL.Image
from pydantic import BaseModel, Field
import requests
from ruamel.yaml import YAML
import cv2
import tempfile
from moviepy import concatenate_videoclips, VideoFileClip
import contextlib


def _get_human_readable_size(size: int) -> str:
    s = float(size)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if s < 1024:
            return f"{s:.2f} {unit}"
        s /= 1024
    return f"{s:.2f} PB"


@dataclass
class Video:
    bytes: bytes
    mime: str = "video/mp4"
    temporary_url: str | None = None

    def save(self, path: str | Path) -> "Video":
        """
        Save the video to a local file.
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(self.bytes)
        return self

    def __repr__(self) -> str:
        s = _get_human_readable_size(len(self.bytes))
        url = f", {self.temporary_url}" if self.temporary_url else ""
        return f"Video({self.mime}, {s}{url})"

    def show(self, *, small=False) -> "Video":
        w = 240 if small else None
        h = 135 if small else None
        display(
            IPVideo(
                data=self.bytes,
                width=w,
                height=h,
                html_attributes=f"controls style='object-fit: contain; object-position: center center; background-color: black;'",
                embed=True,
                mimetype=self.mime,
            )
        )
        return self

    @staticmethod
    def load(path_or_url: "VideoLike") -> "Video":
        """
        Load a video from a file or URL.
        """
        if isinstance(path_or_url, Video):
            return path_or_url
        temporary_url = None
        if isinstance(path_or_url, Path) or not path_or_url.startswith("http"):
            path = Path(path_or_url)
            match path.suffix:
                case ".mp4":
                    mime = "video/mp4"
                case _:
                    raise ValueError(f"Unsupported video format: {path.suffix}")
            assert path.exists(), f"File not found: {path}"
            bytes = path.read_bytes()
        else:
            temporary_url = path_or_url
            response = requests.get(path_or_url)
            response.raise_for_status()
            bytes = response.content
            mime = (
                response.headers.get("Content-Type", "video/mp4")
                if not temporary_url.endswith(".mp4")
                else "video/mp4"
            )
        return Video(bytes=bytes, mime=mime, temporary_url=temporary_url)

    def __get_frame(self, pos: Literal["first", "last"]) -> "Image":
        with tempfile.NamedTemporaryFile(delete=True, suffix=".mp4") as temp_file:
            temp_file.write(self.bytes)
            vs = cv2.VideoCapture(temp_file.name)
            if pos == "first":
                vs.set(cv2.CAP_PROP_POS_FRAMES, 0)
            else:
                frames = vs.get(cv2.CAP_PROP_FRAME_COUNT)
                vs.set(cv2.CAP_PROP_POS_FRAMES, frames - 1)
            success, frame = vs.read()
            if not success:
                raise ValueError("Failed to extract last frame")
            return Image(
                bytes=cv2.imencode(".png", frame)[1].tobytes(), mime="image/png"
            )

    def get_first_frame(self) -> "Image":
        return self.__get_frame("first")

    def get_last_frame(self) -> "Image":
        return self.__get_frame("last")

    @staticmethod
    def concat(videos: Sequence[Union[str, Path, "Video"]]) -> "Video":
        with contextlib.ExitStack() as stack:
            video_clips = []
            for v in videos:
                if isinstance(v, Video):
                    f = tempfile.NamedTemporaryFile(delete=True, suffix=".mp4")
                    f.write(v.bytes)
                    f.flush()
                    stack.enter_context(f)
                    video_clips.append(VideoFileClip(f.name))
                else:
                    video_clips.append(VideoFileClip(str(v)))
            concat_clip = concatenate_videoclips(video_clips, method="compose")
            with tempfile.NamedTemporaryFile(delete=True, suffix=".mp4") as out:
                concat_clip.write_videofile(out.name)
                out.seek(0)
                return Video(bytes=out.read(), mime="video/mp4")


type VideoLike = Union[str, Path, Video]


def is_video_like(obj: Any) -> TypeGuard[VideoLike]:
    return isinstance(obj, (Video, str, Path))


@dataclass
class Image:
    bytes: bytes
    mime: str
    temporary_url: str | None = None

    def save(self, path: str | Path) -> "Image":
        """
        Save the video to a local file.
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(self.bytes)
        return self

    def __repr__(self) -> str:
        s = _get_human_readable_size(len(self.bytes))
        url = f", {self.temporary_url}" if self.temporary_url else ""
        return f"Image({self.mime}, {s}{url})"

    def get_pil_image(self) -> PIL.Image.Image:
        """
        Convert the bytes to a PIL Image.
        """
        return PIL.Image.open(BytesIO(self.bytes), formats=[self.mime.split("/")[1]])

    def show(self, *, small=False) -> "Image":
        w = 240 if small else None
        h = 135 if small else None
        display(
            IPImage(
                data=self.bytes,
                width=w,
                height=h,
            )
        )
        return self

    @staticmethod
    def load(path_or_url: "ImageLike") -> "Image":
        """
        Load an image from a file or URL.
        """
        if isinstance(path_or_url, Image):
            return path_or_url
        temporary_url = None
        if isinstance(path_or_url, PIL.Image.Image):
            image = path_or_url
            bytes = BytesIO()
            image.save(bytes, format=image.format or "PNG")
            bytes.seek(0)
            mime = (
                PIL.Image.MIME.get(image.format, "image/png")
                if image.format
                else "image/png"
            )
            bytes = bytes.getvalue()
        elif isinstance(path_or_url, Path) or not path_or_url.startswith("http"):
            path = Path(path_or_url)
            assert path.exists(), f"File not found: {path}"
            bytes = path.read_bytes()
            mime = PIL.Image.open(path).get_format_mimetype() or "image/png"
        else:
            temporary_url = path_or_url
            response = requests.get(path_or_url)
            response.raise_for_status()
            bytes = response.content
            mime = response.headers.get("Content-Type", "image/png")
        return Image(bytes=bytes, mime=mime, temporary_url=temporary_url)


type ImageLike = Union[str, Path, PIL.Image.Image, Image]


def is_image_like(obj: Any) -> TypeGuard[ImageLike]:
    return isinstance(obj, (Image, PIL.Image.Image, str, Path))


class Lora(BaseModel):
    path: str
    scale: float | None = 1.0

    @staticmethod
    def __from_str(s: str) -> "Lora":
        if s.startswith("civitai:"):
            parts = s.split(":")
            assert len(parts) in (2, 3), f"Invalid civitai lora format: {s}"
            model_id = parts[1]
            url = f"https://civitai-models.0xdead.dev/{model_id}"
            scale = float(parts[2]) if len(parts) == 3 else 1.0
            return Lora(path=url, scale=scale)
        else:
            return Lora(path=s)

    @staticmethod
    def process(loras: Sequence["LoraLike"]) -> list[dict[str, Any]]:
        result = []
        for lora in loras:
            if isinstance(lora, str):
                result.append(Lora.__from_str(lora))
            else:
                result.append(lora)
        return [result.model_dump() for result in result]


type LoraLike = Union[str, Lora]


class Script(BaseModel):
    title: str
    description: str
    content: str
    clips: list[str] = Field(default_factory=list)

    def dump(self):
        print("# Title:", self.title)
        print("---")
        print("# Description\n", self.description)
        print("---")
        for i, clip in enumerate(self.clips):
            print(f"# Clip {i + 1}\n", clip)
            print("---")

    def save(self, path: str | Path) -> "Script":
        path = Path(path)
        assert path.suffix == ".yaml", "Script must be saved as a .yaml file"
        path.parent.mkdir(parents=True, exist_ok=True)

        def str_representer(dumper, data):
            if len(data.splitlines()) > 1:  # check for multiline string
                return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
            return dumper.represent_scalar("tag:yaml.org,2002:str", data)

        doc = YAML()
        doc.representer.add_representer(str, str_representer)
        doc.default_flow_style = False
        with path.open("w+") as f:
            doc.dump(self.model_dump(), f)
        return self

    @staticmethod
    def load(path: str | Path) -> "Script":
        path = Path(path)
        assert path.exists(), f"File not found: {path}"
        assert path.suffix == ".yaml", "Script must be loaded from a .yaml file"
        with path.open("r") as f:
            data = YAML().load(f)
        return Script(**data)
