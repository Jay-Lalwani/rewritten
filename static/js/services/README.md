# Service Modules

This directory contains service modules that handle API communication and other external integrations.

## Current Services

- **api.js**: Handles all API communication with the server

## Planned Services for LMS Integration

When implementing LMS integration, consider creating the following service modules:

### 1. LMS Connector (`lms-connector.js`)

```javascript
/**
 * LMS Connector Service
 * Handles communication with Learning Management Systems
 */
const LMSConnector = {
  /**
   * Initialize connection to the LMS
   * @returns {Promise} Promise resolving when connection is established
   */
  initialize: function() {
    // Implementation depends on LMS API (SCORM, xAPI, LTI, etc.)
  },
  
  /**
   * Get learner information from the LMS
   * @returns {Promise} Promise resolving to user data
   */
  getLearnerInfo: function() {
    // Implementation
  },
  
  /**
   * Report progress to the LMS
   * @param {Object} progressData - Progress data to report
   * @returns {Promise} Promise resolving when data is reported
   */
  reportProgress: function(progressData) {
    // Implementation
  },
  
  /**
   * Terminate the LMS connection
   * @returns {Promise} Promise resolving when connection is terminated
   */
  terminate: function() {
    // Implementation
  }
};
```

### 2. Authentication Service (`auth-service.js`)

```javascript
/**
 * Authentication Service
 * Handles user authentication with the backend and LMS
 */
const AuthService = {
  /**
   * Get current user information
   * @returns {Promise} Promise resolving to user data
   */
  getCurrentUser: function() {
    // Implementation
  },
  
  /**
   * Check if user is authenticated
   * @returns {boolean} True if user is authenticated
   */
  isAuthenticated: function() {
    // Implementation
  },
  
  /**
   * Login user with credentials
   * @param {Object} credentials - User credentials
   * @returns {Promise} Promise resolving when user is logged in
   */
  login: function(credentials) {
    // Implementation
  },
  
  /**
   * Logout user
   * @returns {Promise} Promise resolving when user is logged out
   */
  logout: function() {
    // Implementation
  }
};
```

### 3. Progress Tracking Service (`progress-service.js`)

```javascript
/**
 * Progress Tracking Service
 * Handles tracking and reporting user progress
 */
const ProgressService = {
  /**
   * Track a user action
   * @param {Object} action - The action to track
   * @returns {Promise} Promise resolving when action is tracked
   */
  trackAction: function(action) {
    // Implementation
  },
  
  /**
   * Get user progress
   * @returns {Promise} Promise resolving to progress data
   */
  getProgress: function() {
    // Implementation
  },
  
  /**
   * Save progress to server and LMS
   * @returns {Promise} Promise resolving when progress is saved
   */
  saveProgress: function() {
    // Implementation
  }
};
```

## Integration Guidelines

When implementing new services:

1. Follow the module pattern used in existing services
2. Expose a clear public API
3. Handle errors gracefully
4. Log important events
5. Integrate with the `RewrittenApp` global object
6. Use promises for asynchronous operations 