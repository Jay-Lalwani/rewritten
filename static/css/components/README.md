# CSS Components

This directory contains component-specific CSS files that can be used to break down the main `styles.css` file as the application grows.

## Component Structure

Each component should have its own CSS file named after the component. For example:

- `header.css` - Styles for the header component
- `game-container.css` - Styles for the game container
- `scenario-card.css` - Styles for scenario cards

## Usage

When implementing component-specific CSS, follow these guidelines:

1. Use BEM (Block Element Modifier) naming conventions for classes
2. Keep selectors specific to the component
3. Use CSS variables defined in the root for consistency
4. Include the component CSS in the head of the document

Example component CSS file:

```css
/* scenario-card.css */
.scenario-card {
  transition: all 0.3s ease;
  border-radius: 8px;
  border: 2px solid var(--primary-color);
  background-color: #fff;
}

.scenario-card__title {
  font-size: 1.2rem;
  color: var(--primary-color);
}

.scenario-card__icon {
  color: var(--accent-color);
  font-size: 2rem;
}

.scenario-card--selected {
  border-color: var(--secondary-color);
  transform: translateY(-5px);
}
```

## Integration with Base Styles

When breaking down `styles.css` into component files, remember to:

1. Keep global styles, variables, and resets in the main `styles.css`
2. Import component styles using `@import` or include them in the HTML
3. Ensure there are no conflicts between component styles 