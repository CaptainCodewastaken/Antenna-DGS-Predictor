# Spec: frontend

> **Module ID:** `frontend`  
> **Capability Map:** [capability_map.md](file:///Users/himaghnaroy/.gemini/antigravity-ide/brain/b5b0a198-c758-41d8-a785-cb83ea463b44/capability_map.md)  
> **Depends on:** `api`  
> **Consumed by:** end users (judges, evaluators)

---

## Objective

Build a premium, visually stunning React SPA that implements the "Physics Under Glass" concept — three progressive layers of depth (Design Canvas → Physics Reveal → ML Arena) in one cohesive experience. The UI must impress non-expert judges at first glance AND withstand scrutiny from knowledgeable evaluators who dig deeper.

### Design Philosophy
- **Dark mode first** — premium, modern aesthetic
- **Glassmorphism** — frosted glass panels with backdrop-filter
- **Micro-animations** — every state change is animated (not jarring)
- **Progressive disclosure** — complexity revealed on demand, not dumped on screen
- **Data density** — lots of information, elegantly organized

---

## Tech Stack

- **Framework:** React 18+ (Vite)
- **Language:** JavaScript (JSX)
- **Styling:** Vanilla CSS with CSS custom properties (design tokens)
- **Charts:** Plotly.js (2D polar, 3D surface, line charts)
- **Canvas:** SVG (antenna schematic rendering)
- **Fonts:** Inter (UI), JetBrains Mono (data/numbers)
- **Icons:** Lucide React
- **HTTP:** fetch API (no axios — keep it simple)
- **State:** React useState/useReducer (no Redux — app state is simple)

---

## Commands

```bash
# Install dependencies
cd frontend && npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint
npm run lint
```

---

## Project Structure

```
frontend/
├── index.html
├── package.json
├── vite.config.js
├── public/
│   └── favicon.svg
├── src/
│   ├── main.jsx                    # Entry point
│   ├── App.jsx                     # Root layout + state management
│   ├── index.css                   # Global styles, design tokens, glassmorphism
│   │
│   ├── api/
│   │   └── client.js               # API client: predict(), getPattern(), etc.
│   │
│   ├── components/
│   │   ├── Layout/
│   │   │   ├── Header.jsx           # App title, branding
│   │   │   ├── Sidebar.jsx          # Antenna configuration controls
│   │   │   └── Layout.css
│   │   │
│   │   ├── AntennaCanvas/
│   │   │   ├── AntennaCanvas.jsx    # SVG antenna schematic (Layer 1)
│   │   │   ├── PatchRenderer.jsx    # Draws the patch on substrate
│   │   │   ├── SlotRenderer.jsx     # Draws DGS slots on ground plane
│   │   │   ├── DimensionLabels.jsx  # Dimension annotations
│   │   │   └── AntennaCanvas.css
│   │   │
│   │   ├── Controls/
│   │   │   ├── DimensionSliders.jsx # Substrate, patch, feed sliders
│   │   │   ├── SubstratePresets.jsx # FR4, Rogers material selector
│   │   │   ├── SlotControls.jsx     # Add/remove/configure DGS slots
│   │   │   └── Controls.css
│   │   │
│   │   ├── Results/
│   │   │   ├── PredictionCards.jsx   # Frequency, Gain result cards (animated)
│   │   │   ├── PhysicsReveal.jsx     # Expandable physics detail panel (Layer 2)
│   │   │   ├── CavityModelDetail.jsx # Shows cavity model equation + terms
│   │   │   ├── DGSCircuitDetail.jsx  # Shows L, C, equivalent circuit
│   │   │   └── Results.css
│   │   │
│   │   ├── Patterns/
│   │   │   ├── PolarPattern.jsx      # 2D polar radiation pattern (Plotly)
│   │   │   ├── Pattern3D.jsx         # 3D radiation surface (Plotly)
│   │   │   ├── SParameterPlot.jsx    # S₁₁ return loss chart (Plotly)
│   │   │   └── Patterns.css
│   │   │
│   │   ├── ModelComparison/
│   │   │   ├── ModelArena.jsx        # Collapsible ML comparison section (Layer 3)
│   │   │   ├── Leaderboard.jsx       # Model ranking table
│   │   │   ├── MetricsTable.jsx      # R², MAE, RMSE per model
│   │   │   ├── FeatureImportance.jsx # Bar chart of feature importance
│   │   │   ├── LearningCurves.jsx    # Learning curve line charts
│   │   │   └── ModelComparison.css
│   │   │
│   │   └── shared/
│   │       ├── GlassCard.jsx         # Reusable glassmorphism card
│   │       ├── AnimatedNumber.jsx    # Number that animates on change
│   │       ├── LoadingSpinner.jsx
│   │       ├── Tooltip.jsx
│   │       └── shared.css
│   │
│   ├── hooks/
│   │   ├── useAntennaConfig.js       # State for antenna configuration
│   │   ├── usePrediction.js          # Fetch prediction on config change (debounced)
│   │   ├── usePattern.js             # Fetch radiation pattern
│   │   └── useModelComparison.js     # Fetch model comparison data
│   │
│   └── utils/
│       ├── constants.js              # Substrate presets, default dimensions
│       ├── formatters.js             # Number formatting (GHz, dBi, etc.)
│       └── debounce.js               # Debounce utility for slider changes
```

---

## Page Layout

```
┌──────────────────────────────────────────────────────────────────────┐
│  HEADER: "Antenna DGS Predictor — Physics Under Glass"              │
├──────────────┬───────────────────────────────────────────────────────┤
│              │                                                       │
│  SIDEBAR     │  MAIN CONTENT                                        │
│              │                                                       │
│  Substrate   │  ┌─────────────────────┬─────────────────────┐       │
│  · Material  │  │                     │                     │       │
│  · W, L, H   │  │  ANTENNA CANVAS     │  PREDICTION CARDS   │       │
│              │  │  (SVG schematic)     │  · Freq: 2.41 GHz  │       │
│  Patch       │  │                     │  · Gain: 6.2 dBi   │       │
│  · W, L      │  │                     │  · BW: 80 MHz      │       │
│              │  │                     │                     │       │
│  Feed        │  └─────────────────────┴─────────────────────┘       │
│  · W, Inset  │                                                       │
│              │  ┌─────────────────────┬─────────────────────┐       │
│  DGS Slots   │  │  2D POLAR PATTERN   │  3D RADIATION       │       │
│  · Add slot  │  │  (Plotly)           │  SURFACE (Plotly)   │       │
│  · Slot 1    │  │                     │                     │       │
│  · Slot 2    │  └─────────────────────┴─────────────────────┘       │
│              │                                                       │
│  [Predict]   │  ┌───────────────────────────────────────────┐       │
│              │  │  S₁₁ RETURN LOSS PLOT (Plotly)            │       │
│              │  └───────────────────────────────────────────┘       │
│              │                                                       │
│              │  ▶ PHYSICS REVEAL (expandable) ──────────────        │
│              │    Cavity model equation, DGS circuit, terms          │
│              │                                                       │
│              │  ▶ MODEL COMPARISON (expandable) ────────────        │
│              │    Leaderboard, metrics, feature importance,          │
│              │    learning curves                                    │
│              │                                                       │
├──────────────┴───────────────────────────────────────────────────────┤
│  FOOTER (minimal)                                                    │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Design System (`index.css`)

### Color Tokens

```css
:root {
    /* Background layers */
    --bg-primary: #0a0a1a;
    --bg-secondary: #111128;
    --bg-tertiary: #1a1a3e;

    /* Glass effect */
    --glass-bg: rgba(255, 255, 255, 0.05);
    --glass-border: rgba(255, 255, 255, 0.1);
    --glass-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    --glass-blur: 20px;

    /* Accent colors */
    --accent-primary: #6366f1;     /* Indigo */
    --accent-secondary: #8b5cf6;   /* Violet */
    --accent-success: #22c55e;     /* Green */
    --accent-warning: #f59e0b;     /* Amber */
    --accent-danger: #ef4444;      /* Red */
    --accent-info: #06b6d4;        /* Cyan */

    /* Gradients */
    --gradient-primary: linear-gradient(135deg, #6366f1, #8b5cf6);
    --gradient-surface: linear-gradient(135deg, rgba(99,102,241,0.1), rgba(139,92,246,0.05));

    /* Text */
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;

    /* Typography */
    --font-ui: 'Inter', system-ui, sans-serif;
    --font-mono: 'JetBrains Mono', 'Fira Code', monospace;

    /* Spacing scale */
    --space-xs: 4px;
    --space-sm: 8px;
    --space-md: 16px;
    --space-lg: 24px;
    --space-xl: 32px;
    --space-2xl: 48px;

    /* Border radius */
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-xl: 24px;

    /* Transitions */
    --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
    --transition-normal: 300ms cubic-bezier(0.4, 0, 0.2, 1);
    --transition-slow: 500ms cubic-bezier(0.4, 0, 0.2, 1);
}
```

### Glass Card Component

```css
.glass-card {
    background: var(--glass-bg);
    backdrop-filter: blur(var(--glass-blur));
    -webkit-backdrop-filter: blur(var(--glass-blur));
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    box-shadow: var(--glass-shadow);
    padding: var(--space-lg);
    transition: transform var(--transition-fast), box-shadow var(--transition-fast);
}

.glass-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
}
```

---

## Key Components

### AntennaCanvas (SVG)

Renders a top-down view of the antenna:
- **Ground plane** — dark rectangle (full substrate size)
- **Patch** — colored rectangle centered on substrate
- **Feed line** — narrow rectangle from patch edge
- **DGS slots** — cut-out rectangles on the ground plane (dashed border, different color)
- **Dimension lines** — arrows with labels showing W, L, H values

All dimensions scale proportionally. The canvas auto-zooms to fit the antenna.

### PredictionCards (Animated)

```jsx
// Each card shows one metric with animated number transition
<GlassCard>
    <label>Resonant Frequency</label>
    <AnimatedNumber value={2.41} unit="GHz" precision={3} />
    <span className="delta">-32 MHz from DGS</span>
</GlassCard>
```

Numbers animate smoothly when predictions update (CSS `transition` on `transform`).

### PhysicsReveal (Expandable)

Clicking a prediction card expands a panel below showing:
- The cavity model equation with **actual computed values** substituted in (not just the formula)
- DGS equivalent circuit diagram (drawn in SVG: inductor + capacitor symbols with values)
- Step-by-step derivation: ε_eff → ΔL → L_eff → f_r → Δf_dgs → f_final

### PolarPattern (Plotly)

```javascript
Plotly.newPlot(element, [{
    type: 'scatterpolar',
    r: gainDb,
    theta: thetaDeg,
    mode: 'lines',
    line: { color: '#6366f1', width: 3 },
    fill: 'toself',
    fillcolor: 'rgba(99, 102, 241, 0.1)',
}], {
    polar: {
        radialaxis: { title: 'Gain (dB)', range: [-20, maxGain + 5] },
        angularaxis: { direction: 'clockwise', rotation: 90 },
    },
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'transparent',
    font: { color: '#f1f5f9', family: 'Inter' },
});
```

### ModelArena (Collapsible)

A drawer that expands from the bottom of the page:
- **Leaderboard** — table sorted by overall R², with rank badges (🥇🥈🥉)
- **Per-model metrics** — R², MAE, RMSE for freq and gain
- **Feature importance** — horizontal bar chart (Plotly)
- **Learning curves** — line chart with train/test R² vs dataset size (Plotly)
- **Model predictions** — table showing each model's prediction for the current config

---

## Interaction Flow

```
1. User adjusts sliders in sidebar
       ↓
2. useAntennaConfig updates state
       ↓
3. AntennaCanvas re-renders (instant, local state)
       ↓
4. usePrediction debounces (300ms) then calls POST /api/predict
       ↓
5. PredictionCards animate to new values
       ↓
6. User clicks "Show Pattern" → POST /api/pattern
       ↓
7. PolarPattern + Pattern3D render with Plotly
       ↓
8. User clicks a PredictionCard → PhysicsReveal expands
       ↓
9. User clicks "Model Comparison" → ModelArena expands
       ↓
10. Leaderboard, FeatureImportance, LearningCurves render
```

### Debouncing Strategy

Slider changes trigger many events. Debounce API calls:
- **300ms** for prediction (fast, small payload)
- **500ms** for radiation pattern (larger payload)
- **No debounce** for model comparison (fetched once, cached)

---

## Responsive Considerations

This is a **desktop-only** demo tool (per scope). Minimum viewport: 1280 × 720.
- Sidebar is fixed width (320px)
- Main content fills remaining space
- Plotly charts resize with container

---

## Code Style

```jsx
import { useState, useCallback } from 'react';
import './Controls.css';

/**
 * Slider control for a single antenna dimension.
 * Displays current value with unit, sends changes to parent via onChange.
 */
export function DimensionSlider({ label, value, min, max, step, unit, onChange }) {
    return (
        <div className="dimension-slider">
            <label className="dimension-slider__label">
                {label}
                <span className="dimension-slider__value">
                    {value.toFixed(1)} {unit}
                </span>
            </label>
            <input
                type="range"
                min={min}
                max={max}
                step={step}
                value={value}
                onChange={(e) => onChange(parseFloat(e.target.value))}
                className="dimension-slider__input"
            />
        </div>
    );
}
```

**Conventions:**
- Named exports, no default exports
- One component per file
- BEM-style CSS class names (`component__element--modifier`)
- CSS files colocated with components
- Props documented in JSDoc above the component
- No inline styles — all styling in CSS files
- All interactive elements have unique `id` attributes

---

## Testing Strategy

**Framework:** Manual browser testing (this is a visual UI)  
**Primary verification:** Visual inspection in browser + DevTools console

| Check | How to verify |
|-------|---------------|
| **Layout** | Open in 1280×720 — no overflow, no scrollbar issues |
| **Sliders** | All sliders responsive, values update AntennaCanvas in real-time |
| **API calls** | Network tab shows debounced requests, correct payloads |
| **Prediction cards** | Numbers animate smoothly on change |
| **Plotly charts** | Polar pattern renders, 3D surface rotates, S₁₁ shows dip |
| **Physics reveal** | Expands/collapses, shows actual computed values |
| **Model comparison** | Leaderboard shows all 8 models ranked, charts render |
| **Console errors** | Zero console errors during normal use |
| **Dark mode** | All elements visible, no white flashes, text readable |

---

## Boundaries

### Always Do
- Use CSS custom properties from the design system (no hardcoded colors)
- Debounce API calls from slider changes
- Show loading states during API calls
- Handle API errors gracefully (display message, don't crash)
- Use semantic HTML (`<main>`, `<aside>`, `<section>`, `<header>`)

### Ask First
- Adding new pages or routes (currently single-page)
- Adding third-party UI component libraries
- Adding state management beyond useState/useReducer

### Never Do
- Inline styles
- Direct DOM manipulation (use React refs if needed)
- `console.log` in production code (use a debug flag)
- Block the main thread with heavy computation (all computation is on the backend)

---

## Success Criteria

1. **First impression:** A judge seeing the app for the first time says "wow" — dark, polished, professional
2. **Antenna canvas** updates instantly when sliders change (no visible lag)
3. **Prediction cards** show animated numbers with correct units
4. **2D polar pattern** resembles a real antenna radiation pattern (broadside main lobe, back lobe)
5. **3D radiation surface** renders and is rotatable/zoomable
6. **S₁₁ plot** shows clear resonance dip at the predicted frequency
7. **Physics reveal** shows actual equation terms (not just formulas) — ε_eff = 4.01, ΔL = 0.74mm, etc.
8. **Model comparison** shows all 8 models ranked, with metrics and charts
9. **Zero console errors** during normal operation
10. **Page loads in <3 seconds** on localhost
