import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get ElevenLabs API key from environment variables
ELEVEN_LABS_API_KEY = os.environ.get("ELEVEN_LABS_API_KEY")

def generate_speech(text, voice_id="21m00Tcm4TlvDq8ikWAM"):
    """
    Generate speech using ElevenLabs API
    
    Args:
        text: The text to convert to speech
        voice_id: The voice ID to use (default is 'Rachel')
        
    Returns:
        URL to the generated audio file or None if generation failed
    """
    
    if not ELEVEN_LABS_API_KEY:
        print("Error: ELEVEN_LABS_API_KEY not found in environment variables")
        return None
        
    try:
        # API endpoint for text-to-speech
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        # Headers with API key
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVEN_LABS_API_KEY
        }
        
        # Request data
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5,
                "speed": 1.2
            }
        }
        
        # Make the API request
        response = requests.post(url, json=data, headers=headers)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Save the audio file
            static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'audio')
            os.makedirs(static_dir, exist_ok=True)
            
            # Generate a unique filename
            from uuid import uuid4
            filename = f"{uuid4()}.mp3"
            filepath = os.path.join(static_dir, filename)
            
            # Save the audio
            with open(filepath, "wb") as f:
                f.write(response.content)
            
            print(f"Audio generated successfully: {filepath}")
            return f"/static/audio/{filename}"
        else:
            print(f"Error generating audio: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"Error in TTS generation: {e}")
        return None 