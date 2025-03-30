/**
 * Main application entry point
 */

// Initialize application when DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
  // Initialize components
  GameComponent.init();
  ScenarioComponent.init();
  QuizComponent.init();

  // Set up any additional event listeners or app-wide functionality
  setupAppEventListeners();

  // Check for LMS integration if available
  checkLMSIntegration();
});

/**
 * Set up application-wide event listeners
 */
function setupAppEventListeners() {
  // Add any global event listeners here
  // This can be used to handle application-wide events

  // Example: Close modal on escape key
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      const openModals = document.querySelectorAll(".modal.show");
      openModals.forEach((modal) => {
        const modalInstance = bootstrap.Modal.getInstance(modal);
        if (modalInstance) {
          modalInstance.hide();
        }
      });
    }
  });
}

/**
 * Check for LMS integration
 * This is a placeholder for future LMS integration code
 */
function checkLMSIntegration() {
  // This function will be expanded in the future to handle LMS integration
  console.log("Ready for future LMS integration");

  // Will contain code to:
  // 1. Initialize LMS API connection
  // 2. Fetch user data from LMS
  // 3. Set up progress tracking to LMS
  // 4. Handle authentication with LMS
}

/**
 * Public API for external integrations
 * This exposes a clean interface for LMS or other systems to interact with the application
 */
const RewrittenApp = {
  // Scenario management
  scenarios: {
    getAll: () => ApiService.getScenarios(),
    create: (name) => ScenarioComponent.addNewScenario(name),
    delete: (name) => ScenarioComponent.deleteScenario(name),
  },

  // Game management
  game: {
    start: (scenario) => GameComponent.startGame(scenario),
    getCurrentState: () => ({
      currentScene: GameComponent.currentScene,
      decisions: GameComponent.decisions,
    }),
    getProgress: () => ApiService.getProgress(),
  },

  // UI controls
  ui: {
    showGame: () => {
      Utils.hideElement(GameComponent.startScreen);
      Utils.hideElement(GameComponent.loadingScreen);
      Utils.showElement(GameComponent.gameContainer);
    },
    showStartScreen: () => {
      Utils.hideElement(GameComponent.gameContainer);
      Utils.hideElement(GameComponent.loadingScreen);
      Utils.showElement(GameComponent.startScreen);
    },
    showLoading: () => {
      Utils.hideElement(GameComponent.startScreen);
      Utils.hideElement(GameComponent.gameContainer);
      Utils.showElement(GameComponent.loadingScreen);
    },
  },
};

// Expose the API to the window object for external access
window.RewrittenApp = RewrittenApp;
