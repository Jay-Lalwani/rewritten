/**
 * Scenario component for handling scenario management
 */

const ScenarioComponent = {
  scenarioContainer: null,
  newScenarioForm: null,

  /**
   * Initialize the scenario component
   */
  init: function() {
    this.scenarioContainer = Utils.getById('scenario-container');
    this.newScenarioForm = Utils.getById('new-scenario-form');
    this.initEventListeners();
    this.loadScenarios();
  },

  /**
   * Initialize event listeners
   */
  initEventListeners: function() {
    // New scenario form submission
    if (this.newScenarioForm) {
      this.newScenarioForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const scenarioNameInput = Utils.getById('new-scenario-name');
        const scenarioName = scenarioNameInput.value.trim();

        if (scenarioName) {
          this.addNewScenario(scenarioName);
          scenarioNameInput.value = '';
        }
      });
    }
  },

  /**
   * Load scenarios from the server
   */
  loadScenarios: function() {
    // Show loading state
    if (this.scenarioContainer) {
      this.scenarioContainer.innerHTML = '<div class="col-12 text-center"><p>Loading scenarios...</p></div>';

      // Fetch scenarios from the server
      ApiService.getScenarios()
        .then((data) => {
          // Clear container
          this.scenarioContainer.innerHTML = '';

          // Add each scenario
          data.scenarios.forEach((scenario) => {
            this.addScenarioCard(scenario);
          });
        })
        .catch(() => {
          this.scenarioContainer.innerHTML = '<div class="col-12 text-center"><p>Error loading scenarios. Please refresh the page.</p></div>';
        });
    }
  },

  /**
   * Add a scenario card to the UI
   * @param {string} scenario - The scenario name
   */
  addScenarioCard: function(scenario) {
    const scenarioCol = Utils.createElement('div', { className: 'col-lg-6 col-md-8 mb-4' });
    
    // Initial card structure
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
    const card = scenarioCol.querySelector('.scenario-card');
    card.addEventListener('click', function(e) {
      // Don't trigger if clicking the delete button
      if (!e.target.closest('.delete-scenario')) {
        const scenarioName = this.getAttribute('data-scenario');
        GameComponent.startGame(scenarioName);
      }
    });

    // Add delete event
    const deleteBtn = scenarioCol.querySelector('.delete-scenario');
    deleteBtn.addEventListener('click', (e) => {
      e.stopPropagation(); // Prevent the card click event
      const scenarioName = e.currentTarget.getAttribute('data-scenario');
      this.deleteScenario(scenarioName);
    });

    this.scenarioContainer.appendChild(scenarioCol);
    
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
  addNewScenario: function(scenarioName) {
    ApiService.addScenario(scenarioName)
      .then((data) => {
        if (data.success) {
          // Add new scenario card
          this.addScenarioCard(data.scenario);

          // Close the modal
          const modal = bootstrap.Modal.getInstance(document.getElementById('addScenarioModal'));
          if (modal) {
            modal.hide();
          }
        } else {
          alert(data.message || 'Scenario already exists');
        }
      })
      .catch(() => {
        alert('An error occurred while adding the scenario.');
      });
  },

  /**
   * Delete a scenario
   * @param {string} scenarioName - The name of the scenario to delete
   */
  deleteScenario: function(scenarioName) {
    if (confirm(`Are you sure you want to delete the "${scenarioName}" scenario?`)) {
      ApiService.deleteScenario(scenarioName)
        .then((data) => {
          if (data.success) {
            // Remove the card from the UI
            const scenarioCard = document.querySelector(`.scenario-card[data-scenario="${scenarioName}"]`);
            if (scenarioCard) {
              const scenarioCol = scenarioCard.closest('.col-lg-6');
              if (scenarioCol) {
                scenarioCol.remove();
              }
            }
          } else {
            alert(data.message || 'Failed to delete scenario');
          }
        })
        .catch(() => {
          alert('An error occurred while deleting the scenario.');
        });
    }
  }
}; 