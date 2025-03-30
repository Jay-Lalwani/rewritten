import os
import json
import google.genai as genai
from dotenv import load_dotenv
from google.genai import types

# Load environment variables
load_dotenv()

# Configure Gemini API
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Producer Agent (Scene Prompt Generator) system prompt
PRODUCER_SYSTEM_PROMPT = """
You are the Visual Prompt Producer. Your role is to convert narrative text into two coherent scene prompts that will drive image and video generation. For each narrative input, generate two distinct scene descriptions with a clear emphasis on ACTION and DYNAMISM:

- A **first_frame_prompt**: A detailed self-contained description of the key image (first frame) for the scene.
- A **video_prompt**: A concise prompt describing a 5 second video clip that captures ONE MAIN ACTION - something visually engaging that happens in the scene.

Your output must be in valid JSON as follows:

{
  "scenes": [
    {
      "scene_id": 1,
      "first_frame_prompt": "<Detailed key image description>",
      "video_prompt": "<Concise video prompt>"
    },
    {
      "scene_id": 2,
      "first_frame_prompt": "<Detailed key image description>",
      "video_prompt": "<Concise video prompt>"
    }
  ]
}

IMPORTANT GUIDELINES:
1. The FIRST video (scene_id 1) should be thorough, provide background context, have all the subjects for the video, and establish the historical setting and perfectly describe the details of the image.
2. The SECOND video (scene_id 2) should directly relate to the decision that will need to be made, showing a key moment that leads to the choice.
3. Each video prompt must describe ONE CLEAR ACTION that happens - like "JFK signing a document" or "Soviet ships advancing toward the blockade line" - not just mood or atmosphere.
4. Ensure that each prompt is clear, self-contained, and provides all the necessary visual details without assuming external context. (Be literal, don't make assumptions)
5. KEEP VIDEO PROMPTS CONCISE AND SIMPLE TO UNDERSTAND.
6. Avoid special characters, aggressive language or nsfw prompts that specify violence or gore.
"""


def generate_scene_prompts(narrative_text):
    """
    Convert a narrative text into scene prompts for image and video generation.

    Args:
        narrative_text: The narrative text to convert

    Returns:
        JSON object with scene prompts
    """
    # Create a new chat with system instruction
    chat = client.chats.create(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(system_instruction=PRODUCER_SYSTEM_PROMPT),
    )

    prompt = f"""
    Narrative: {narrative_text}
    
    Convert this narrative into two distinct scene prompts for image and video generation.
    Each scene should have a first_frame_prompt and a video_prompt as specified.
    Remember that the first scene should establish context, the second scene should relate to the decision, and both video prompts must describe ONE CLEAR ACTION.
    """

    # Get response from Gemini
    response = chat.send_message(prompt)

    try:
        # Parse the response
        # Gemini might wrap the JSON in markdown code blocks, so we need to extract it
        content = response.text
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        scene_data = json.loads(content)

        # Print generated prompts
        print("\n=== GENERATED SCENE PROMPTS ===")
        for scene in scene_data["scenes"]:
            print(f"Scene {scene['scene_id']}:")
            print(f"  Image: {scene['first_frame_prompt']}")
            print(f"  Video: {scene['video_prompt']}")
        print("==============================\n")

        # Validate the response format
        assert "scenes" in scene_data
        assert len(scene_data["scenes"]) == 2
        for scene in scene_data["scenes"]:
            assert "scene_id" in scene
            assert "first_frame_prompt" in scene
            assert "video_prompt" in scene

        return scene_data

    except (json.JSONDecodeError, AssertionError) as e:
        # Fallback to a default response if the AI response is not valid
        return {
            "scenes": [
                {
                    "scene_id": 1,
                    "first_frame_prompt": f"Historical scene depicting {narrative_text}",
                    "video_prompt": f"Short video clip showing {narrative_text}",
                },
                {
                    "scene_id": 2,
                    "first_frame_prompt": f"Close-up of key figures involved in {narrative_text}",
                    "video_prompt": f"A dramatic moment showing a critical choice being made related to {narrative_text}",
                },
            ]
        }
