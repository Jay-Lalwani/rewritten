/**
 * Utility functions for the Rewritten application
 */

const Utils = {
  /**
   * Shows an element by removing the d-none class
   * @param {HTMLElement} element - The element to show
   */
  showElement: function (element) {
    if (element) {
      element.classList.remove("d-none");
    }
  },

  /**
   * Hides an element by adding the d-none class
   * @param {HTMLElement} element - The element to hide
   */
  hideElement: function (element) {
    if (element) {
      element.classList.add("d-none");
    }
  },

  /**
   * Creates an element with the given attributes and properties
   * @param {string} tag - The HTML tag to create
   * @param {Object} attributes - Attributes to set on the element
   * @param {string} textContent - Optional text content for the element
   * @returns {HTMLElement} The created element
   */
  createElement: function (tag, attributes = {}, textContent = "") {
    const element = document.createElement(tag);

    // Set attributes
    for (const [key, value] of Object.entries(attributes)) {
      if (key === "className") {
        element.className = value;
      } else {
        element.setAttribute(key, value);
      }
    }

    // Set text content if provided
    if (textContent) {
      element.textContent = textContent;
    }

    return element;
  },

  /**
   * Get a DOM element by its ID
   * @param {string} id - The ID of the element
   * @returns {HTMLElement} The DOM element
   */
  getById: function (id) {
    return document.getElementById(id);
  },
};
