/**
 * API service for interacting with the backend
 */

const ApiService = {
  /**
   * Fetch all scenarios from the server
   * @returns {Promise} Promise resolving to scenarios data
   */
  getScenarios: function() {
    return fetch('/api/scenarios')
      .then(response => response.json())
      .catch(error => {
        console.error('Error loading scenarios:', error);
        throw error;
      });
  },

  /**
   * Add a new scenario
   * @param {string} scenarioName - The name of the scenario to add
   * @returns {Promise} Promise resolving to result data
   */
  addScenario: function(scenarioName) {
    return fetch('/api/scenarios', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name: scenarioName }),
    })
      .then(response => response.json())
      .catch(error => {
        console.error('Error adding scenario:', error);
        throw error;
      });
  },

  /**
   * Delete a scenario
   * @param {string} scenarioName - The name of the scenario to delete
   * @returns {Promise} Promise resolving to result data
   */
  deleteScenario: function(scenarioName) {
    return fetch(`/api/scenarios/${encodeURIComponent(scenarioName)}`, {
      method: 'DELETE',
    })
      .then(response => response.json())
      .catch(error => {
        console.error('Error deleting scenario:', error);
        throw error;
      });
  },

  /**
   * Start a new game
   * @param {string} scenario - The scenario to start
   * @returns {Promise} Promise resolving to initial game data
   */
  startGame: function(scenario) {
    return fetch('/api/start', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ scenario: scenario }),
    })
      .then(response => response.json())
      .catch(error => {
        console.error('Error starting game:', error);
        throw error;
      });
  },

  /**
   * Make a decision in the game
   * @param {string} sceneId - The current scene ID
   * @param {string} decisionId - The selected decision ID
   * @returns {Promise} Promise resolving to next scene data
   */
  makeDecision: function(sceneId, decisionId) {
    return fetch('/api/decision', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        scene_id: sceneId,
        decision: decisionId,
      }),
    })
      .then(response => response.json())
      .catch(error => {
        console.error('Error making decision:', error);
        throw error;
      });
  },

  /**
   * Get progress information
   * @returns {Promise} Promise resolving to progress data
   */
  getProgress: function() {
    return fetch('/api/progress')
      .then(response => response.json())
      .catch(error => {
        console.error('Error getting progress:', error);
        throw error;
      });
  },
  
  /**
   * Get the first frame preview for a scenario
   * @param {string} scenarioName - The name of the scenario
   * @returns {Promise} Promise resolving to preview data
   */
  getScenarioPreview: function(scenarioName) {
    return fetch(`/api/scenarios/${encodeURIComponent(scenarioName)}/preview`)
      .then(response => response.json())
      .catch(error => {
        console.error('Error getting scenario preview:', error);
        // Return a default preview
        return { preview_url: '/static/images/placeholder.jpg' };
      });
  }
}; 