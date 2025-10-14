def load_dotenv(env: dict[str, str] | None = None):
    import dotenv, os

    dotenv.load_dotenv()

    if env is not None:
        for k, v in env.items():
            os.environ[k] = str(v)


from . import image, video

try:
    import script
except ImportError:
    pass

from vision_spell.types import *

__all__ = [
    "image",
    "video",
    "script",
    "Image",
    "Video",
    "Script",
    "load_dotenv",
]
