# Rewritten: AI-Powered Interactive Historical Adventure Game

An interactive game that lets players reshape history through their decisions, powered by AI-generated narratives and immersive media.

## Overview

"Rewritten" is an educational game that combines:
- AI-generated historical narratives with branching storylines
- Visual storytelling through AI-generated images and videos
- Interactive decision-making that impacts historical outcomes

Players experience pivotal historical moments like the Cuban Missile Crisis, making decisions that could rewrite history.

## Features

- **AI Story Generation**: Creates historically accurate scenarios with multiple decision paths
- **Dynamic Video Generation**: Produces visual representations of the narrative on-the-fly
- **Personalized Experience**: Each playthrough creates a unique storyline based on player choices
- **Educational Value**: Learn history by experiencing it in an immersive, interactive format

## Setup Instructions

### Prerequisites

- Python 3.11+
- API keys for:
  - Google Gemini API: For narrative and prompt generation
  - Replicate API: For image generation
  - RunwayML API: For video generation (optional - fake implementation included for demo)

### Installation

1. Set up environment variables in a `.env` file in the `rewritten` directory:

```
GEMINI_API_KEY=your_gemini_api_key
REPLICATE_API_TOKEN=your_replicate_api_token
RUNWAY_API_KEY=your_runway_api_key (optional)
SECRET_KEY=your_flask_secret_key
```

2. Install the required dependencies:

```bash
cd rewritten
pip install -r requirements.txt
# install ffmpeg
```

### Running the Application

1. Start the Flask application:

```bash
cd rewritten
python app.py
```

2. Open your web browser and navigate to:

```
http://localhost:5000
```

3. Choose a historical scenario and begin your adventure.

## Project Structure

- `app.py`: Main Flask application
- `api/`: Backend modules for AI integration
  - `writer_agent.py`: Generates historical narratives using Gemini 2.0
  - `producer_agent.py`: Creates visual prompts using Gemini 2.0
  - `media_generator.py`: Handles image and video generation
- `database/`: Database management
- `static/`: Frontend assets (CSS, JavaScript, images, videos)
- `templates/`: HTML templates
- `runwayml.py`: Placeholder implementation of the RunwayML client (for demo purposes)

## Usage

1. Select a historical scenario from the main screen
2. Watch the generated video that sets up the historical context
3. Read the narrative and choose from three possible decisions
4. See how your decisions affect the course of history
5. Track your decision path in the progress tracker

## Notes

This implementation uses:
- Google AI Client with Gemini 2.0 for text generation
- Replicate API for image generation
- A placeholder implementation of RunwayML for video generation in demo mode

## Model Simplification

The application has been simplified to remove the distinction between classes and assignments. Now:

- Teachers create assignments with a specific scenario
- Each assignment generates a unique access code
- Students join assignments directly using the access code
- All functionality related to creating/joining classes has been removed

### Applying the Model Changes

To apply these changes to an existing database:

1. Run the migration script:
   ```
   python reset_migration.py
   ```

This will:
- Reset the database with the simplified model
- Remove class-related tables and references
- Keep the core functionality intact for assignments and scenario selection

### Model Changes Overview

- Removed `Class` model and all related associations
- Simplified `Assignment` model to no longer reference classes
- Updated UI to focus solely on assignments
- Scenario selection is now done directly when creating an assignment

## License

MIT 