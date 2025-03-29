/**
 * Game component for managing game state and interactions
 */

const GameComponent = {
  // DOM Elements
  startScreen: null,
  loadingScreen: null,
  gameContainer: null,
  gameVideo: null,
  narrativeText: null,
  decisionOptions: null,
  progressPath: null,

  // Game State
  currentScene: null,
  decisions: [],

  /**
   * Initialize the game component
   */
  init: function() {
    // Initialize DOM elements
    this.startScreen = Utils.getById('start-screen');
    this.loadingScreen = Utils.getById('loading-screen');
    this.gameContainer = Utils.getById('game-container');
    this.gameVideo = Utils.getById('game-video');
    this.narrativeText = Utils.getById('narrative-text');
    this.decisionOptions = Utils.getById('decision-options');
    this.progressPath = Utils.getById('progress-path');

    this.initEventListeners();
  },

  /**
   * Initialize event listeners
   */
  initEventListeners: function() {
    // Video player events
    if (this.gameVideo) {
      this.gameVideo.addEventListener('ended', () => {
        // Display decision options when video ends
        this.enableDecisions();
      });
    }
  },

  /**
   * Start a new game with the given scenario
   * @param {string} scenario - The scenario name
   */
  startGame: function(scenario) {
    // Show loading screen
    Utils.hideElement(this.startScreen);
    Utils.showElement(this.loadingScreen);

    // Request initial game state from the server
    ApiService.startGame(scenario)
      .then((data) => {
        // Save the current scene and initialize the game
        this.currentScene = data.narrative;

        // Set video source
        this.gameVideo.src = data.media;
        this.gameVideo.load();

        // Hide loading screen and show game container
        Utils.hideElement(this.loadingScreen);
        Utils.showElement(this.gameContainer);

        // Update narrative text
        this.updateNarrativeDisplay();

        // Start playing the video
        this.gameVideo.play();
      })
      .catch(() => {
        alert('An error occurred while starting the game. Please try again.');

        // Go back to start screen
        Utils.hideElement(this.loadingScreen);
        Utils.showElement(this.startScreen);
      });
  },

  /**
   * Update the narrative display
   */
  updateNarrativeDisplay: function() {
    // Update the narrative text
    if (this.narrativeText && this.currentScene) {
      this.narrativeText.textContent = this.currentScene.narrative;
    }

    // Clear existing decision options
    if (this.decisionOptions) {
      this.decisionOptions.innerHTML = '';

      // Create decision cards (but don't enable them until videos finish)
      if (this.currentScene && this.currentScene.options) {
        this.currentScene.options.forEach((option) => {
          const decisionCard = Utils.createElement('div', { className: 'col-md-4' });
          decisionCard.innerHTML = `
            <div class="card decision-card" data-decision-id="${option.id}">
              <div class="card-body">
                <p class="card-text">${option.option}</p>
              </div>
            </div>
          `;
          this.decisionOptions.appendChild(decisionCard);
        });
      }
    }
  },

  /**
   * Enable decision cards for interaction
   */
  enableDecisions: function() {
    // Enable decision cards
    const decisionCards = document.querySelectorAll('.decision-card');
    decisionCards.forEach((card) => {
      card.addEventListener('click', () => {
        const decisionId = card.getAttribute('data-decision-id');
        this.makeDecision(decisionId);

        // Add selected class to the chosen card
        decisionCards.forEach((c) => c.classList.remove('selected'));
        card.classList.add('selected');
      });
    });
  },

  /**
   * Make a decision
   * @param {string} decisionId - The selected decision ID
   */
  makeDecision: function(decisionId) {
    // Show loading screen
    Utils.hideElement(this.gameContainer);
    Utils.showElement(this.loadingScreen);

    // Save the decision to the history
    const selectedOption = this.currentScene.options.find(
      (opt) => opt.id === decisionId
    );
    
    this.decisions.push({
      scene_id: this.currentScene.scene_id,
      decision: decisionId,
      decision_text: selectedOption.option,
    });

    // Update progress tracker
    this.updateProgressTracker();

    // Send decision to the server
    ApiService.makeDecision(this.currentScene.scene_id, decisionId)
      .then((data) => {
        // Update current scene
        this.currentScene = data.narrative;

        // Update video
        this.gameVideo.src = data.media;
        this.gameVideo.load();

        // Hide loading screen, show game container
        Utils.hideElement(this.loadingScreen);
        Utils.showElement(this.gameContainer);

        // Update narrative
        this.updateNarrativeDisplay();

        // Start playing the video
        this.gameVideo.play();
      })
      .catch(() => {
        alert('An error occurred while processing your decision. Please try again.');

        // Go back to game container
        Utils.hideElement(this.loadingScreen);
        Utils.showElement(this.gameContainer);
      });
  },

  /**
   * Update the progress tracker with decision history
   */
  updateProgressTracker: function() {
    if (this.progressPath) {
      // Clear current progress display
      this.progressPath.innerHTML = '';

      // Add each decision to the progress path
      this.decisions.forEach((decision, index) => {
        const progressItem = Utils.createElement('div', {
          className: 'progress-item'
        }, `Decision ${index + 1}: ${decision.decision_text}`);
        
        this.progressPath.appendChild(progressItem);
      });
    }
  }
}; 