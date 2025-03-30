/**
 * Quiz component for displaying trivia questions between scenes
 */

const QuizComponent = {
    // DOM Elements
    quizContainer: null,
    quizQuestion: null,
    quizOptions: null,
    quizFeedback: null,
    quizFeedbackAlert: null,
    quizFeedbackText: null,
    quizContinueBtn: null,
    
    // Quiz State
    currentQuestion: null,
    
    /**
     * Initialize the quiz component
     */
    init: function() {
      // Initialize DOM elements
      this.quizContainer = Utils.getById('quiz-container');
      this.quizQuestion = Utils.getById('quiz-question');
      this.quizOptions = Utils.getById('quiz-options');
      this.quizFeedback = Utils.getById('quiz-feedback');
      this.quizFeedbackAlert = Utils.getById('quiz-feedback-alert');
      this.quizFeedbackText = Utils.getById('quiz-feedback-text');
      this.quizContinueBtn = Utils.getById('quiz-continue-btn');
      
      this.initEventListeners();
    },
  
    /**
     * Initialize event listeners
     */
    initEventListeners: function() {
      // Continue button
      if (this.quizContinueBtn) {
        this.quizContinueBtn.addEventListener('click', () => {
          // Hide quiz, show loading screen, and resume the game flow
          Utils.hideElement(this.quizContainer);
          Utils.showElement(GameComponent.loadingScreen);
          
          // Continue with the API request that was paused
          GameComponent.continueAfterQuiz();
        });
      }
    },
  
    /**
     * Show a quiz question
     * @param {Object} question - The question data
     */
    showQuestion: function(question) {
      this.currentQuestion = question;
      
      // Set question text
      this.quizQuestion.textContent = question.question;
      
      // Clear existing options
      this.quizOptions.innerHTML = '';
      
      // Create option cards
      question.options.forEach((option) => {
        const optionCard = Utils.createElement('div', { className: 'col-md-4' });
        optionCard.innerHTML = `
          <div class="card quiz-option-card" data-option-id="${option.id}">
            <div class="card-body">
              <p class="card-text">${option.text}</p>
            </div>
          </div>
        `;
        this.quizOptions.appendChild(optionCard);
      });
      
      // Add event listeners to options
      const optionCards = document.querySelectorAll('.quiz-option-card');
      optionCards.forEach((card) => {
        card.addEventListener('click', () => {
          const optionId = card.getAttribute('data-option-id');
          this.selectOption(optionId, optionCards, card);
        });
      });
      
      // Reset feedback
      Utils.hideElement(this.quizFeedback);
      Utils.hideElement(this.quizContinueBtn);
      
      // Hide loading screen, show quiz container
      Utils.hideElement(GameComponent.loadingScreen);
      Utils.showElement(this.quizContainer);
  
      console.log("Quiz question displayed to user");
    },
  
    /**
     * Handle user selecting an option
     * @param {string} optionId - The selected option ID
     * @param {NodeList} allCards - All option cards
     * @param {Element} selectedCard - The selected card
     */
    selectOption: function(optionId, allCards, selectedCard) {
      // Disable all options
      allCards.forEach((card) => {
        card.style.pointerEvents = 'none';
      });
      
      // Add selected class
      allCards.forEach((card) => card.classList.remove('selected'));
      selectedCard.classList.add('selected');
      
      // Check if answer is correct
      const isCorrect = optionId === this.currentQuestion.correct_option_id;
      
      // Show feedback
      if (isCorrect) {
        this.quizFeedbackAlert.className = 'alert alert-success';
        this.quizFeedbackText.textContent = 'Correct! ' + this.currentQuestion.explanation;
      } else {
        this.quizFeedbackAlert.className = 'alert alert-danger';
        this.quizFeedbackText.textContent = 'Incorrect. ' + this.currentQuestion.explanation;
        
        // Highlight correct answer
        allCards.forEach((card) => {
          if (card.getAttribute('data-option-id') === this.currentQuestion.correct_option_id) {
            card.classList.add('correct');
          }
        });
      }
      
      Utils.showElement(this.quizFeedback);
      Utils.showElement(this.quizContinueBtn);
    }
  }; 