import React, { useState, useCallback } from 'react';
import { useSpring, animated } from '@react-spring/web';
import { useAccessibility } from '../../contexts/AccessibilityContext';
import { useSimulation } from '../../contexts/SimulationContext';
import { usePerformance } from '../../contexts/PerformanceContext';

/**
 * Interactive Control Panel Component
 * Provides simulation playback controls and real-time interaction
 * Implements touch-optimized controls for mobile devices
 */

interface ControlButtonProps {
  icon: string;
  label: string;
  onClick: () => void;
  disabled?: boolean;
  active?: boolean;
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'small' | 'medium' | 'large';
  shortcut?: string;
}

const ControlButton: React.FC<ControlButtonProps> = ({
  icon,
  label,
  onClick,
  disabled = false,
  active = false,
  variant = 'primary',
  size = 'medium',
  shortcut
}) => {
  const { settings } = useAccessibility();

  const [isPressed, setIsPressed] = useState(false);

  const { scale, opacity } = useSpring({
    scale: isPressed ? 0.95 : 1,
    opacity: disabled ? 0.5 : 1,
    config: { tension: 300, friction: 10 }
  });

  const handleClick = useCallback(() => {
    if (!disabled) {
      onClick();
    }
  }, [disabled, onClick]);

  const handleKeyDown = useCallback((event: React.KeyboardEvent) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      handleClick();
    }
  }, [handleClick]);

  return (
    <animated.button
      className={`control-button control-button--${variant} control-button--${size} ${active ? 'active' : ''}`}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      onMouseDown={() => setIsPressed(true)}
      onMouseUp={() => setIsPressed(false)}
      onMouseLeave={() => setIsPressed(false)}
      disabled={disabled}
      aria-label={`${label}${shortcut ? ` (${shortcut})` : ''}`}
      aria-pressed={active}
      style={{
        transform: scale.to(s => `scale(${s})`),
        opacity
      }}
    >
      <span className="control-button__icon">{icon}</span>
      <span className="control-button__label">{label}</span>
      {shortcut && (
        <span className="control-button__shortcut">{shortcut}</span>
      )}
    </animated.button>
  );
};

const ControlPanel: React.FC = () => {
  const { simulationState, dispatch } = useSimulation();
  const { settings } = useAccessibility();
  const { metrics } = usePerformance();

  const [isExpanded, setIsExpanded] = useState(false);

  const { height, opacity } = useSpring({
    height: isExpanded ? 200 : 60,
    opacity: isExpanded ? 1 : 0.9,
    config: { tension: 280, friction: 30 }
  });

  const handlePlayPause = useCallback(() => {
    const newStatus = simulationState.status === 'running' ? 'paused' : 'running';
    dispatch({
      type: 'SET_SIMULATION_STATE',
      payload: { ...simulationState, status: newStatus }
    });
  }, [simulationState, dispatch]);

  const handleStop = useCallback(() => {
    dispatch({
      type: 'SET_SIMULATION_STATE',
      payload: { ...simulationState, status: 'stopped' }
    });
  }, [simulationState, dispatch]);

  const handleReset = useCallback(() => {
    dispatch({ type: 'RESET_METRICS' });
    // Reset simulation to initial state
  }, [dispatch]);

  const handleExport = useCallback(() => {
    // Export current simulation state
    const dataStr = JSON.stringify({
      simulationState,
      timestamp: Date.now()
    }, null, 2);

    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);

    const link = document.createElement('a');
    link.href = url;
    link.download = `simulation-export-${Date.now()}.json`;
    link.click();

    URL.revokeObjectURL(url);
  }, [simulationState]);

  const toggleExpanded = useCallback(() => {
    setIsExpanded(prev => !prev);
  }, []);

  return (
    <animated.div
      className={`control-panel ${settings.highContrast ? 'high-contrast' : ''}`}
      style={{ height: height.to(h => `${h}px`) }}
    >
      <div className="control-panel__header">
        <h2 className="control-panel__title">Simulation Controls</h2>
        <ControlButton
          icon={isExpanded ? '−' : '+'}
          label={isExpanded ? 'Collapse' : 'Expand'}
          onClick={toggleExpanded}
          size="small"
          variant="secondary"
        />
      </div>

      <animated.div
        className="control-panel__content"
        style={{ opacity }}
      >
        <div className="control-panel__main-controls">
          <ControlButton
            icon={simulationState.status === 'running' ? '⏸' : '▶'}
            label={simulationState.status === 'running' ? 'Pause' : 'Play'}
            onClick={handlePlayPause}
            active={simulationState.status === 'running'}
            shortcut="Space"
            size="large"
          />

          <ControlButton
            icon="⏹"
            label="Stop"
            onClick={handleStop}
            disabled={simulationState.status === 'stopped'}
            variant="danger"
            shortcut="Ctrl+S"
          />

          <ControlButton
            icon="↻"
            label="Reset"
            onClick={handleReset}
            variant="secondary"
            shortcut="Ctrl+R"
          />
        </div>

        <div className="control-panel__secondary-controls">
          <ControlButton
            icon="📊"
            label="Export Data"
            onClick={handleExport}
            variant="secondary"
            size="small"
          />

          <ControlButton
            icon="⚙"
            label="Settings"
            onClick={() => {/* Open settings modal */}}
            variant="secondary"
            size="small"
          />
        </div>

        <div className="control-panel__status">
          <div className="status-indicator">
            <span
              className={`status-dot status-dot--${simulationState.status}`}
              aria-label={`Simulation status: ${simulationState.status}`}
            />
            <span className="status-text">
              Status: {simulationState.status.charAt(0).toUpperCase() + simulationState.status.slice(1)}
            </span>
          </div>

          <div className="performance-metrics">
            <span className="metric">
              <span className="metric__label">FPS:</span>
              <span className="metric__value">{metrics.fps}</span>
            </span>
            <span className="metric">
              <span className="metric__label">Agents:</span>
              <span className="metric__value">{simulationState.activeAgents}</span>
            </span>
            <span className="metric">
              <span className="metric__label">Trust:</span>
              <span className="metric__value">{simulationState.averageTrustScore}%</span>
            </span>
          </div>
        </div>

        {/* Progress bar for loading states */}
        {simulationState.status === 'anomaly_detected' && (
          <div className="progress-container">
            <div className="progress-bar">
              <div
                className="progress-fill progress-fill--warning"
                style={{ width: '100%' }}
              />
            </div>
            <span className="progress-label">Anomaly Detected</span>
          </div>
        )}
      </animated.div>
    </animated.div>
  );
};

export default ControlPanel;