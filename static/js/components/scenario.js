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
    this.scenarioContainer = Utils.getById("scenario-container");
    this.newScenarioForm = Utils.getById("new-scenario-form");
    this.initEventListeners();
    this.loadScenarios();
  },

  /**
   * Initialize event listeners
   */
  initEventListeners: function () {
    // New scenario form submission
    if (this.newScenarioForm) {
      this.newScenarioForm.addEventListener("submit", (e) => {
        e.preventDefault();
        console.log("Form submitted");
        const scenarioNameInput = Utils.getById("new-scenario-name");
        const scenarioName = scenarioNameInput.value.trim();
        console.log("Scenario name:", scenarioName);

        if (scenarioName) {
          this.addNewScenario(scenarioName);
          scenarioNameInput.value = "";
        }
      });
    } else {
      console.warn("New scenario form not found");
    }
  },

  /**
   * Load scenarios from the server
   */
  loadScenarios: function () {
    // Show loading state
    if (this.scenarioContainer) {
      this.scenarioContainer.innerHTML =
        '<div class="col-12 text-center"><p>Loading scenarios...</p></div>';

      // Fetch scenarios from the server
      ApiService.getScenarios()
        .then((data) => {
          // Clear container
          this.scenarioContainer.innerHTML = "";

          // Add each scenario
          data.scenarios.forEach((scenario) => {
            this.addScenarioCard(scenario);
          });
        })
        .catch(() => {
          this.scenarioContainer.innerHTML =
            '<div class="col-12 text-center"><p>Error loading scenarios. Please refresh the page.</p></div>';
        });
    }
  },

  /**
   * Add a scenario card to the UI
   * @param {string} scenario - The scenario name
   */
  addScenarioCard: function (scenario) {
    const scenarioCol = Utils.createElement("div", {
      className: "col-lg-6 col-md-8 mb-4",
    });
    
    // Check if user is a teacher (for delete button visibility)
    const isTeacher = document.body.getAttribute('data-user-type') === 'teacher';
    
    scenarioCol.innerHTML = `
      <div class="card scenario-card" data-scenario="${scenario}">
        <div class="card-body">
          <div class="scenario-icon"><i class="fas fa-landmark"></i></div>
          <h5 class="card-title">${scenario}</h5>
          ${isTeacher ? `
          <button class="btn btn-sm btn-danger delete-scenario" data-scenario="${scenario}">
            <i class="fas fa-trash-alt"></i>
          </button>
          ` : ''}
        </div>
      </div>
    `;

    // Add click event to the scenario card
    const card = scenarioCol.querySelector(".scenario-card");
    card.addEventListener("click", function (e) {
      // Don't trigger if clicking the delete button
      if (!e.target.closest(".delete-scenario")) {
        const scenarioName = this.getAttribute("data-scenario");
        
        // Check if GameComponent exists, otherwise redirect to view-scenarios
        if (typeof GameComponent !== 'undefined') {
          GameComponent.startGame(scenarioName);
        } else {
          console.log(`GameComponent not found, redirecting to scenario: ${scenarioName}`);
          // Store the scenario in localStorage for auto-start
          localStorage.setItem('startScenario', scenarioName);
          // Redirect to the view-scenarios page
          window.location.href = '/view-scenarios';
        }
      }
    });

    // Add delete event if delete button exists
    const deleteBtn = scenarioCol.querySelector(".delete-scenario");
    if (deleteBtn) {
      deleteBtn.addEventListener("click", (e) => {
        e.stopPropagation(); // Prevent the card click event
        const scenarioName = e.currentTarget.getAttribute("data-scenario");
        this.deleteScenario(scenarioName);
      });
    }

    this.scenarioContainer.appendChild(scenarioCol);
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
          const modalElement = document.getElementById("addScenarioModal");
          if (modalElement) {
            const modalInstance = bootstrap.Modal.getInstance(modalElement);
            if (modalInstance) {
              modalInstance.hide();
            } else {
              // If modal instance doesn't exist yet, create and hide it
              const newModal = new bootstrap.Modal(modalElement);
              newModal.hide();
            }
          }
        } else {
          alert(data.message || "Scenario already exists");
        }
      })
      .catch((error) => {
        console.error("Error adding scenario:", error);
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
