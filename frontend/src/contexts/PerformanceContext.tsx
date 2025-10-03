import React, { createContext, useContext, useReducer, useEffect, useRef, ReactNode } from 'react';
import { PerformanceMetrics, QualitySettings } from '../types/simulation';

/**
 * Performance Context Provider
 * Monitors and optimizes rendering performance
 * Implements adaptive quality management for 60+ FPS target
 */

interface PerformanceContextType {
  metrics: PerformanceMetrics;
  performanceLevel: 'low' | 'medium' | 'high';
  adaptiveQuality: boolean;
  targetFPS: number;
  isMonitoring: boolean;
  dispatch: React.Dispatch<PerformanceAction>;
}

type PerformanceAction =
  | { type: 'UPDATE_METRICS'; payload: Partial<PerformanceMetrics> }
  | { type: 'SET_PERFORMANCE_LEVEL'; payload: 'low' | 'medium' | 'high' }
  | { type: 'SET_ADAPTIVE_QUALITY'; payload: boolean }
  | { type: 'SET_TARGET_FPS'; payload: number }
  | { type: 'SET_MONITORING'; payload: boolean }
  | { type: 'RESET_METRICS' };

const initialMetrics: PerformanceMetrics = {
  fps: 60,
  frameTime: 16.67,
  memoryUsage: 0,
  drawCalls: 0,
  triangles: 0
};

const initialState: PerformanceContextType = {
  metrics: initialMetrics,
  performanceLevel: 'high',
  adaptiveQuality: true,
  targetFPS: 60,
  isMonitoring: true,
  dispatch: () => {}
};

const PerformanceContext = createContext<PerformanceContextType>(initialState);

export const usePerformance = () => {
  const context = useContext(PerformanceContext);
  if (!context) {
    throw new Error('usePerformance must be used within a PerformanceProvider');
  }
  return context;
};

interface PerformanceProviderProps {
  children: ReactNode;
}

export const PerformanceProvider: React.FC<PerformanceProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(performanceReducer, initialState);
  const frameCountRef = useRef(0);
  const lastTimeRef = useRef(performance.now());
  const fpsHistoryRef = useRef<number[]>([]);

  // Performance monitoring loop
  useEffect(() => {
    if (!state.isMonitoring) return;

    let animationFrameId: number;

    const monitorPerformance = (currentTime: number) => {
      frameCountRef.current++;

      // Calculate FPS every second
      if (currentTime - lastTimeRef.current >= 1000) {
        const fps = Math.round((frameCountRef.current * 1000) / (currentTime - lastTimeRef.current));
        const frameTime = (currentTime - lastTimeRef.current) / frameCountRef.current;

        // Update FPS history for adaptive quality calculation
        fpsHistoryRef.current.push(fps);
        if (fpsHistoryRef.current.length > 60) {
          fpsHistoryRef.current.shift(); // Keep last 60 seconds
        }

        // Get memory usage if available
        const memoryInfo = (performance as any).memory;
        const memoryUsage = memoryInfo ? memoryInfo.usedJSHeapSize / memoryInfo.jsHeapSizeLimit : 0;

        // Update metrics
        dispatch({
          type: 'UPDATE_METRICS',
          payload: {
            fps,
            frameTime,
            memoryUsage,
            drawCalls: 0, // Would need to get from Three.js stats
            triangles: 0  // Would need to get from Three.js stats
          }
        });

        // Adaptive quality management
        if (state.adaptiveQuality) {
          updateAdaptiveQuality(fps, dispatch);
        }

        frameCountRef.current = 0;
        lastTimeRef.current = currentTime;
      }

      if (state.isMonitoring) {
        animationFrameId = requestAnimationFrame(monitorPerformance);
      }
    };

    animationFrameId = requestAnimationFrame(monitorPerformance);

    return () => {
      if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
      }
    };
  }, [state.isMonitoring, state.adaptiveQuality]);

  // Monitor WebGL performance
  useEffect(() => {
    const canvas = document.querySelector('canvas');
    if (!canvas) return;

    const context = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
    if (!context) return;

    const debugInfo = context.getExtension('WEBGL_debug_renderer_info');
    if (debugInfo) {
      const renderer = context.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
      console.log('WebGL Renderer:', renderer);
    }
  }, []);

  return (
    <PerformanceContext.Provider value={{ ...state, dispatch }}>
      {children}
    </PerformanceContext.Provider>
  );
};

// Reducer function for performance state management
function performanceReducer(state: PerformanceContextType, action: PerformanceAction): PerformanceContextType {
  switch (action.type) {
    case 'UPDATE_METRICS':
      return {
        ...state,
        metrics: { ...state.metrics, ...action.payload }
      };

    case 'SET_PERFORMANCE_LEVEL':
      return {
        ...state,
        performanceLevel: action.payload
      };

    case 'SET_ADAPTIVE_QUALITY':
      return {
        ...state,
        adaptiveQuality: action.payload
      };

    case 'SET_TARGET_FPS':
      return {
        ...state,
        targetFPS: action.payload
      };

    case 'SET_MONITORING':
      return {
        ...state,
        isMonitoring: action.payload
      };

    case 'RESET_METRICS':
      return {
        ...state,
        metrics: initialMetrics
      };

    default:
      return state;
  }
}

// Adaptive quality management based on FPS
function updateAdaptiveQuality(fps: number, dispatch: React.Dispatch<PerformanceAction>) {
  const avgFPS = fps; // In a real implementation, calculate average from history

  if (avgFPS < 30 && fps < 30) {
    // Poor performance - reduce quality
    dispatch({ type: 'SET_PERFORMANCE_LEVEL', payload: 'low' });
  } else if (avgFPS >= 30 && avgFPS < 50) {
    // Medium performance
    dispatch({ type: 'SET_PERFORMANCE_LEVEL', payload: 'medium' });
  } else if (avgFPS >= 50) {
    // Good performance - can use high quality
    dispatch({ type: 'SET_PERFORMANCE_LEVEL', payload: 'high' });
  }
}

// Quality settings based on performance level
export function getQualitySettings(performanceLevel: 'low' | 'medium' | 'high'): QualitySettings {
  switch (performanceLevel) {
    case 'low':
      return {
        shadowMapSize: 512,
        particleCount: 300,
        geometryDetail: 'low',
        antialias: false
      };

    case 'medium':
      return {
        shadowMapSize: 1024,
        particleCount: 600,
        geometryDetail: 'medium',
        antialias: true
      };

    case 'high':
    default:
      return {
        shadowMapSize: 2048,
        particleCount: 1000,
        geometryDetail: 'high',
        antialias: true
      };
  }
}

// Performance optimization utilities
export class PerformanceOptimizer {
  private static instance: PerformanceOptimizer;
  private observers: PerformanceObserver[] = [];

  static getInstance(): PerformanceOptimizer {
    if (!PerformanceOptimizer.instance) {
      PerformanceOptimizer.instance = new PerformanceOptimizer();
    }
    return PerformanceOptimizer.instance;
  }

  startMonitoring() {
    if (typeof PerformanceObserver === 'undefined') return;

    // Monitor long tasks
    try {
      const longTaskObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.duration > 50) {
            console.warn('Long task detected:', entry);
          }
        }
      });
      longTaskObserver.observe({ entryTypes: ['longtask'] });
      this.observers.push(longTaskObserver);
    } catch (e) {
      console.warn('Long task monitoring not supported');
    }

    // Monitor layout shifts
    try {
      const layoutShiftObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if ((entry as any).value > 0.1) {
            console.warn('Layout shift detected:', entry);
          }
        }
      });
      layoutShiftObserver.observe({ entryTypes: ['layout-shift'] });
      this.observers.push(layoutShiftObserver);
    } catch (e) {
      console.warn('Layout shift monitoring not supported');
    }
  }

  stopMonitoring() {
    this.observers.forEach(observer => observer.disconnect());
    this.observers = [];
  }

  getMemoryUsage(): { used: number; total: number; limit: number } | null {
    const memory = (performance as any).memory;
    if (memory) {
      return {
        used: memory.usedJSHeapSize,
        total: memory.totalJSHeapSize,
        limit: memory.jsHeapSizeLimit
      };
    }
    return null;
  }

  forceGarbageCollection() {
    if ('gc' in window) {
      (window as any).gc();
    }
  }
}