# Rewritten: Reshape History

An interactive historical narrative experience where users can explore how different decisions might have changed the course of history.

## Project Architecture

This project uses a hybrid architecture:
- **Flask Backend**: Handles AI-driven narrative generation, video generation, and database operations
- **Next.js Frontend**: Provides a modern, responsive user interface

## Prerequisites

- Node.js 18+ and npm
- Python 3.8+
- pip (Python package installer)
- Git

## Initial Setup

### Clone the Repository

```bash
git clone https://github.com/yourusername/rewritten.git
cd rewritten
```

### One-Command Setup

For a quick setup that installs both frontend and backend dependencies:

```bash
# Create and activate a Python virtual environment first
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Then run the setup command
npm run setup

# Initialize the database
npm run init-db
```

### Manual Setup (Alternative)

#### Backend Setup

1. Create and activate a Python virtual environment:

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

2. Install backend dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:

```bash
# Copy the example .env file
cp .env.example .env

# Edit the .env file with your configuration
# Particularly the API keys for narrative and media generation
```

4. Initialize the database:

```bash
npm run init-db
# OR
flask init-db
```

#### Frontend Setup

1. Install Node.js dependencies:

```bash
npm install
```

2. Configure frontend environment variables:

```bash
# Ensure .env.local exists with the Flask backend URL
echo "NEXT_PUBLIC_FLASK_API_URL=http://localhost:5000" > .env.local
```

## Project Structure

The project has a hybrid structure with both Next.js and Flask components:

- `/app.py`: Main Flask application
- `/database/`: Database management and models
- `/api/`: Python modules for AI narrative and media generation
  - `writer_agent.py`: Narrative generation
  - `producer_agent.py`: Scene prompt generation
  - `media_generator.py`: Video generation 
- `/static/`: Static assets for the Flask app
- `/templates/`: HTML templates for the Flask app
- `/src/`: Next.js application source
  - `/app/`: Next.js pages using App Router
  - `/components/`: React components
  - `/lib/`: Utility functions and API client

> **Important**: Ensure the `/api` directory exists with proper Python modules. The Flask backend imports from this directory.

## Running the Application

### Development Mode

To run both the Flask backend and Next.js frontend simultaneously:

```bash
npm run dev:all
```

This will start:
- Flask backend on http://localhost:5000
- Next.js frontend on http://localhost:3000

### Running Components Separately

To run the Next.js frontend only:

```bash
npm run dev
```

To run the Flask backend only:

```bash
npm run flask
# OR with debug mode
npm run flask -- --debug
```

## Application Features

### Scenario Management

- Create new historical scenarios
- Choose from existing scenarios
- Delete scenarios

### Interactive Narrative Experience

- Watch AI-generated videos representing historical moments
- Read generated narrative text
- Make decisions that alter the course of history
- Track your decision history throughout the scenario

## API Communication

The frontend communicates with the Flask backend via these key endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/scenarios` | GET | Retrieve available scenarios |
| `/api/scenarios` | POST | Create a new scenario |
| `/api/scenarios/:name` | DELETE | Delete a scenario |
| `/api/start` | POST | Start a new game session |
| `/api/decision` | POST | Make a decision in the current narrative |
| `/api/progress` | GET | Get the current game progress |

The Flask backend handles:
- Narrative generation using AI models
- Video generation and processing
- Game state management
- Session tracking

## Building for Production

### Frontend Build

```bash
npm run build
```

### Starting Production Servers

For the Next.js frontend:

```bash
npm run start
```

For the Flask backend, use a production WSGI server like Gunicorn:

```bash
gunicorn --bind 0.0.0.0:5000 app:app
```

## Troubleshooting

### Common Issues

1. **"ModuleNotFoundError: No module named 'api'"**:
   - Ensure the `/api` directory exists at the project root
   - Make sure it contains `__init__.py`, `writer_agent.py`, `producer_agent.py`, and `media_generator.py`
   - Verify that your Python virtualenv is activated

2. **Flask server doesn't start**:
   - Ensure the virtual environment is activated
   - Check that all required Python dependencies are installed
   - Verify that the required environment variables are set

3. **Next.js build fails**:
   - Check for TypeScript errors with `npm run lint`
   - Ensure all npm dependencies are installed
   - Verify the Next.js configuration

4. **API communication errors**:
   - Confirm that CORS is properly configured
   - Verify that the Flask backend URL is correct in .env.local
   - Check the browser console for detailed error messages

## License

[MIT License](LICENSE) 