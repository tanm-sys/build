import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { AccessibilitySettings } from '../types/simulation';

/**
 * Accessibility Context Provider
 * Manages WCAG 2.1 compliance features and accessibility settings
 * Implements screen reader support, keyboard navigation, and high contrast mode
 */

interface AccessibilityContextType {
  settings: AccessibilitySettings;
  announcements: string[];
  focusElement: string | null;
  isReducedMotion: boolean;
  isHighContrast: boolean;
  dispatch: React.Dispatch<AccessibilityAction>;
}

type AccessibilityAction =
  | { type: 'SET_HIGH_CONTRAST'; payload: boolean }
  | { type: 'SET_REDUCED_MOTION'; payload: boolean }
  | { type: 'SET_SCREEN_READER'; payload: boolean }
  | { type: 'SET_FONT_SIZE'; payload: 'small' | 'medium' | 'large' }
  | { type: 'SET_COLOR_BLIND_MODE'; payload: boolean }
  | { type: 'ADD_ANNOUNCEMENT'; payload: string }
  | { type: 'CLEAR_ANNOUNCEMENTS' }
  | { type: 'SET_FOCUS_ELEMENT'; payload: string | null }
  | { type: 'UPDATE_SETTINGS'; payload: Partial<AccessibilitySettings> };

const initialSettings: AccessibilitySettings = {
  highContrast: false,
  reducedMotion: false,
  screenReader: false,
  fontSize: 'medium',
  colorBlindMode: false
};

const initialState: AccessibilityContextType = {
  settings: initialSettings,
  announcements: [],
  focusElement: null,
  isReducedMotion: false,
  isHighContrast: false,
  dispatch: () => {}
};

const AccessibilityContext = createContext<AccessibilityContextType>(initialState);

export const useAccessibility = () => {
  const context = useContext(AccessibilityContext);
  if (!context) {
    throw new Error('useAccessibility must be used within an AccessibilityProvider');
  }
  return context;
};

interface AccessibilityProviderProps {
  children: ReactNode;
}

export const AccessibilityProvider: React.FC<AccessibilityProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(accessibilityReducer, initialState);

  // Apply accessibility settings to document
  useEffect(() => {
    applyAccessibilitySettings(state.settings);
  }, [state.settings]);

  // Keyboard navigation handler
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      handleKeyboardNavigation(event, state, dispatch);
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [state]);

  // Screen reader announcements
  useEffect(() => {
    if (state.announcements.length > 0 && state.settings.screenReader) {
      announceToScreenReader(state.announcements[state.announcements.length - 1]);
    }
  }, [state.announcements, state.settings.screenReader]);

  return (
    <AccessibilityContext.Provider value={{ ...state, dispatch }}>
      {children}
    </AccessibilityContext.Provider>
  );
};

// Reducer function for accessibility state management
function accessibilityReducer(state: AccessibilityContextType, action: AccessibilityAction): AccessibilityContextType {
  switch (action.type) {
    case 'SET_HIGH_CONTRAST':
      return {
        ...state,
        settings: { ...state.settings, highContrast: action.payload },
        isHighContrast: action.payload
      };

    case 'SET_REDUCED_MOTION':
      return {
        ...state,
        settings: { ...state.settings, reducedMotion: action.payload },
        isReducedMotion: action.payload
      };

    case 'SET_SCREEN_READER':
      return {
        ...state,
        settings: { ...state.settings, screenReader: action.payload }
      };

    case 'SET_FONT_SIZE':
      return {
        ...state,
        settings: { ...state.settings, fontSize: action.payload }
      };

    case 'SET_COLOR_BLIND_MODE':
      return {
        ...state,
        settings: { ...state.settings, colorBlindMode: action.payload }
      };

    case 'ADD_ANNOUNCEMENT':
      return {
        ...state,
        announcements: [...state.announcements, action.payload]
      };

    case 'CLEAR_ANNOUNCEMENTS':
      return {
        ...state,
        announcements: []
      };

    case 'SET_FOCUS_ELEMENT':
      return {
        ...state,
        focusElement: action.payload
      };

    case 'UPDATE_SETTINGS':
      return {
        ...state,
        settings: { ...state.settings, ...action.payload }
      };

    default:
      return state;
  }
}

// Apply accessibility settings to the document
function applyAccessibilitySettings(settings: AccessibilitySettings) {
  const root = document.documentElement;

  // High contrast mode
  if (settings.highContrast) {
    root.classList.add('high-contrast');
  } else {
    root.classList.remove('high-contrast');
  }

  // Reduced motion
  if (settings.reducedMotion) {
    root.classList.add('reduced-motion');
  } else {
    root.classList.remove('reduced-motion');
  }

  // Font size
  root.classList.remove('font-small', 'font-medium', 'font-large');
  root.classList.add(`font-${settings.fontSize}`);

  // Color blind mode
  if (settings.colorBlindMode) {
    root.classList.add('color-blind-mode');
  } else {
    root.classList.remove('color-blind-mode');
  }

  // Screen reader optimizations
  if (settings.screenReader) {
    root.classList.add('screen-reader-mode');
    // Ensure all interactive elements have proper focus indicators
    document.querySelectorAll('button, [role="button"], a, input, select, textarea').forEach(element => {
      element.setAttribute('tabindex', element.getAttribute('tabindex') || '0');
    });
  } else {
    root.classList.remove('screen-reader-mode');
  }
}

// Handle keyboard navigation for 3D scene
function handleKeyboardNavigation(
  event: KeyboardEvent,
  state: AccessibilityContextType,
  dispatch: React.Dispatch<AccessibilityAction>
) {
  // Skip if user is typing in an input
  if (event.target instanceof HTMLInputElement || event.target instanceof HTMLTextAreaElement) {
    return;
  }

  switch (event.key) {
    case 'Tab':
      handleTabNavigation(event, dispatch);
      break;

    case 'Enter':
    case ' ':
      handleActivation(event, state, dispatch);
      break;

    case 'Escape':
      dispatch({ type: 'SET_FOCUS_ELEMENT', payload: null });
      break;

    case 'ArrowUp':
    case 'ArrowDown':
    case 'ArrowLeft':
    case 'ArrowRight':
      handleArrowNavigation(event, state, dispatch);
      break;

    case 'Home':
      dispatch({ type: 'ADD_ANNOUNCEMENT', payload: 'Moved to first element' });
      break;

    case 'End':
      dispatch({ type: 'ADD_ANNOUNCEMENT', payload: 'Moved to last element' });
      break;

    case 'F1':
      if (!event.ctrlKey && !event.altKey) {
        event.preventDefault();
        dispatch({ type: 'ADD_ANNOUNCEMENT', payload: 'Help menu opened' });
      }
      break;
  }
}

// Handle tab navigation
function handleTabNavigation(event: KeyboardEvent, dispatch: React.Dispatch<AccessibilityAction>) {
  const focusableElements = document.querySelectorAll(
    'button, [role="button"], a[href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  );

  const currentIndex = Array.from(focusableElements).findIndex(el => el === document.activeElement);

  if (event.shiftKey) {
    // Shift+Tab - go to previous element
    const prevIndex = currentIndex > 0 ? currentIndex - 1 : focusableElements.length - 1;
    (focusableElements[prevIndex] as HTMLElement)?.focus();
  } else {
    // Tab - go to next element
    const nextIndex = currentIndex < focusableElements.length - 1 ? currentIndex + 1 : 0;
    (focusableElements[nextIndex] as HTMLElement)?.focus();
  }

  event.preventDefault();
}

// Handle element activation
function handleActivation(
  event: KeyboardEvent,
  state: AccessibilityContextType,
  dispatch: React.Dispatch<AccessibilityAction>
) {
  const target = event.target as HTMLElement;

  if (target) {
    // Announce the action to screen readers
    const label = target.getAttribute('aria-label') ||
                 target.textContent ||
                 target.getAttribute('title') ||
                 'Element';

    dispatch({ type: 'ADD_ANNOUNCEMENT', payload: `${label} activated` });

    // Handle specific element types
    if (target.hasAttribute('data-3d-control')) {
      handle3DControlActivation(target, dispatch);
    }
  }

  event.preventDefault();
}

// Handle arrow key navigation for 3D scene
function handleArrowNavigation(
  event: KeyboardEvent,
  state: AccessibilityContextType,
  dispatch: React.Dispatch<AccessibilityAction>
) {
  if (state.focusElement?.startsWith('3d-')) {
    // Handle 3D scene navigation
    const step = event.ctrlKey ? 5 : 1;

    switch (event.key) {
      case 'ArrowUp':
        dispatch({ type: 'ADD_ANNOUNCEMENT', payload: `Camera moved up by ${step} units` });
        break;
      case 'ArrowDown':
        dispatch({ type: 'ADD_ANNOUNCEMENT', payload: `Camera moved down by ${step} units` });
        break;
      case 'ArrowLeft':
        dispatch({ type: 'ADD_ANNOUNCEMENT', payload: `Camera rotated left by ${step} degrees` });
        break;
      case 'ArrowRight':
        dispatch({ type: 'ADD_ANNOUNCEMENT', payload: `Camera rotated right by ${step} degrees` });
        break;
    }
  }

  event.preventDefault();
}

// Handle 3D control activation
function handle3DControlActivation(target: HTMLElement, dispatch: React.Dispatch<AccessibilityAction>) {
  const controlType = target.getAttribute('data-3d-control');

  switch (controlType) {
    case 'rotate':
      dispatch({ type: 'ADD_ANNOUNCEMENT', payload: 'Rotation mode activated. Use arrow keys to rotate the view.' });
      break;
    case 'zoom':
      dispatch({ type: 'ADD_ANNOUNCEMENT', payload: 'Zoom mode activated. Use up and down arrows to zoom in and out.' });
      break;
    case 'pan':
      dispatch({ type: 'ADD_ANNOUNCEMENT', payload: 'Pan mode activated. Use arrow keys to pan the view.' });
      break;
    case 'focus':
      const agentId = target.getAttribute('data-agent-id');
      dispatch({ type: 'ADD_ANNOUNCEMENT', payload: `Focusing on agent ${agentId || 'unknown'}` });
      break;
  }
}

// Announce messages to screen readers
function announceToScreenReader(message: string) {
  const announcement = document.createElement('div');
  announcement.setAttribute('aria-live', 'polite');
  announcement.setAttribute('aria-atomic', 'true');
  announcement.className = 'sr-only';
  announcement.textContent = message;

  document.body.appendChild(announcement);

  // Remove after announcement
  setTimeout(() => {
    document.body.removeChild(announcement);
  }, 1000);
}