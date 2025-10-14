import asyncio
from agentia import Agent
import nest_asyncio

from vision_spell.types import Script, ImageLike
from pydantic import BaseModel, Field


INSTRUCTIONS = """
You are an movie script writer. You will be given a brief description of the plot. Your task is to write a script for the movie or a video clip, including dialogue, scene descriptions, and any necessary actions. The script should be engaging, well-structured, and suitable for a feature-length film.

# Basics for writing prompts

Good prompts are descriptive and clear. To get your generated video closer to what you want, start with identifying your core idea and then refine your idea by adding keywords and modifiers.

The following elements should be included in your prompt:

Subject: The object, person, animal, or scenery that you want in your video.
Context: The background or context in which the subject is placed.
Action: What the subject is doing (for example, walking, running, or turning their head).
Style: This can be general or very specific. Consider using specific film style keywords, such as horror film, film noir, or animated styles like cartoon style render.
Camera motion: Optional: What the camera is doing, such as aerial view, eye-level, top-down shot, or low-angle shot.
Composition: Optional: How the shot is framed, such as wide shot, close-up, or extreme close-up.
Ambiance: Optional: How the color and light contribute to the scene, such as blue tones, night, or warm tones.
Audio: The background music, sound effects, or dialogue. Dialog should be written in the script format, with character names followed by their dialogue in quotes.

# More tips

Use descriptive language: Use adjectives and adverbs to paint a clear picture for Veo.

Provide context: If necessary, include background information to help your model understand what you want.

Reference specific artistic styles: If you have a particular aesthetic in mind, reference specific artistic styles or art movements.

Utilize prompt engineering tools: Consider exploring prompt engineering tools or resources to help you refine your prompts and achieve optimal results. For more information, see Introduction to prompting.

Enhance the facial details in your personal and group images: Specify facial details as a focus of the photo like using the word portrait in the prompt.

Clearly specify if you want audio. We recommend that you use separate sentences in your prompt to describe the audio.
"""

MODEL = "openai/gpt-4.1"


async def __script(
    description: str,
    clips: int = 1,
    dump=True,
    images: ImageLike | list[ImageLike] | None = None,
) -> Script:
    agent = Agent(model=MODEL, instructions=INSTRUCTIONS)
    duration = 8 * clips  # 8 seconds per clip
    prompt = f"""
    # NOW GENERATE A SCRIPT FOR A MOVIE BASED ON THE FOLLOWING DESCRIPTION
    # Just write the script itself, do not include any other text, no title, no description.
    # The duration of the video is {duration} seconds.

    ---

    {description}
    """
    run = agent.run(prompt, stream=True)
    content = ""
    async for stream in run:
        async for chunk in stream:
            print(chunk, end="", flush=True)
            content += chunk

    # Split into clips

    if clips > 1:
        f = Field(
            min_length=clips, max_length=clips, description="List of script clips"
        )

        class ClipsAndTitle(BaseModel):
            title: str = Field(description="The title of the whole script")
            clips: list[str] = f

        run = agent.run(
            f"""
            1. Generate a title for the overall script.
            2. Split the script into {clips} clips, each with a duration of {duration} seconds. Write a script for each clip. The clips should be connected and form a coherent story, with smooth transitions between them.
            """,
            response_format=ClipsAndTitle,
        )
        msg = await run
        cat = msg.cast(ClipsAndTitle)
        if dump:
            print("---")
            print("Title:", cat.title)
            print("---")
            for i, clip in enumerate(cat.clips):
                print(clip)
                print("---")
        clips_list = cat.clips
    else:

        class Title(BaseModel):
            title: str = Field(description="The title of the whole script")

        run = agent.run(
            "Generate a title for the overall script.", response_format=Title
        )
        msg = await run
        cat = msg.cast(Title)
        if dump:
            print("---")
            print("Title:", cat.title)
            print("---")
        clips_list = [content]

    return Script(
        title=cat.title,
        description=description,
        content=content,
        clips=clips_list,
    )


def script(
    description: str,
    clips: int = 1,
    dump=True,
    images: ImageLike | list[ImageLike] | None = None,
) -> Script:
    nest_asyncio.apply()
    return asyncio.run(__script(description, clips, dump, images))
