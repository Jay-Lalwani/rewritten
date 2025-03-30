/**
 * Teacher Dashboard component for managing teacher assignments
 */

const TeacherDashboardComponent = {
  assignmentsContainer: null,

  /**
   * Initialize the teacher dashboard component
   */
  init: function() {
    this.assignmentsContainer = Utils.getById('assignments-container');
    this.initEventListeners();
    // For now, we're using dummy data, but this would load actual assignments
    // this.loadAssignments();
  },

  /**
   * Initialize event listeners for the teacher dashboard
   */
  initEventListeners: function() {
    // Event delegation for assignment card actions
    if (this.assignmentsContainer) {
      this.assignmentsContainer.addEventListener('click', (e) => {
        // Handle view responses button
        if (e.target.closest('.btn-outline-primary')) {
          const card = e.target.closest('.assignment-card');
          if (card) {
            const title = card.querySelector('.card-title').textContent;
            console.log(`View responses for: ${title}`);
            // In a real app, this would navigate to the responses page
            alert(`Viewing responses for: ${title}`);
          }
        }
        
        // Handle delete button
        if (e.target.closest('.btn-outline-danger')) {
          const card = e.target.closest('.assignment-card');
          if (card) {
            const title = card.querySelector('.card-title').textContent;
            if (confirm(`Are you sure you want to delete the assignment: "${title}"?`)) {
              console.log(`Deleting assignment: ${title}`);
              // In a real app, this would delete the assignment via API
              card.closest('.col-lg-6').remove();
            }
          }
        }
      });
    }
    
    // Create assignment button - reuse the same modal as creating scenarios
    const createButton = document.querySelector('#teacher-dashboard .btn-primary');
    if (createButton) {
      createButton.addEventListener('click', () => {
        // Make sure the modal title is appropriate for assignments
        const modalTitle = document.querySelector('#addScenarioModal .modal-title');
        if (modalTitle) {
          modalTitle.textContent = 'Create New Assignment';
        }
        
        // Update the form label if needed
        const formLabel = document.querySelector('#addScenarioModal label');
        if (formLabel) {
          formLabel.textContent = 'Assignment Name:';
        }
      });
    }
  },

  /**
   * Create a new assignment (would be implemented in a real app)
   * Currently just reuses scenario creation
   */
  createAssignment: function(name) {
    // In a real app, we would save the assignment to the backend
    // For now, we'll just create a new card
    this.addAssignmentCard({
      title: name,
      class: "World History - Period 3",
      dueDate: "12/31/2023",
      description: "New historical scenario assignment.",
      completed: 0,
      total: 24,
      status: "Active"
    });
  },

  /**
   * Add an assignment card to the UI
   * @param {Object} assignment - The assignment data
   */
  addAssignmentCard: function(assignment) {
    const col = document.createElement('div');
    col.className = 'col-lg-6 col-md-8 mb-4';
    
    // Random icon from a set of educational icons
    const icons = ['book', 'scroll', 'landmark', 'university', 'atlas', 'globe'];
    const randomIcon = icons[Math.floor(Math.random() * icons.length)];
    
    col.innerHTML = `
      <div class="card assignment-card">
        <div class="card-body">
          <div class="assignment-header">
            <span class="assignment-icon"><i class="fas fa-${randomIcon}"></i></span>
            <h5 class="card-title">${assignment.title}</h5>
          </div>
          <p class="card-text">Assigned to: ${assignment.class}</p>
          <p class="card-subtitle">Due: ${assignment.dueDate}</p>
          <div class="assignment-details">
            <p>${assignment.description}</p>
            <div class="assignment-stats">
              <span class="badge bg-info">${assignment.completed}/${assignment.total} students completed</span>
              <span class="badge bg-${assignment.status === 'Active' ? 'success' : 'secondary'}">${assignment.status}</span>
            </div>
          </div>
          <div class="mt-3">
            <button class="btn btn-sm btn-outline-primary">View Responses</button>
            <button class="btn btn-sm btn-outline-danger">
              <i class="fas fa-trash-alt"></i>
            </button>
          </div>
        </div>
      </div>
    `;
    
    this.assignmentsContainer.prepend(col);
  }
};

// Make sure this component is initialized in app.js 