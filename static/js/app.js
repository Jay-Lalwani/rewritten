// Main JavaScript for Rewritten Game

document.addEventListener("DOMContentLoaded", function () {
  // DOM Elements
  const startScreen = document.getElementById("start-screen");
  const loadingScreen = document.getElementById("loading-screen");
  const gameContainer = document.getElementById("game-container");
  const gameVideo = document.getElementById("game-video");
  const narrativeText = document.getElementById("narrative-text");
  const decisionOptions = document.getElementById("decision-options");
  const progressPath = document.getElementById("progress-path");
  const scenarioContainer = document.getElementById("scenario-container");
  const newScenarioForm = document.getElementById("new-scenario-form");

  // Game State
  let currentScene = null;
  let decisions = [];

  // Load scenarios on page load
  loadScenarios();

  // Initialize Event Listeners
  initEventListeners();

  // Functions
  function initEventListeners() {
    // New scenario form submission
    newScenarioForm.addEventListener("submit", function (e) {
      e.preventDefault();
      const scenarioNameInput = document.getElementById("new-scenario-name");
      const scenarioName = scenarioNameInput.value.trim();

      if (scenarioName) {
        addNewScenario(scenarioName);
        scenarioNameInput.value = "";
      }
    });

    // Video player events
    gameVideo.addEventListener("ended", function () {
      // Display decision options when video ends
      enableDecisions();
    });
  }

  function loadScenarios() {
    // Show loading state
    scenarioContainer.innerHTML =
      '<div class="col-12 text-center"><p>Loading scenarios...</p></div>';

    // Fetch scenarios from the server
    fetch("/api/scenarios")
      .then((response) => response.json())
      .then((data) => {
        // Clear container
        scenarioContainer.innerHTML = "";

        // Add each scenario
        data.scenarios.forEach((scenario) => {
          addScenarioCard(scenario);
        });
      })
      .catch((error) => {
        console.error("Error loading scenarios:", error);
        scenarioContainer.innerHTML =
          '<div class="col-12 text-center"><p>Error loading scenarios. Please refresh the page.</p></div>';
      });
  }

  function addScenarioCard(scenario) {
    const scenarioCol = document.createElement("div");
    scenarioCol.className = "col-lg-6 col-md-8 mb-4";
    scenarioCol.innerHTML = `
            <div class="card scenario-card" data-scenario="${scenario}">
                <div class="card-body">
                    <div class="scenario-icon"><i class="fas fa-landmark"></i></div>
                    <h5 class="card-title">${scenario}</h5>
                    <button class="btn btn-sm btn-danger delete-scenario" data-scenario="${scenario}">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                </div>
            </div>
        `;

    // Add click event to the scenario card
    const card = scenarioCol.querySelector(".scenario-card");
    card.addEventListener("click", function (e) {
      // Don't trigger if clicking the delete button
      if (!e.target.closest(".delete-scenario")) {
        const scenarioName = this.getAttribute("data-scenario");
        startGame(scenarioName);
      }
    });

    // Add delete event
    const deleteBtn = scenarioCol.querySelector(".delete-scenario");
    deleteBtn.addEventListener("click", function (e) {
      e.stopPropagation(); // Prevent the card click event
      const scenarioName = this.getAttribute("data-scenario");
      deleteScenario(scenarioName);
    });

    scenarioContainer.appendChild(scenarioCol);
  }

  function addNewScenario(scenarioName) {
    // Send request to add new scenario
    fetch("/api/scenarios", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ name: scenarioName }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          // Add new scenario card
          addScenarioCard(data.scenario);

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
      .catch((error) => {
        console.error("Error adding scenario:", error);
        alert("An error occurred while adding the scenario.");
      });
  }

  function startGame(scenario) {
    // Show loading screen
    startScreen.classList.add("d-none");
    loadingScreen.classList.remove("d-none");

    // Request initial game state from the server
    fetch("/api/start", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ scenario: scenario }),
    })
      .then((response) => response.json())
      .then((data) => {
        // Save the current scene and initialize the game
        currentScene = data.narrative;

        // Set video source
        gameVideo.src = data.media;
        gameVideo.load();

        // Hide loading screen and show game container
        loadingScreen.classList.add("d-none");
        gameContainer.classList.remove("d-none");

        // Update narrative text
        updateNarrativeDisplay();

        // Start playing the video
        gameVideo.play();
      })
      .catch((error) => {
        console.error("Error starting game:", error);
        alert("An error occurred while starting the game. Please try again.");

        // Go back to start screen
        loadingScreen.classList.add("d-none");
        startScreen.classList.remove("d-none");
      });
  }

  function updateNarrativeDisplay() {
    // Update the narrative text
    narrativeText.textContent = currentScene.narrative;

    // Clear existing decision options
    decisionOptions.innerHTML = "";

    // Create decision cards (but don't enable them until videos finish)
    currentScene.options.forEach((option) => {
      const decisionCard = document.createElement("div");
      decisionCard.className = "col-md-4";
      decisionCard.innerHTML = `
                <div class="card decision-card" data-decision-id="${option.id}">
                    <div class="card-body">
                        <p class="card-text">${option.option}</p>
                    </div>
                </div>
            `;
      decisionOptions.appendChild(decisionCard);
    });
  }

  function enableDecisions() {
    // Enable decision cards
    const decisionCards = document.querySelectorAll(".decision-card");
    decisionCards.forEach((card) => {
      card.addEventListener("click", function () {
        const decisionId = this.getAttribute("data-decision-id");
        makeDecision(decisionId);

        // Add selected class to the chosen card
        decisionCards.forEach((c) => c.classList.remove("selected"));
        this.classList.add("selected");
      });
    });
  }

  function makeDecision(decisionId) {
    // Show loading screen
    gameContainer.classList.add("d-none");
    loadingScreen.classList.remove("d-none");

    // Save the decision to the history
    const selectedOption = currentScene.options.find(
      (opt) => opt.id === decisionId,
    );
    decisions.push({
      scene_id: currentScene.scene_id,
      decision: decisionId,
      decision_text: selectedOption.option,
    });

    // Update progress tracker
    updateProgressTracker();

    // Send decision to the server
    fetch("/api/decision", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        scene_id: currentScene.scene_id,
        decision: decisionId,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        // Update current scene
        currentScene = data.narrative;

        // Set video source
        gameVideo.src = data.media;
        gameVideo.load();

        // Update narrative display
        updateNarrativeDisplay();

        // Hide loading screen and show game container
        loadingScreen.classList.add("d-none");
        gameContainer.classList.remove("d-none");

        // Start playing the video
        gameVideo.play();
      })
      .catch((error) => {
        console.error("Error making decision:", error);
        alert(
          "An error occurred while processing your decision. Please try again.",
        );

        // Show game container again
        loadingScreen.classList.add("d-none");
        gameContainer.classList.remove("d-none");
      });
  }

  function updateProgressTracker() {
    // Clear the progress path
    progressPath.innerHTML = "";

    // Add each decision to the progress tracker
    decisions.forEach((decision) => {
      const progressItem = document.createElement("div");
      progressItem.className = "progress-item";
      progressItem.textContent = decision.decision_text;
      progressPath.appendChild(progressItem);
    });
  }

  function deleteScenario(scenarioName) {
    // Send request to delete scenario
    fetch(`/api/scenarios/${encodeURIComponent(scenarioName)}`, {
      method: "DELETE",
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          // Remove scenario card from DOM
          const cards = document.querySelectorAll(".scenario-card");
          cards.forEach((card) => {
            if (card.getAttribute("data-scenario") === scenarioName) {
              card.closest(".col-lg-6").remove();
            }
          });
        } else {
          alert(
            "Error deleting scenario: " + (data.message || "Unknown error"),
          );
        }
      })
      .catch((error) => {
        console.error("Error deleting scenario:", error);
        alert("An error occurred while deleting the scenario.");
      });
  }
});
