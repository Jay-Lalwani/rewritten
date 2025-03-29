# Rewritten Frontend Architecture

This document describes the frontend architecture of the Rewritten application, which is designed to be modular, extensible, and ready for integrations such as LMS (Learning Management Systems).

## Directory Structure

```
static/
├── css/            # CSS stylesheets
├── js/             # JavaScript files
│   ├── components/ # UI components
│   ├── services/   # API and external services
│   └── utils/      # Utility functions
├── images/         # Static images
└── videos/         # Video content
```

## HTML Structure

The application uses a template-based approach with Flask's Jinja2 templating system.

```
templates/
├── components/     # Reusable UI components
│   ├── header.html
│   ├── footer.html
│   ├── game-container.html
│   └── ...
├── layouts/        # Page layouts
│   └── base.html   # Base layout template
└── index.html      # Main entry page
```

## JavaScript Architecture

The JavaScript is organized into a modular structure to promote maintainability and extensibility:

1. **Components**: UI components with specific functionality
   - `scenario.js` - Manages scenario selection and creation
   - `game.js` - Handles the main game logic and UI

2. **Services**: API interactions and external service integrations
   - `api.js` - Communicates with the backend API

3. **Utils**: Helper functions and utilities
   - `index.js` - General utility functions

4. **App Entry Point**: 
   - `app.js` - Main application initialization and coordination

## Public API

The application exposes a public API through the `RewrittenApp` global object for external integrations, including:

- **Scenario Management**: Create, delete, and retrieve scenarios
- **Game Control**: Start games, retrieve current state
- **UI Controls**: Show/hide different application screens

## Extending the Application

To add new features:

1. **New Component**: Create a new JavaScript file in `js/components/` 
2. **HTML Templates**: Add any necessary HTML templates in `templates/components/`
3. **Service Integration**: Extend existing services or add new ones in `js/services/`
4. **Import in App**: Update the relevant imports and initialization in `app.js`

## LMS Integration

Future LMS integration should utilize the public API exposed through `RewrittenApp` and may involve:

1. Adding SCORM/xAPI support in a new service file
2. Extending authentication for LMS-based login
3. Adding progress tracking and reporting
4. Creating a connector service specific to the LMS platform

## CSS Organization

The CSS follows a component-based organization that matches the JavaScript and HTML structure. Consider breaking the main `styles.css` into component-specific files as the application grows. 