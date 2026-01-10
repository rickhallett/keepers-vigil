# IMP-0010: Mobile Responsive UI for All Core Features

**Priority:** HIGH
**Category:** ux_mobile
**Effort:** high
**Status:** proposed

## Affected Files

- `frontend/src/styles/game.css`
- `frontend/src/components/*.tsx`
- `frontend/index.html`

## Problem Statement

The current mobile experience has minimal responsiveness (only a basic `@media (max-width: 600px)` query). Key issues:

1. **Virtual keyboard coverage** - Input gets hidden when keyboard opens
2. **Touch targets too small** - Hard to tap on mobile
3. **Status bar takes too much space** - Reduces narrative reading area
4. **No safe area handling** - Content clips on notched devices (iPhone X+)
5. **No quick actions** - Common commands require full typing
6. **Loading state not prominent** - Users may not notice processing
7. **Landscape orientation** - Not optimized for horizontal use

## Current State Analysis

```css
/* Current mobile styles (insufficient) */
@media (max-width: 600px) {
  :root { font-size: 16px; }
  .game-container { padding: var(--spacing-sm); }
  .start-screen h1 { font-size: 1.8rem; }
  .status-bar { flex-direction: column; gap: var(--spacing-xs); }
  .status-inventory { text-align: left; }
}
```

## Proposed Solution

### 1. Add Mobile-Specific CSS Variables

```css
/* frontend/src/styles/game.css */
:root {
  /* Existing variables... */

  /* Mobile-specific */
  --touch-target-min: 44px;  /* Apple HIG minimum */
  --safe-area-top: env(safe-area-inset-top, 0px);
  --safe-area-bottom: env(safe-area-inset-bottom, 0px);
  --safe-area-left: env(safe-area-inset-left, 0px);
  --safe-area-right: env(safe-area-inset-right, 0px);
}
```

### 2. Update index.html for Mobile

```html
<!-- frontend/index.html -->
<head>
  <!-- Existing meta tags... -->
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover, maximum-scale=1.0, user-scalable=no" />
  <meta name="theme-color" content="#0d0d0d" />
  <meta name="apple-mobile-web-app-capable" content="yes" />
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
</head>
```

### 3. Comprehensive Mobile Styles

```css
/* frontend/src/styles/game.css - Enhanced mobile section */

/* Tablet breakpoint */
@media (max-width: 768px) {
  .game-container {
    padding: var(--spacing-sm);
    padding-left: calc(var(--spacing-sm) + var(--safe-area-left));
    padding-right: calc(var(--spacing-sm) + var(--safe-area-right));
  }

  .narrative-entry {
    margin-bottom: var(--spacing-md);
  }
}

/* Mobile breakpoint */
@media (max-width: 600px) {
  :root {
    font-size: 16px;
    --spacing-md: 0.75rem;
    --spacing-lg: 1.5rem;
  }

  html, body {
    /* Prevent overscroll bounce */
    overscroll-behavior: none;
    /* Prevent text size adjustment */
    -webkit-text-size-adjust: 100%;
  }

  /* Game container - full viewport with safe areas */
  .game-container {
    padding: var(--spacing-sm);
    padding-top: calc(var(--spacing-sm) + var(--safe-area-top));
    padding-bottom: calc(var(--spacing-sm) + var(--safe-area-bottom));
    padding-left: calc(var(--spacing-sm) + var(--safe-area-left));
    padding-right: calc(var(--spacing-sm) + var(--safe-area-right));
    height: 100dvh; /* Dynamic viewport height for mobile */
  }

  /* Start screen - touch-friendly */
  .start-screen {
    padding: var(--spacing-lg);
    justify-content: flex-start;
    padding-top: 20vh;
  }

  .start-screen h1 {
    font-size: 1.6rem;
    letter-spacing: 0.15em;
  }

  .start-screen .subtitle {
    font-size: 1rem;
    margin-bottom: var(--spacing-lg);
  }

  .start-button {
    padding: var(--spacing-md) var(--spacing-xl);
    min-height: var(--touch-target-min);
    font-size: 1rem;
    width: 100%;
    max-width: 280px;
  }

  /* Status bar - collapsible on mobile */
  .status-bar {
    flex-direction: column;
    gap: var(--spacing-xs);
    padding: var(--spacing-xs) var(--spacing-sm);
    font-size: 0.75rem;
    background: var(--bg-primary);
    position: sticky;
    top: 0;
    z-index: 10;
  }

  .status-bar.collapsed {
    flex-direction: row;
    justify-content: space-between;
  }

  .status-bar.collapsed .status-exits,
  .status-bar.collapsed .status-inventory {
    display: none;
  }

  .status-toggle {
    display: block;
    position: absolute;
    right: var(--spacing-sm);
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: none;
    color: var(--text-secondary);
    font-size: 0.8rem;
    padding: var(--spacing-xs);
    min-width: var(--touch-target-min);
    min-height: var(--touch-target-min);
  }

  /* Narrative display - optimized for reading */
  .narrative-display {
    flex: 1;
    padding: var(--spacing-sm) 0;
    font-size: 1rem;
    line-height: 1.6;
    /* Smooth scrolling on iOS */
    -webkit-overflow-scrolling: touch;
  }

  .narrative-entry {
    margin-bottom: var(--spacing-md);
    padding: 0 var(--spacing-xs);
  }

  .narrative-player {
    font-size: 0.9rem;
    padding-left: var(--spacing-sm);
  }

  /* Command input - fixed at bottom, above keyboard */
  .command-input {
    position: sticky;
    bottom: 0;
    padding: var(--spacing-sm);
    padding-bottom: calc(var(--spacing-sm) + var(--safe-area-bottom));
    background: var(--bg-secondary);
    border-top: 1px solid var(--border);
    z-index: 20;
  }

  .command-input input {
    font-size: 16px; /* Prevents iOS zoom on focus */
    min-height: var(--touch-target-min);
    padding: var(--spacing-sm);
  }

  .command-input .prompt {
    min-width: var(--touch-target-min);
    min-height: var(--touch-target-min);
    display: flex;
    align-items: center;
    justify-content: center;
  }

  /* Quick actions bar for common commands */
  .quick-actions {
    display: flex;
    gap: var(--spacing-xs);
    padding: var(--spacing-xs) 0;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
  }

  .quick-actions::-webkit-scrollbar {
    display: none;
  }

  .quick-action-btn {
    flex-shrink: 0;
    background: var(--bg-primary);
    border: 1px solid var(--border);
    color: var(--text-secondary);
    padding: var(--spacing-xs) var(--spacing-sm);
    border-radius: 4px;
    font-family: var(--font-ui);
    font-size: 0.75rem;
    min-height: 36px;
    white-space: nowrap;
  }

  .quick-action-btn:active {
    background: var(--border);
    color: var(--text-primary);
  }

  /* Loading indicator - more prominent on mobile */
  .narrative-loading {
    padding: var(--spacing-md);
    text-align: center;
    font-size: 1.2rem;
  }

  .loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(13, 13, 13, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 100;
  }

  .loading-overlay .loading-text {
    color: var(--text-primary);
    font-size: 1.1rem;
    animation: pulse 1.5s infinite;
  }

  /* Error message - touch dismissible */
  .error-message {
    padding: var(--spacing-md);
    margin: var(--spacing-sm);
    border-radius: 4px;
    background: rgba(184, 90, 90, 0.1);
  }
}

/* Small mobile breakpoint */
@media (max-width: 375px) {
  :root {
    font-size: 14px;
  }

  .start-screen h1 {
    font-size: 1.4rem;
  }

  .status-bar {
    font-size: 0.7rem;
  }

  .quick-action-btn {
    font-size: 0.7rem;
    padding: var(--spacing-xs);
  }
}

/* Landscape orientation */
@media (max-height: 500px) and (orientation: landscape) {
  .game-container {
    flex-direction: row;
    gap: var(--spacing-md);
  }

  .narrative-display {
    flex: 2;
    height: 100%;
  }

  .command-input-wrapper {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
  }

  .status-bar {
    position: absolute;
    top: var(--spacing-xs);
    right: var(--spacing-xs);
    flex-direction: row;
    background: rgba(13, 13, 13, 0.9);
    padding: var(--spacing-xs);
    border-radius: 4px;
    font-size: 0.7rem;
  }

  .start-screen {
    padding-top: var(--spacing-lg);
  }

  .quick-actions {
    flex-wrap: wrap;
  }
}

/* Keyboard visible detection (via JS) */
.keyboard-visible .narrative-display {
  max-height: 40vh;
}

.keyboard-visible .status-bar {
  display: none;
}

.keyboard-visible .quick-actions {
  display: none;
}

/* Touch-specific styles */
@media (hover: none) and (pointer: coarse) {
  /* Larger touch targets */
  .start-button,
  .quick-action-btn {
    min-height: 48px;
  }

  /* Remove hover effects that don't work on touch */
  .start-button:hover {
    background: transparent;
    color: var(--accent);
  }

  /* Active state instead */
  .start-button:active {
    background: var(--accent);
    color: var(--bg-primary);
  }

  /* Tap highlight */
  .narrative-entry {
    -webkit-tap-highlight-color: rgba(201, 169, 89, 0.1);
  }

  /* Disable text selection on UI elements */
  .status-bar,
  .command-input,
  .quick-actions {
    user-select: none;
    -webkit-user-select: none;
  }
}

/* Reduced motion preference */
@media (prefers-reduced-motion: reduce) {
  .narrative-entry {
    animation: none;
  }

  .cursor {
    animation: none;
    opacity: 1;
  }

  .loading-dots {
    animation: none;
    opacity: 1;
  }
}

/* Dark mode preference (already dark, but ensure consistency) */
@media (prefers-color-scheme: dark) {
  :root {
    color-scheme: dark;
  }
}
```

### 4. New Quick Actions Component

```tsx
// frontend/src/components/QuickActions.tsx
import '../styles/game.css';

interface QuickActionsProps {
  onAction: (command: string) => void;
  disabled: boolean;
  currentRoom: string;
}

const COMMON_ACTIONS = [
  { label: 'Look', command: 'look' },
  { label: 'Inventory', command: 'inventory' },
  { label: 'Help', command: 'help' },
];

const ROOM_ACTIONS: Record<string, Array<{ label: string; command: string }>> = {
  threshold: [
    { label: 'Talk to Traveler', command: 'talk to traveler' },
    { label: 'Go Archive', command: 'go archive' },
  ],
  archive: [
    { label: 'Examine Diagrams', command: 'examine technical diagrams' },
    { label: 'Go Threshold', command: 'go threshold' },
  ],
  keeper_cell: [
    { label: 'Examine Journal', command: 'examine keeper journal' },
    { label: 'Go Letters', command: 'go letter room' },
  ],
  letter_room: [
    { label: 'Examine Letters', command: 'examine letter collection' },
    { label: 'Go Back', command: 'go keeper cell' },
  ],
  passage: [
    { label: 'Examine Doorway', command: 'examine doorway' },
    { label: 'Go Back', command: 'go archive' },
  ],
};

export function QuickActions({ onAction, disabled, currentRoom }: QuickActionsProps) {
  const roomActions = ROOM_ACTIONS[currentRoom] || [];
  const allActions = [...COMMON_ACTIONS, ...roomActions];

  return (
    <div className="quick-actions">
      {allActions.map((action) => (
        <button
          key={action.command}
          className="quick-action-btn"
          onClick={() => onAction(action.command)}
          disabled={disabled}
        >
          {action.label}
        </button>
      ))}
    </div>
  );
}
```

### 5. Collapsible Status Bar Component Update

```tsx
// frontend/src/components/StatusBar.tsx
import { useState } from 'react';
import '../styles/game.css';

interface StatusBarProps {
  currentRoom: string;
  inventory: string[];
  exits: string[];
}

const ROOM_NAMES: Record<string, string> = {
  threshold: 'The Threshold',
  keeper_cell: "The Keeper's Cell",
  archive: 'The Archive',
  letter_room: 'The Letter Room',
  passage: 'The Passage',
};

export function StatusBar({ currentRoom, inventory, exits }: StatusBarProps) {
  const [collapsed, setCollapsed] = useState(false);
  const roomName = ROOM_NAMES[currentRoom] || currentRoom;
  const exitNames = exits.map(e => ROOM_NAMES[e] || e);

  return (
    <div className={`status-bar ${collapsed ? 'collapsed' : ''}`}>
      <div className="status-room">
        <span className="status-label">Location:</span>
        <span className="status-value">{roomName}</span>
      </div>

      {!collapsed && (
        <>
          <div className="status-exits">
            <span className="status-label">Exits:</span>
            <span className="status-value">{exitNames.join(', ') || 'none'}</span>
          </div>

          {inventory.length > 0 && (
            <div className="status-inventory">
              <span className="status-label">Carrying:</span>
              <span className="status-value">{inventory.join(', ')}</span>
            </div>
          )}
        </>
      )}

      <button
        className="status-toggle"
        onClick={() => setCollapsed(!collapsed)}
        aria-label={collapsed ? 'Expand status bar' : 'Collapse status bar'}
      >
        {collapsed ? '▼' : '▲'}
      </button>
    </div>
  );
}
```

### 6. Virtual Keyboard Detection Hook

```tsx
// frontend/src/hooks/useKeyboardVisibility.ts
import { useState, useEffect } from 'react';

export function useKeyboardVisibility() {
  const [isKeyboardVisible, setIsKeyboardVisible] = useState(false);

  useEffect(() => {
    // Only run on mobile
    if (typeof window === 'undefined' || !('visualViewport' in window)) {
      return;
    }

    const viewport = window.visualViewport;
    if (!viewport) return;

    const handleResize = () => {
      // Keyboard is likely visible if viewport height is significantly less than window height
      const heightDiff = window.innerHeight - viewport.height;
      setIsKeyboardVisible(heightDiff > 150);
    };

    viewport.addEventListener('resize', handleResize);
    viewport.addEventListener('scroll', handleResize);

    return () => {
      viewport.removeEventListener('resize', handleResize);
      viewport.removeEventListener('scroll', handleResize);
    };
  }, []);

  return isKeyboardVisible;
}
```

### 7. Updated App Component with Mobile Features

```tsx
// frontend/src/App.tsx
import { useGameState } from './hooks/useGameState';
import { useKeyboardVisibility } from './hooks/useKeyboardVisibility';
import { NarrativeDisplay } from './components/NarrativeDisplay';
import { CommandInput } from './components/CommandInput';
import { StatusBar } from './components/StatusBar';
import { QuickActions } from './components/QuickActions';
import './styles/game.css';

function App() {
  const {
    gameStarted,
    isLoading,
    error,
    narrative,
    currentRoom,
    inventory,
    exits,
    startNewGame,
    sendCommand,
  } = useGameState();

  const isKeyboardVisible = useKeyboardVisibility();

  if (!gameStarted) {
    return (
      <div className="game-container">
        <div className="start-screen">
          <h1>THE LAST VIGIL</h1>
          <p className="subtitle">A story of endings and beginnings</p>
          <button
            className="start-button"
            onClick={startNewGame}
            disabled={isLoading}
          >
            {isLoading ? 'Awakening...' : 'Begin'}
          </button>
          {error && <p className="error-message">{error}</p>}
        </div>
      </div>
    );
  }

  return (
    <div className={`game-container ${isKeyboardVisible ? 'keyboard-visible' : ''}`}>
      <StatusBar currentRoom={currentRoom} inventory={inventory} exits={exits} />
      <NarrativeDisplay entries={narrative} isLoading={isLoading} />

      <div className="command-input-wrapper">
        <QuickActions
          onAction={sendCommand}
          disabled={isLoading}
          currentRoom={currentRoom}
        />
        <CommandInput onSubmit={sendCommand} disabled={isLoading} />
      </div>

      {error && <p className="error-message">{error}</p>}

      {isLoading && (
        <div className="loading-overlay" aria-live="polite">
          <span className="loading-text">The station contemplates...</span>
        </div>
      )}
    </div>
  );
}

export default App;
```

## Implementation Steps

1. Update `frontend/index.html` with mobile meta tags
2. Add CSS variables for safe areas and touch targets
3. Implement comprehensive mobile breakpoints in CSS
4. Create `QuickActions` component
5. Update `StatusBar` with collapse functionality
6. Create `useKeyboardVisibility` hook
7. Update `App.tsx` to integrate mobile features
8. Test on multiple devices (iOS Safari, Android Chrome)
9. Test landscape orientation
10. Test with screen readers for accessibility

## Testing Checklist

- [ ] iPhone SE (375px width) - smallest common mobile
- [ ] iPhone 14 Pro (390px) - with notch/dynamic island
- [ ] iPhone 14 Pro Max (430px) - large phone
- [ ] iPad Mini (768px) - tablet
- [ ] Android phone (various) - Chrome browser
- [ ] Landscape mode on all above
- [ ] Virtual keyboard open/close
- [ ] Safe area handling on notched devices
- [ ] Touch targets are 44px minimum
- [ ] Text is readable without zooming
- [ ] Quick actions work correctly
- [ ] Status bar collapses/expands
- [ ] Loading overlay is visible
- [ ] Reduced motion preference respected

## Success Criteria

- All core features usable on mobile without zooming
- Touch targets meet 44px minimum (Apple HIG)
- No content clipped by notches or home indicators
- Virtual keyboard doesn't obscure input
- Quick actions reduce typing needed by 50%
- Works in both portrait and landscape
