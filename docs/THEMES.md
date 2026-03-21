# DHQ Global Theme System

This document outlines the architecture and available options for the DHQ Global Theme System. The system uses CSS variables and a `data-theme` attribute to provide a consistent, premium, and eye-friendly interface across the entire server.

## Core Philosophy
- **Pastel Palette**: All themes use soft, pastel colors to minimize eye strain and provide a "premium" feel.
- **Glassmorphism**: Themes heavily leverage glassmorphism (transparency + background blur).
- **Unified Variables**: All components should use the CSS variables defined in `main.css`.

## Available Themes

### 1. Light (Default)
Soft sky blue and white gradients.
- `bg-gradient`: Sky blue to pinkish white.
- `primary-color`: #3b82f6 (Blue)

### 2. Dark
Deep navy and indigo.
- `bg-gradient`: Navy to indigo.
- `primary-color`: #6366f1 (Indigo)

### 3. Blue
Serene oceanic pastel blue.
- `bg-gradient`: Light blue to ocean blue.

### 4. Pink
Sakura and rose pastel.
- `bg-gradient`: Soft pink to rose.

### 5. Red
Soft coral and terracotta pastel.
- `bg-gradient`: Coral to terracotta.

### 6. Gold
Elegant champagne and gold pastel.
- `bg-gradient`: Champagne to soft gold.

### 7. Silver
Metallic gray and silver pastel.
- `bg-gradient`: Light gray to silver.

### 8. Gray
Monochromatic soft gray.
- `bg-gradient`: Smoke to charcoal.

### 9. Purple
Lavender and amethyst pastel.
- `bg-gradient`: Lavender to soft purple.

### 10. Brown
Earth tones and coffee pastel.
- `bg-gradient`: Latte to mocha.

### 11. Glass
Maximum transparency and blur.
- `bg-gradient`: Transparent gradients over the background vector shapes.

## Implementation Details

### Theme Selection
Themes are applied by setting the `data-theme` attribute on the `<html>` or `#app` element:
```html
<div id="app" data-theme="pink">...</div>
```

### CSS Variables
The following variables must be defined for every theme:
- `--bg-gradient`: The animated background gradient.
- `--text-primary`: Main text color.
- `--text-secondary`: Sub-text color.
- `--glass-bg-primary`: Primary glass background (panels).
- `--glass-bg-secondary`: Secondary glass background (cards).
- `--glass-border`: Subtle border for glass elements.
- `--primary-color`: Use for accents, buttons, and active states.

### Persistence
The theme selection is stored in `localStorage` under the key `dhq-theme`.

## Adding New Themes
To add a new theme, add a new block in `src/assets/main.css`:
```css
[data-theme="new-theme"] {
  --bg-gradient: ...;
  --text-primary: ...;
  /* ... other variables ... */
}
```
