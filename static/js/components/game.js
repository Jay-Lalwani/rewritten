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
  pendingDecision: null, // Store decision while quiz is shown
  preloadedQuiz: null, // Store preloaded quiz question

  /**
   * Initialize the game component
   */
  init: function () {
    console.log('GameComponent init called');
    
    // First try to find elements directly
    this.startScreen = Utils.getById("start-screen");
    this.loadingScreen = Utils.getById("loading-screen");
    this.gameContainer = Utils.getById("game-container");
    
    // If elements aren't found in the main document (might be in a section),
    // try to find them within section containers
    if (!this.gameContainer) {
      const gameSection = document.getElementById('section-game');
      if (gameSection) {
        console.log('Game section found, searching within it');
        this.gameContainer = gameSection.querySelector('#game-container');
        if (!this.loadingScreen) {
          this.loadingScreen = gameSection.querySelector('#loading-screen');
        }
      }
    }
    
    console.log('Game container found:', !!this.gameContainer);
    console.log('Loading screen found:', !!this.loadingScreen);
    console.log('Start screen found:', !!this.startScreen);
    
    // Initialize video and narrative elements if game container exists
    if (this.gameContainer) {
      this.gameVideo = this.gameContainer.querySelector("#game-video");
      this.narrativeText = this.gameContainer.querySelector("#narrative-text");
      this.decisionOptions = this.gameContainer.querySelector("#decision-options");
      this.progressPath = this.gameContainer.querySelector("#progress-path");
      this.ttsButton = this.gameContainer.querySelector("#tts-button");
      this.narrativeAudio = this.gameContainer.querySelector("#narrative-audio");
      
      console.log('Game video found:', !!this.gameVideo);
      console.log('Narrative text found:', !!this.narrativeText);
      console.log('Decision options found:', !!this.decisionOptions);
    } else {
      console.warn("Game container not found. Some game features may not work.");
    }

    this.initEventListeners();
  },

  /**
   * Initialize event listeners
   */
  initEventListeners: function () {
    // Video player events
    if (this.gameVideo) {
      this.gameVideo.addEventListener("play", () => {
        // Auto-play audio when video starts
        this.playNarrativeAudio();

        // Preload quiz question when video starts playing
        this.preloadQuizQuestion();
      });

      this.gameVideo.addEventListener("ended", () => {
        // Display decision options when video ends
        this.enableDecisions();
      });
    }

    // TTS button events
    if (this.ttsButton) {
      this.ttsButton.addEventListener("click", () => {
        this.toggleMute();
      });
    }

    // Audio player events
    if (this.narrativeAudio) {
      this.narrativeAudio.addEventListener("ended", () => {
        this.isPlayingAudio = false;
        this.updateTtsButtonState();
      });
    }
  },

  /**
   * Toggle audio mute state
   */
  toggleMute: function () {
    this.isMuted = !this.isMuted;

    if (this.narrativeAudio) {
      this.narrativeAudio.muted = this.isMuted;
    }

    this.updateTtsButtonState();
  },

  /**
   * Play narrative audio
   */
  playNarrativeAudio: function () {
    if (!this.currentScene || !this.currentScene.narrative || !this.audioUrl) {
      return;
    }

    // Set audio source if not already set
    if (
      !this.narrativeAudio.getAttribute("data-scene-id") ||
      this.narrativeAudio.getAttribute("data-scene-id") !==
        String(this.currentScene.scene_id)
    ) {
      this.narrativeAudio.src = this.audioUrl;
      this.narrativeAudio.setAttribute(
        "data-scene-id",
        this.currentScene.scene_id,
      );
    }

    // Set muted state based on user preference
    this.narrativeAudio.muted = this.isMuted;

    // Play the audio
    this.narrativeAudio.play().catch((error) => {
      console.error("Error playing narrative audio:", error);
    });

    this.isPlayingAudio = true;
    this.updateTtsButtonState();
  },

  /**
   * Update TTS button state
   */
  updateTtsButtonState: function () {
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
  startGame: function (scenario) {
    console.log('GameComponent.startGame called with scenario:', scenario);
    
    // Show loading screen
    if (this.startScreen) {
      Utils.hideElement(this.startScreen);
    }
    
    if (this.loadingScreen) {
      Utils.showElement(this.loadingScreen);
    }
    
    // Force section-based navigation with direct style manipulation
    const sections = document.querySelectorAll('.section-content');
    sections.forEach(section => {
      section.style.display = 'none';
      section.classList.remove('active');
    });
    
    const gameSection = document.getElementById('section-game');
    if (gameSection) {
      gameSection.style.display = 'block';
      gameSection.classList.add('active');
      console.log('Game section activated');
      
      // Make sure the game container is in the game section
      this.gameContainer = gameSection.querySelector('#game-container');
      if (!this.gameContainer) {
        console.error('Game container not found in game section');
      }
      
      // Update sidebar active state
      const navItems = document.querySelectorAll('.sidebar-nav-item');
      navItems.forEach(nav => nav.classList.remove('active'));
      
      const gameNavItem = document.querySelector('.sidebar-nav-item[data-section="game"]');
      if (gameNavItem) {
        gameNavItem.classList.add('active');
      }
    } else {
      console.error('Game section not found');
    }

    // Request initial game state from the server
    console.log('Calling ApiService.startGame');
    ApiService.startGame(scenario)
      .then((data) => {
        console.log('Game data received from API:', data);
        
        // Save the current scene and initialize the game
        this.currentScene = data.narrative;
        this.audioUrl = data.audio;

        // Set video source if video element exists
        if (this.gameVideo) {
          this.gameVideo.src = data.media;
          this.gameVideo.load();
          console.log('Video source set:', data.media);
        } else {
          console.error('Game video element not found');
          
          // Try to find it again
          if (this.gameContainer) {
            this.gameVideo = this.gameContainer.querySelector('#game-video');
            if (this.gameVideo) {
              this.gameVideo.src = data.media;
              this.gameVideo.load();
              console.log('Video element found on retry');
            }
          }
        }

        // Hide loading screen and show game container
        if (this.loadingScreen) {
          Utils.hideElement(this.loadingScreen);
        }
        
        if (this.gameContainer) {
          Utils.showElement(this.gameContainer);
          console.log('Game container shown');
        } else {
          console.error('Cannot show game container: not found');
        }

        // Update narrative text
        this.updateNarrativeDisplay();

        // Start playing the video if it exists
        if (this.gameVideo) {
          console.log('Starting video playback');
          this.gameVideo.play().catch(error => {
            console.error('Error playing video:', error);
          });
        }
      })
      .catch((error) => {
        console.error('Error starting game:', error);
        alert("An error occurred while starting the game. Please try again.");

        // Go back to start screen
        if (this.loadingScreen) {
          Utils.hideElement(this.loadingScreen);
        }
        
        if (this.startScreen) {
          Utils.showElement(this.startScreen);
        }
        
        // Also handle section-based navigation for error case
        const startSection = document.getElementById('section-gallery');
        if (startSection) {
          sections.forEach(section => {
            section.style.display = 'none';
            section.classList.remove('active');
          });
          
          startSection.style.display = 'block';
          startSection.classList.add('active');
          
          // Update sidebar active state
          const navItems = document.querySelectorAll('.sidebar-nav-item');
          navItems.forEach(nav => nav.classList.remove('active'));
          
          const galleryNavItem = document.querySelector('.sidebar-nav-item[data-section="gallery"]');
          if (galleryNavItem) {
            galleryNavItem.classList.add('active');
          }
        }
      });
  },

  /**
   * Update the narrative display
   */
  updateNarrativeDisplay: function () {
    // Update the narrative text
    if (this.narrativeText && this.currentScene) {
      this.narrativeText.textContent = this.currentScene.narrative;
    }

    // Reset audio state for new narrative
    if (this.narrativeAudio) {
      this.narrativeAudio.pause();
      this.narrativeAudio.currentTime = 0;
      this.narrativeAudio.removeAttribute("src");
      this.narrativeAudio.removeAttribute("data-scene-id");
      this.isPlayingAudio = false;
      this.updateTtsButtonState();
    }

    // Clear existing decision options
    if (this.decisionOptions) {
      this.decisionOptions.innerHTML = "";

      // Create decision cards (but don't enable them until videos finish)
      if (this.currentScene && this.currentScene.options) {
        this.currentScene.options.forEach((option) => {
          const decisionCard = Utils.createElement("div", {
            className: "col-md-4",
          });
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
  preloadQuizQuestion: function () {
    // Only preload if we don't already have one
    if (!this.preloadedQuiz) {
      ApiService.getQuizQuestion()
        .then((data) => {
          if (data.question) {
            this.preloadedQuiz = data.question;
            console.log("Quiz question preloaded and ready");
          }
        })
        .catch((error) => {
          console.error("Error preloading quiz:", error);
        });
    }
  },

  /**
   * Enable decision cards for interaction
   */
  enableDecisions: function () {
    // Enable decision cards
    const decisionCards = document.querySelectorAll(".decision-card");
    decisionCards.forEach((card) => {
      card.addEventListener("click", () => {
        const decisionId = card.getAttribute("data-decision-id");
        this.makeDecision(decisionId);

        // Add selected class to the chosen card
        decisionCards.forEach((c) => c.classList.remove("selected"));
        card.classList.add("selected");
      });
    });
  },

  /**
   * Make a decision
   * @param {string} decisionId - The selected decision ID
   */
  makeDecision: function (decisionId) {
    // Store the decision for later processing
    this.pendingDecision = {
      sceneId: this.currentScene.scene_id,
      decisionId: decisionId,
    };

    // Save the decision to the history
    const selectedOption = this.currentScene.options.find(
      (opt) => opt.id === decisionId,
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
        .then((data) => {
          if (data.question) {
            Utils.hideElement(this.loadingScreen);
            QuizComponent.showQuestion(data.question);
          } else {
            this.processDecision();
          }
        })
        .catch((error) => {
          console.error("Error fetching quiz:", error);
          this.processDecision();
        });
    }
  },

  /**
   * Continue after quiz is completed
   */
  continueAfterQuiz: function () {
    // Process the pending decision
    this.processDecision();
  },

  /**
   * Process the stored decision with the API
   */
  processDecision: function () {
    if (!this.pendingDecision) {
      console.error("No pending decision to process");
      return;
    }

    // Send decision to the server
    ApiService.makeDecision(
      this.pendingDecision.sceneId,
      this.pendingDecision.decisionId,
    )
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
        alert(
          "An error occurred while processing your decision. Please try again.",
        );

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
  updateProgressTracker: function () {
    if (this.progressPath) {
      // Clear current progress display
      this.progressPath.innerHTML = "";

      // Add each decision to the progress path
      this.decisions.forEach((decision, index) => {
        const progressItem = Utils.createElement(
          "div",
          {
            className: "progress-item",
          },
          `Decision ${index + 1}: ${decision.decision_text}`,
        );

        this.progressPath.appendChild(progressItem);
      });
    }
  },
};
