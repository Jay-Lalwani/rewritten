/**
 * Main application entry point
 */

// Initialize application when DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
  // Initialize components
  GameComponent.init();
  ScenarioComponent.init();
  TeacherDashboardComponent.init();
  
  // Set up any additional event listeners or app-wide functionality
  setupAppEventListeners();
  
  // Check for LMS integration if available
  checkLMSIntegration();
  
  // Initialize navigation
  initNavigation();
  
  // Initialize scenarios (if on gallery page)
  if (document.getElementById('gallery-screen').closest('.section-content').classList.contains('active')) {
    initScenarios();
  }
});

/**
 * Set up application-wide event listeners
 */
function setupAppEventListeners() {
  // Add any global event listeners here
  // This can be used to handle application-wide events
  
  // Example: Close modal on escape key
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      const openModals = document.querySelectorAll('.modal.show');
      openModals.forEach(modal => {
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
  console.log('Ready for future LMS integration');
  
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
    delete: (name) => ScenarioComponent.deleteScenario(name)
  },
  
  // Game management
  game: {
    start: (scenario) => GameComponent.startGame(scenario),
    getCurrentState: () => ({
      currentScene: GameComponent.currentScene,
      decisions: GameComponent.decisions
    }),
    getProgress: () => ApiService.getProgress()
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
    }
  }
};

// Expose the API to the window object for external access
window.RewrittenApp = RewrittenApp;

// Initialize navigation between sections
function initNavigation() {
  const navItems = document.querySelectorAll('.sidebar-nav-item');
  
  navItems.forEach(item => {
    item.addEventListener('click', function() {
      // Remove active class from all nav items
      navItems.forEach(nav => nav.classList.remove('active'));
      
      // Add active class to clicked item
      this.classList.add('active');
      
      // Hide all sections
      const sections = document.querySelectorAll('.section-content');
      sections.forEach(section => section.classList.remove('active'));
      
      // Show the selected section
      const targetSection = this.getAttribute('data-section');
      document.getElementById(`section-${targetSection}`).classList.add('active');
      
      // Initialize scenarios if gallery section becomes active
      if (targetSection === 'gallery') {
        initScenarios();
      }
    });
  });
}

// Initialize scenarios (stub function - implement based on your existing code)
function initScenarios() {
  // Call existing scenario loading function
  if (typeof ScenarioComponent.loadScenarios === 'function') {
    ScenarioComponent.loadScenarios();
    
    // Add event delegation for scenario card clicks
    const scenarioContainer = document.getElementById('scenario-container');
    if (scenarioContainer) {
      scenarioContainer.addEventListener('click', function(e) {
        const scenarioCard = e.target.closest('.scenario-card');
        // Only process if clicking on the card and not on delete button
        if (scenarioCard && !e.target.closest('.delete-scenario')) {
          e.preventDefault();
          const scenarioName = scenarioCard.getAttribute('data-scenario');
          
          // Start the game with this scenario
          if (typeof GameComponent.startGame === 'function') {
            // Switch to game section
            const sections = document.querySelectorAll('.section-content');
            sections.forEach(section => section.classList.remove('active'));
            document.getElementById('section-game').classList.add('active');
            
            // Update sidebar active state
            const navItems = document.querySelectorAll('.sidebar-nav-item');
            navItems.forEach(nav => nav.classList.remove('active'));
            
            // Start the game
            GameComponent.startGame(scenarioName);
          }
        }
      });
    }
  }
}
