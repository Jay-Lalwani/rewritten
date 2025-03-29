import os
import json
import google.genai as genai
from dotenv import load_dotenv
from google.genai import types

# Load environment variables
load_dotenv()

# Configure Gemini API
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Writer Agent (Historical Narrative Generator) system prompt
WRITER_SYSTEM_PROMPT = """
You are the Historical Narrative Agent. Your task is to generate fast-paced, intense, historically accurate scenarios and branching narratives based on player decisions. For each decision point, produce a concise narrative that sets the historical context and then present exactly three decision options. Your output must be valid JSON in the following format:

{
  "scene_id": <integer>,
  "narrative": "<historically accurate description with context>",
  "options": [
      { "id": "1", "option": "<Option Text>" },
      { "id": "2", "option": "<Option Text>" },
      { "id": "3", "option": "<Option Text>" }
  ]
}

IMPORTANT GUIDELINES:
1. Each decision option should present a clear and DISTINCT path forward.
2. All options should feel consequential and change the course of events significantly.

Your narratives should make the player feel they're at the center of a fast-moving historical situation, while remaining informative from a learning perspective.
"""

def generate_narrative(previous_narrative, decision_id, scenario=None):
    """
    Generate a historical narrative based on previous state and decision.
    
    Args:
        previous_narrative: The previous narrative state (None for initial state)
        decision_id: The ID of the decision made by the user (None for initial state)
        scenario: The historical scenario to generate (e.g., "Cuban Missile Crisis")
        
    Returns:
        JSON object with the new narrative state
    """
    
    # Create a new chat with system instruction
    chat = client.chats.create(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction=WRITER_SYSTEM_PROMPT
        )
    )
    
    if previous_narrative is None:
        # Initial narrative generation
        prompt = f"Generate the initial scenario for '{scenario}'. Focus on the first critical decision point with high tension and urgency."
    else:
        # Generate continuation based on previous narrative and decision
        option_text = next((opt["option"] for opt in previous_narrative["options"] if opt["id"] == decision_id), "")
        prompt = f"""
        Previous narrative: {previous_narrative['narrative']}
        Player's decision: {option_text}
        
        Generate the next fast-paced narrative segment and three new decision options. 
        Keep it brief and impactful - focus on the immediate consequences and the next critical choice.
        """
    
    # Get response from Gemini
    response = chat.send_message(prompt)
    
    try:
        # Parse the response
        content = response.text
        
        # Extract JSON from the response (may be wrapped in markdown code blocks)
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        # Parse the JSON
        narrative_data = json.loads(content)
        
        # Validate the response format
        assert "scene_id" in narrative_data
        assert "narrative" in narrative_data
        assert "options" in narrative_data
        assert len(narrative_data["options"]) == 3
        
        return narrative_data
    
    except (json.JSONDecodeError, AssertionError) as e:
        print(f"Error generating narrative: {e}")
        print(f"Raw response: {response.text}")
        
        # Fallback to a default response if the AI response is not valid
        scene_id = 1 if previous_narrative is None else previous_narrative["scene_id"] + 1
        
        return {
            "scene_id": scene_id,
            "narrative": f"A critical moment in the {scenario or 'historical'} scenario unfolds. Time for a quick decision.",
            "options": [
                {"id": "1", "option": "Take immediate action"},
                {"id": "2", "option": "Consult with advisors first"},
                {"id": "3", "option": "Consider an alternative approach"}
            ]
        } 