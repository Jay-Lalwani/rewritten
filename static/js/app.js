/**
 * Main application entry point
 */

// Initialize application when DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
  // Check if this is the /view-scenarios page
  const currentPath = window.location.pathname;
  if (currentPath === '/view-scenarios') {
    console.log('On view-scenarios page, special handling required');
    
    // Delay initialization to ensure DOM is ready
    setTimeout(() => {
      // Initialize components
      console.log('Initializing components on view-scenarios page');
      GameComponent.init();
      ScenarioComponent.init();
      TeacherDashboardComponent.init();
      QuizComponent.init();
      
      // Set up any additional event listeners or app-wide functionality
      setupAppEventListeners();
      
      // Initialize navigation
      initNavigation();
      
      // Use direct DOM manipulation to force gallery to be active
      console.log('Forcing gallery section to be active for view-scenarios page');
      forceGalleryActive();
      
      // Initialize scenarios after a short delay
      setTimeout(() => {
        console.log('Starting scenario initialization after delay');
        initScenarios();
      }, 200);
    }, 100);
  } else {
    // Normal initialization for other pages
    console.log('Normal initialization for page:', currentPath);
    // Initialize components
    GameComponent.init();
    ScenarioComponent.init();
    TeacherDashboardComponent.init();
    
    QuizComponent.init();

    // Set up any additional event listeners or app-wide functionality
    setupAppEventListeners();

    // Check for LMS integration if available
    checkLMSIntegration();
    
    // Initialize navigation
    initNavigation();
    
    // Initialize scenarios if gallery section is active
    const gallerySection = document.getElementById('section-gallery');
    if (gallerySection && gallerySection.classList.contains('active')) {
      initScenarios();
    }
  }
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

// Initialize navigation between sections
function initNavigation() {
  const navItems = document.querySelectorAll('.sidebar-nav-item');
  
  navItems.forEach(item => {
    item.addEventListener('click', function(e) {
      e.preventDefault(); // Prevent default action if it's a link
      
      console.log('Nav item clicked:', this.getAttribute('data-section'));
      
      // Remove active class from all nav items
      navItems.forEach(nav => nav.classList.remove('active'));
      
      // Add active class to clicked item
      this.classList.add('active');
      
      // Hide all sections using direct style setting
      const sections = document.querySelectorAll('.section-content');
      sections.forEach(section => {
        section.style.display = 'none';
        section.classList.remove('active');
      });
      
      // Show the selected section
      const targetSection = this.getAttribute('data-section');
      const targetElement = document.getElementById(`section-${targetSection}`);
      
      if (targetElement) {
        targetElement.style.display = 'block';
        targetElement.classList.add('active');
        console.log('Activated section:', targetElement.id);
        
        // Initialize scenarios if gallery section becomes active
        if (targetSection === 'gallery') {
          console.log('Gallery section activated via navigation, initializing scenarios');
          // Wait a little for DOM to update
          setTimeout(() => {
            initScenarios();
          }, 100);
        }
      } else {
        console.warn(`Section with ID section-${targetSection} not found`);
      }
    });
  });
}

// Initialize scenarios (stub function - implement based on your existing code)
function initScenarios() {
  // Call existing scenario loading function
  console.log('initializing scenarios');
  
  // Debug HTML structure
  const gallerySection = document.getElementById('section-gallery');
  console.log('Gallery section found:', !!gallerySection);
  
  if (gallerySection) {
    console.log('Gallery section class list:', gallerySection.classList);
    // Make sure the gallery section is active
    const sections = document.querySelectorAll('.section-content');
    sections.forEach(section => section.classList.remove('active'));
    gallerySection.classList.add('active');
    
    // Update sidebar active state
    const navItems = document.querySelectorAll('.sidebar-nav-item');
    navItems.forEach(nav => nav.classList.remove('active'));
    
    const galleryNavItem = document.querySelector('.sidebar-nav-item[data-section="gallery"]');
    if (galleryNavItem) {
      galleryNavItem.classList.add('active');
    }
    
    const galleryScreen = gallerySection.querySelector('#gallery-screen');
    console.log('Gallery screen found:', !!galleryScreen);
    
    if (galleryScreen) {
      const scenarioContainer = galleryScreen.querySelector('#scenario-container');
      console.log('Scenario container found:', !!scenarioContainer);
      
      if (scenarioContainer) {
        console.log('Scenario container display style:', window.getComputedStyle(scenarioContainer).display);
        console.log('Scenario container visibility:', window.getComputedStyle(scenarioContainer).visibility);
      }
    }
  }
  
  // Force a reload of scenarios - this will use the updated scenario container logic
  if (typeof ScenarioComponent.init === 'function') {
    // Re-initialize to find the right container
    ScenarioComponent.init();
  } else if (typeof ScenarioComponent.loadScenarios === 'function') {
    ScenarioComponent.loadScenarios();
  }
  
  // Add event delegation for scenario card clicks
  const scenarioContainer = findScenarioContainer();
  
  if (scenarioContainer) {
    // Remove existing event listeners to prevent duplicates
    const oldContainer = scenarioContainer.cloneNode(true);
    scenarioContainer.parentNode.replaceChild(oldContainer, scenarioContainer);
    
    // Add new event listener to the fresh clone
    oldContainer.addEventListener('click', function(e) {
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
          
          const gameSection = document.getElementById('section-game');
          if (gameSection) {
            gameSection.classList.add('active');
            
            // Update sidebar active state
            const navItems = document.querySelectorAll('.sidebar-nav-item');
            navItems.forEach(nav => nav.classList.remove('active'));
            
            const gameNavItem = document.querySelector('.sidebar-nav-item[data-section="game"]');
            if (gameNavItem) {
              gameNavItem.classList.add('active');
            }
          }
          
          // Start the game
          GameComponent.startGame(scenarioName);
        }
      }
    });
  } else {
    console.warn('No scenario container found to attach click events');
  }
}

// Helper function to find the scenario container in the nested structure
function findScenarioContainer() {
  let container = document.getElementById('scenario-container');
  
  if (!container) {
    // Try to find within section-gallery (new structure)
    const gallerySection = document.getElementById('section-gallery');
    if (gallerySection) {
      const galleryScreen = gallerySection.querySelector('#gallery-screen');
      if (galleryScreen) {
        container = galleryScreen.querySelector('#scenario-container');
      }
    }
    
    // If still not found, try the old structure
    if (!container) {
      const galleryScreen = document.getElementById('gallery-screen');
      if (galleryScreen) {
        container = galleryScreen.querySelector('#scenario-container');
      }
      
      if (!container) {
        const startScreen = document.getElementById('start-screen');
        if (startScreen) {
          container = startScreen.querySelector('#scenario-container');
        }
      }
    }
  }
  
  return container;
}

/**
 * Force the gallery section to be active
 */
function forceGalleryActive() {
  console.log('Forcing gallery section to be active');
  
  // Use direct DOM manipulation
  const allSections = document.querySelectorAll('.section-content');
  allSections.forEach(section => {
    section.style.display = 'none';
    section.classList.remove('active');
  });
  
  const gallerySection = document.getElementById('section-gallery');
  if (gallerySection) {
    // Force display block on ALL parent elements
    let element = gallerySection;
    while (element) {
      if (element.style) {
        element.style.display = 'block';
      }
      element = element.parentElement;
    }
    
    gallerySection.style.display = 'block';
    gallerySection.classList.add('active');
    
    // Also force display on all important children
    const galleryScreen = gallerySection.querySelector('#gallery-screen');
    if (galleryScreen) {
      galleryScreen.style.display = 'block';
      
      const scenarioContainer = galleryScreen.querySelector('#scenario-container');
      if (scenarioContainer) {
        scenarioContainer.style.display = 'flex';
        scenarioContainer.style.visibility = 'visible';
      }
    }
    
    console.log('Gallery section set to active and displayed');
    console.log('Gallery section offsetParent:', gallerySection.offsetParent);
    if (galleryScreen) {
      console.log('Gallery screen offsetParent:', galleryScreen.offsetParent);
      if (scenarioContainer) {
        console.log('Scenario container offsetParent:', scenarioContainer.offsetParent);
      }
    }
  } else {
    console.error('Gallery section not found');
  }
  
  // Update sidebar
  const navItems = document.querySelectorAll('.sidebar-nav-item');
  navItems.forEach(nav => nav.classList.remove('active'));
  
  const galleryNavItem = document.querySelector('.sidebar-nav-item[data-section="gallery"]');
  if (galleryNavItem) {
    galleryNavItem.classList.add('active');
    console.log('Gallery nav item set to active');
  }
}
