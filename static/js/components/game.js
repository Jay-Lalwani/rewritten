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
  ttsButton: null,
  narrativeAudio: null,

  // Game State
  currentScene: null,
  decisions: [],
  isPlayingAudio: false,
  isMuted: false,
  pendingDecision: null,  // Store decision while quiz is shown
  preloadedQuiz: null,    // Store preloaded quiz question

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
    this.ttsButton = Utils.getById('tts-button');
    this.narrativeAudio = Utils.getById('narrative-audio');

    this.initEventListeners();
  },

  /**
   * Initialize event listeners
   */
  initEventListeners: function() {
    // Video player events
    if (this.gameVideo) {
      this.gameVideo.addEventListener('play', () => {
        // Auto-play audio when video starts
        this.playNarrativeAudio();
        
        // Preload quiz question when video starts playing
        this.preloadQuizQuestion();
      });
      
      this.gameVideo.addEventListener('ended', () => {
        // Display decision options when video ends
        this.enableDecisions();
      });
    }

    // TTS button events
    if (this.ttsButton) {
      this.ttsButton.addEventListener('click', () => {
        this.toggleMute();
      });
    }

    // Audio player events
    if (this.narrativeAudio) {
      this.narrativeAudio.addEventListener('ended', () => {
        this.isPlayingAudio = false;
        this.updateTtsButtonState();
      });
    }
  },

  /**
   * Toggle audio mute state
   */
  toggleMute: function() {
    this.isMuted = !this.isMuted;
    
    if (this.narrativeAudio) {
      this.narrativeAudio.muted = this.isMuted;
    }
    
    this.updateTtsButtonState();
  },

  /**
   * Play narrative audio
   */
  playNarrativeAudio: function() {
    if (!this.currentScene || !this.currentScene.narrative || !this.audioUrl) {
      return;
    }

    // Set audio source if not already set
    if (!this.narrativeAudio.getAttribute('data-scene-id') || 
        this.narrativeAudio.getAttribute('data-scene-id') !== String(this.currentScene.scene_id)) {
      this.narrativeAudio.src = this.audioUrl;
      this.narrativeAudio.setAttribute('data-scene-id', this.currentScene.scene_id);
    }
    
    // Set muted state based on user preference
    this.narrativeAudio.muted = this.isMuted;
    
    // Play the audio
    this.narrativeAudio.play().catch(error => {
      console.error('Error playing narrative audio:', error);
    });
    
    this.isPlayingAudio = true;
    this.updateTtsButtonState();
  },

  /**
   * Update TTS button state
   */
  updateTtsButtonState: function() {
    if (this.isMuted) {
      this.ttsButton.innerHTML = '<i class="fas fa-volume-mute"></i>';
      this.ttsButton.title = "Unmute narrative";
    } else {
      this.ttsButton.innerHTML = '<i class="fas fa-volume-up"></i>';
      this.ttsButton.title = "Mute narrative";
    }
    this.ttsButton.disabled = false;
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
        this.audioUrl = data.audio;

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

    // Reset audio state for new narrative
    if (this.narrativeAudio) {
      this.narrativeAudio.pause();
      this.narrativeAudio.currentTime = 0;
      this.narrativeAudio.removeAttribute('src');
      this.narrativeAudio.removeAttribute('data-scene-id');
      this.isPlayingAudio = false;
      this.updateTtsButtonState();
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

    // Preload a quiz question while user is watching video/reading narrative
    this.preloadQuizQuestion();
  },

  /**
   * Preload a quiz question for later use
   */
  preloadQuizQuestion: function() {
    // Only preload if we don't already have one
    if (!this.preloadedQuiz) {
      ApiService.getQuizQuestion()
        .then(data => {
          if (data.question) {
            this.preloadedQuiz = data.question;
            console.log("Quiz question preloaded and ready");
          }
        })
        .catch(error => {
          console.error("Error preloading quiz:", error);
        });
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
    // Store the decision for later processing
    this.pendingDecision = {
      sceneId: this.currentScene.scene_id,
      decisionId: decisionId
    };
    
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

    // Hide game container
    Utils.hideElement(this.gameContainer);
    
    // Use preloaded quiz question if available, otherwise fetch one
    if (this.preloadedQuiz) {
      QuizComponent.showQuestion(this.preloadedQuiz);
      this.preloadedQuiz = null; // Clear so we'll preload a new one
    } else {
      // Fallback to loading screen and fetch a question if preloaded one isn't available
      Utils.showElement(this.loadingScreen);
      ApiService.getQuizQuestion()
        .then(data => {
          if (data.question) {
            Utils.hideElement(this.loadingScreen);
            QuizComponent.showQuestion(data.question);
          } else {
            this.processDecision();
          }
        })
        .catch(error => {
          console.error("Error fetching quiz:", error);
          this.processDecision();
        });
    }
  },
  
  /**
   * Continue after quiz is completed
   */
  continueAfterQuiz: function() {
    // Process the pending decision
    this.processDecision();
  },
  
  /**
   * Process the stored decision with the API
   */
  processDecision: function() {
    if (!this.pendingDecision) {
      console.error("No pending decision to process");
      return;
    }
    
    // Send decision to the server
    ApiService.makeDecision(this.pendingDecision.sceneId, this.pendingDecision.decisionId)
      .then((data) => {
        // Update current scene
        this.currentScene = data.narrative;
        this.audioUrl = data.audio;

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
        
        // Clear the pending decision
        this.pendingDecision = null;
      })
      .catch(() => {
        alert('An error occurred while processing your decision. Please try again.');

        // Go back to game container
        Utils.hideElement(this.loadingScreen);
        Utils.showElement(this.gameContainer);
        
        // Clear the pending decision
        this.pendingDecision = null;
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