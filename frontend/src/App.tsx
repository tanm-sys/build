import React from 'react';
import { Canvas } from '@react-three/fiber';
import { Suspense } from 'react';
import SceneManager from './components/3d/SceneManager';
import ControlPanel from './components/ui/ControlPanel';
import Dashboard from './components/ui/Dashboard';
import Navigation from './components/ui/Navigation';
import { SimulationProvider } from './contexts/SimulationContext';
import { AccessibilityProvider } from './contexts/AccessibilityContext';
import { PerformanceProvider } from './contexts/PerformanceContext';
import './styles/global.css';

/**
 * Main App component for the 3D AI Simulation Visualization Platform
 * Implements WCAG 2.1 accessibility standards and responsive design
 */
const App: React.FC = () => {
  return (
    <AccessibilityProvider>
      <PerformanceProvider>
        <SimulationProvider>
          <div className="app-container">
            <Navigation />

            <main className="main-content" role="main">
              <div className="visualization-section">
                <Canvas
                  camera={{
                    position: [0, 0, 50],
                    fov: 75,
                    near: 0.1,
                    far: 1000
                  }}
                  gl={{
                    antialias: true,
                    alpha: true,
                    powerPreference: "high-performance"
                  }}
                  dpr={[1, 2]}
                  performance={{ min: 0.5 }}
                >
                  <Suspense fallback={null}>
                    <SceneManager />
                  </Suspense>
                </Canvas>
              </div>

              <div className="dashboard-section">
                <Dashboard />
              </div>
            </main>

            <ControlPanel />

            {/* Screen reader announcements */}
            <div
              id="sr-announcements"
              className="sr-only"
              aria-live="polite"
              aria-atomic="true"
            />
          </div>
        </SimulationProvider>
      </PerformanceProvider>
    </AccessibilityProvider>
  );
};

export default App;