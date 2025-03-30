/**
 * Scenario component for handling scenario management
 */

const ScenarioComponent = {
  scenarioContainer: null,
  newScenarioForm: null,

  /**
   * Initialize the scenario component
   */
  init: function () {
    console.log('ScenarioComponent init called');
    
    // Try to find the scenario container - may be in gallery or start screen
    this.scenarioContainer = Utils.getById("scenario-container");
    console.log('Direct scenario container found:', !!this.scenarioContainer);
    
    // If not found directly, try to find within gallery or start screen
    if (!this.scenarioContainer) {
      // First, try section-gallery (new structure)
      const gallerySection = document.getElementById('section-gallery');
      console.log('Gallery section found:', !!gallerySection);
      
      if (gallerySection) {
        // Look for gallery-screen within section-gallery
        const galleryScreen = gallerySection.querySelector('#gallery-screen');
        console.log('Gallery screen found within section:', !!galleryScreen);
        
        if (galleryScreen) {
          this.scenarioContainer = galleryScreen.querySelector('#scenario-container');
          console.log('Scenario container found in gallery section:', !!this.scenarioContainer);
        }
      }
      
      // If still not found, try old structure
      if (!this.scenarioContainer) {
        const galleryScreen = document.getElementById('gallery-screen');
        console.log('Gallery screen found in init:', !!galleryScreen);
        
        if (galleryScreen) {
          this.scenarioContainer = galleryScreen.querySelector('#scenario-container');
          console.log('Scenario container found in gallery:', !!this.scenarioContainer);
        }
        
        if (!this.scenarioContainer) {
          const startScreen = document.getElementById('start-screen');
          console.log('Start screen found:', !!startScreen);
          
          if (startScreen) {
            this.scenarioContainer = startScreen.querySelector('#scenario-container');
            console.log('Scenario container found in start screen:', !!this.scenarioContainer);
          }
        }
      }
    }
    
    this.newScenarioForm = Utils.getById("new-scenario-form");
    
    if (!this.newScenarioForm) {
      const modal = document.getElementById('addScenarioModal');
      if (modal) {
        this.newScenarioForm = modal.querySelector('#new-scenario-form');
      }
    }
    
    this.initEventListeners();
    
    // Only load scenarios if the container exists
    if (this.scenarioContainer) {
      this.loadScenarios();
    } else {
      console.warn('Scenario container not found, scenarios will not be loaded');
    }
  },

  /**
   * Initialize event listeners
   */
  initEventListeners: function () {
    // New scenario form submission
    if (this.newScenarioForm) {
      this.newScenarioForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const scenarioNameInput = Utils.getById("new-scenario-name");
        const scenarioName = scenarioNameInput.value.trim();

        if (scenarioName) {
          this.addNewScenario(scenarioName);
          scenarioNameInput.value = "";
        }
      });
    }
  },

  /**
   * Load scenarios from the server
   */
  loadScenarios: function () {
    console.log('loadScenarios called, container exists:', !!this.scenarioContainer);
    
    // Show loading state
    if (this.scenarioContainer) {
      this.scenarioContainer.innerHTML =
        '<div class="col-12 text-center"><p>Loading scenarios...</p></div>';

      // Fetch scenarios from the server
      ApiService.getScenarios()
        .then((data) => {
          console.log('Scenarios loaded:', data.scenarios ? data.scenarios.length : 'No scenarios array found');
          
          if (!data.scenarios || !Array.isArray(data.scenarios)) {
            console.error('Invalid scenarios data received:', data);
            this.scenarioContainer.innerHTML =
              '<div class="col-12 text-center"><p>Error: Invalid scenario data received.</p></div>';
            return;
          }
          
          // Clear container
          this.scenarioContainer.innerHTML = "";

          // Check if we have any scenarios
          if (data.scenarios.length === 0) {
            this.scenarioContainer.innerHTML =
              '<div class="col-12 text-center"><p>No scenarios found. Create a new one to get started.</p></div>';
            return;
          }

          // Add each scenario
          data.scenarios.forEach((scenario) => {
            this.addScenarioCard(scenario);
          });
        })
        .catch((error) => {
          console.error('Error loading scenarios:', error);
          this.scenarioContainer.innerHTML =
            '<div class="col-12 text-center"><p>Error loading scenarios. Please refresh the page.</p></div>';
        });
    } else {
      console.error('Cannot load scenarios: scenario container not found');
    }
  },

  /**
   * Add a scenario card to the UI
   * @param {string} scenario - The scenario name
   */
  addScenarioCard: function (scenario) {
    console.log('Adding scenario card for:', scenario);
    
    if (!this.scenarioContainer) {
      console.error('Cannot add scenario card: container not found');
      return;
    }
    
    // Check if container is visible and try to fix it if not
    const isVisible = this.scenarioContainer.offsetParent !== null;
    console.log('Container is visible:', isVisible, 'Parent element:', this.scenarioContainer.parentElement);
    
    if (!isVisible) {
      console.log('Container is not visible, attempting to fix...');
      
      // Force display on this container
      this.scenarioContainer.style.display = 'flex';
      this.scenarioContainer.style.visibility = 'visible';
      
      // Find the closest section-content ancestor and make it visible
      let parent = this.scenarioContainer.parentElement;
      while (parent) {
        if (parent.classList && parent.classList.contains('section-content')) {
          parent.style.display = 'block';
          parent.classList.add('active');
          console.log('Made section-content parent visible:', parent.id);
        }
        if (parent.id === 'gallery-screen') {
          parent.style.display = 'block';
          console.log('Made gallery-screen visible');
        }
        parent = parent.parentElement;
      }
    }
    
    const scenarioCol = Utils.createElement("div", {
      className: "col-lg-6 col-md-8 mb-4",
    });
    scenarioCol.innerHTML = `
      <div class="card scenario-card" data-scenario="${scenario}">
        <div class="card-subtitle">Historical Moment</div>
        <h5 class="card-title">${scenario}</h5>
        <div class="scenario-image-container">
          <div class="placeholder">
            <i class="fas fa-image placeholder-icon"></i>
            <span class="placeholder-text">Loading preview...</span>
          </div>
          <img src="" alt="${scenario}" class="scenario-image" style="display: none;">
        </div>
        <button class="btn btn-sm btn-danger delete-scenario" data-scenario="${scenario}">
          <i class="fas fa-trash-alt"></i>
        </button>
      </div>
    `;

    // Add click event to the scenario card
    const card = scenarioCol.querySelector(".scenario-card");
    card.addEventListener("click", function (e) {
      // Don't trigger if clicking the delete button
      if (!e.target.closest(".delete-scenario")) {
        const scenarioName = this.getAttribute("data-scenario");
        console.log('Scenario card clicked, starting game with:', scenarioName);
        
        try {
          // Direct navigation to game section with clean, simple approach
          document.querySelectorAll('.section-content').forEach(s => {
            s.style.display = 'none';
            s.classList.remove('active');
          });
          
          const gameSection = document.getElementById('section-game');
          if (gameSection) {
            gameSection.style.display = 'block';
            gameSection.classList.add('active');
          }
          
          // Start the game - let the GameComponent handle the rest
          if (typeof GameComponent.startGame === 'function') {
            GameComponent.startGame(scenarioName);
          } else {
            console.error('GameComponent.startGame is not a function');
          }
        } catch (error) {
          console.error('Error starting game:', error);
        }
      }
    });

    // Add delete event
    const deleteBtn = scenarioCol.querySelector(".delete-scenario");
    deleteBtn.addEventListener("click", (e) => {
      e.stopPropagation(); // Prevent the card click event
      const scenarioName = e.currentTarget.getAttribute("data-scenario");
      this.deleteScenario(scenarioName);
    });

    // Append to container and then verify it was added
    this.scenarioContainer.appendChild(scenarioCol);
    console.log('Scenario card added, container now has', this.scenarioContainer.children.length, 'children');
    
    // Force gallery section to be visible after adding scenarios
    const gallerySection = document.getElementById('section-gallery');
    if (gallerySection) {
      gallerySection.style.display = 'block';
      gallerySection.classList.add('active');
      
      // Hide all other sections
      const sections = document.querySelectorAll('.section-content');
      sections.forEach(section => {
        if (section !== gallerySection) {
          section.style.display = 'none';
          section.classList.remove('active');
        }
      });
      
      // Update sidebar active state
      const navItems = document.querySelectorAll('.sidebar-nav-item');
      navItems.forEach(nav => nav.classList.remove('active'));
      
      const galleryNavItem = document.querySelector('.sidebar-nav-item[data-section="gallery"]');
      if (galleryNavItem) {
        galleryNavItem.classList.add('active');
      }
    }
    
    // Check again if container is visible after our fixes
    const isNowVisible = this.scenarioContainer.offsetParent !== null;
    console.log('Container is now visible:', isNowVisible);
    
    // Force a redraw of the container
    this.scenarioContainer.style.display = 'none';
    setTimeout(() => {
      this.scenarioContainer.style.display = 'flex';
      console.log('Forced redraw of scenario container');
    }, 50);

    // Fetch scenario preview image
    ApiService.getScenarioPreview(scenario)
      .then(data => {
        if (data && data.preview_url) {
          const imgElement = card.querySelector('.scenario-image');
          const placeholder = card.querySelector('.placeholder');
          
          if (imgElement) {
            // Set up image onload event to hide placeholder when image loads
            imgElement.onload = function() {
              if (placeholder) placeholder.style.display = 'none';
              imgElement.style.display = 'block';
            };
            
            // Set the image source to trigger loading
            imgElement.src = data.preview_url;
            
            // If image fails to load, show error in placeholder
            imgElement.onerror = function() {
              if (placeholder) {
                const icon = placeholder.querySelector('.placeholder-icon');
                const text = placeholder.querySelector('.placeholder-text');
                if (icon) icon.className = 'fas fa-exclamation-circle placeholder-icon';
                if (text) text.textContent = 'Preview unavailable';
              }
            };
          }
        }
      })
      .catch(err => {
        console.log('Could not load preview for scenario:', scenario, err);
        const placeholder = card.querySelector('.placeholder');
        if (placeholder) {
          const icon = placeholder.querySelector('.placeholder-icon');
          const text = placeholder.querySelector('.placeholder-text');
          if (icon) icon.className = 'fas fa-exclamation-circle placeholder-icon';
          if (text) text.textContent = 'Preview unavailable';
        }
      });
  },

  /**
   * Add a new scenario
   * @param {string} scenarioName - The name of the new scenario
   */
  addNewScenario: function (scenarioName) {
    ApiService.addScenario(scenarioName)
      .then((data) => {
        if (data.success) {
          // Add new scenario card
          this.addScenarioCard(data.scenario);

          // Close the modal
          const modal = bootstrap.Modal.getInstance(
            document.getElementById("addScenarioModal"),
          );
          if (modal) {
            modal.hide();
          }
        } else {
          alert(data.message || "Scenario already exists");
        }
      })
      .catch(() => {
        alert("An error occurred while adding the scenario.");
      });
  },

  /**
   * Delete a scenario
   * @param {string} scenarioName - The name of the scenario to delete
   */
  deleteScenario: function (scenarioName) {
    if (
      confirm(`Are you sure you want to delete the "${scenarioName}" scenario?`)
    ) {
      ApiService.deleteScenario(scenarioName)
        .then((data) => {
          if (data.success) {
            // Remove the card from the UI
            const scenarioCard = document.querySelector(
              `.scenario-card[data-scenario="${scenarioName}"]`,
            );
            if (scenarioCard) {
              const scenarioCol = scenarioCard.closest(".col-lg-6");
              if (scenarioCol) {
                scenarioCol.remove();
              }
            } else {
              // If the card wasn't found in the main document, try finding it within sections
              const galleryScreen = document.getElementById('gallery-screen');
              if (galleryScreen) {
                const card = galleryScreen.querySelector(
                  `.scenario-card[data-scenario="${scenarioName}"]`,
                );
                if (card) {
                  const col = card.closest(".col-lg-6");
                  if (col) {
                    col.remove();
                  }
                }
              }
              
              const startScreen = document.getElementById('start-screen');
              if (startScreen) {
                const card = startScreen.querySelector(
                  `.scenario-card[data-scenario="${scenarioName}"]`,
                );
                if (card) {
                  const col = card.closest(".col-lg-6");
                  if (col) {
                    col.remove();
                  }
                }
              }
            }
          } else {
            alert(data.message || "Failed to delete scenario");
          }
        })
        .catch(() => {
          alert("An error occurred while deleting the scenario.");
        });
    }
  },
};
