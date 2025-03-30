import os
import json
import random
import google.genai as genai
from dotenv import load_dotenv
from google.genai import types
import re

# Load environment variables
load_dotenv()

# Configure Gemini API
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Quiz Agent system prompt
QUIZ_SYSTEM_PROMPT = """
You are the Historical Quiz Agent. Your task is to generate historically accurate and educational multiple-choice questions related to the given historical scenario or narrative.

For each request, generate a multiple choice question with exactly three options. Your output must be valid JSON in the following format:

{
  "question": "<clear, concise historical question>",
  "options": [
    {"id": "a", "text": "<option text>"},
    {"id": "b", "text": "<option text>"},
    {"id": "c", "text": "<option text>"}
  ],
  "correct_option_id": "<a, b, or c>",
  "explanation": "<brief explanation of the correct answer>"
}

IMPORTANT GUIDELINES:
1. Questions should be factual and educational about real historical events
2. Options should be plausible but only one should be correct
3. The explanation should briefly educate the user about the correct answer
4. Focus on important historical facts, figures, dates, or consequences
5. Ensure questions are clear, concise, and engaging
6. Make questions moderately challenging but not obscure
7. Do not include trailing commas in JSON arrays or objects
"""

def clean_json_string(json_str):
    """
    Clean a JSON string to remove common formatting issues like trailing commas.
    """
    # Remove trailing commas in arrays and objects
    json_str = re.sub(r',\s*}', '}', json_str)
    json_str = re.sub(r',\s*]', ']', json_str)
    
    return json_str

def generate_quiz_question(scenario=None, narrative=None):
    """
    Generate a historical quiz question related to the given scenario or narrative.

    Args:
        scenario: The historical scenario (e.g., "Cuban Missile Crisis")
        narrative: The current narrative text (optional)

    Returns:
        JSON object with the quiz question
    """

    # Create a new chat with system instruction
    chat = client.chats.create(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(system_instruction=QUIZ_SYSTEM_PROMPT),
    )

    # Build prompt based on available context
    if narrative:
        prompt = f"""
        Generate a multiple-choice quiz question related to the following historical narrative:
        {narrative}
        
        Focus on testing knowledge about important elements from this historical context.
        """
    elif scenario:
        prompt = f"""
        Generate a multiple-choice quiz question about the '{scenario}' historical event.
        Focus on testing knowledge about key facts, figures, or consequences of this event.
        """
    else:
        prompt = """
        Generate a general historical multiple-choice quiz question about a significant 
        historical event, person, or development.
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

        # Clean the JSON string before parsing
        cleaned_content = clean_json_string(content)
        
        # Parse the JSON
        question_data = json.loads(cleaned_content)

        # Validate the response format
        assert "question" in question_data
        assert "options" in question_data
        assert "correct_option_id" in question_data
        assert "explanation" in question_data
        assert len(question_data["options"]) == 3

        # Add an ID to the question
        question_data["id"] = f"q{random.randint(1000, 9999)}"

        return question_data

    except (json.JSONDecodeError, AssertionError) as e:
        print(f"Error generating quiz question: {e}")
        print(f"Raw response: {response.text}")

        # Fallback to a default question if the AI response is not valid
        return {
            "id": f"q{random.randint(1000, 9999)}",
            "question": f"Which historical event is related to {scenario or 'world history'}?",
            "options": [
                {"id": "a", "text": "The signing of the Magna Carta"},
                {"id": "b", "text": "The Cuban Missile Crisis"},
                {"id": "c", "text": "The Fall of the Berlin Wall"},
            ],
            "correct_option_id": "b",
            "explanation": "The Cuban Missile Crisis was a 13-day confrontation between the United States and Soviet Union in October 1962.",
        }


# Fallback questions in case API calls fail
FALLBACK_QUESTIONS = [
    {
        "id": "q1",
        "question": "Which year did the Cuban Missile Crisis occur?",
        "options": [
            {"id": "a", "text": "1960"},
            {"id": "b", "text": "1962"},
            {"id": "c", "text": "1964"},
        ],
        "correct_option_id": "b",
        "explanation": "The Cuban Missile Crisis occurred in October 1962 when the Soviet Union placed nuclear missiles in Cuba.",
    },
    {
        "id": "q2",
        "question": "Who was the U.S. President during the Cuban Missile Crisis?",
        "options": [
            {"id": "a", "text": "Dwight D. Eisenhower"},
            {"id": "b", "text": "John F. Kennedy"},
            {"id": "c", "text": "Lyndon B. Johnson"},
        ],
        "correct_option_id": "b",
        "explanation": "John F. Kennedy was the 35th President of the United States during the Cuban Missile Crisis.",
    },
]


def get_fallback_question():
    """Return a random fallback question if API generation fails."""
    return random.choice(FALLBACK_QUESTIONS)
