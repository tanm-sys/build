import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { Agent, SimulationState, TrustScoreData, WebSocketMessage } from '../types/simulation';

/**
 * Simulation Context Provider
 * Manages global simulation state and real-time updates
 * Implements WebSocket integration for live data streaming
 */

interface SimulationContextType {
  simulationState: SimulationState;
  agents: Agent[];
  trustScores: TrustScoreData[];
  isConnected: boolean;
  lastUpdate: number;
  dispatch: React.Dispatch<SimulationAction>;
}

type SimulationAction =
  | { type: 'SET_SIMULATION_STATE'; payload: SimulationState }
  | { type: 'UPDATE_AGENTS'; payload: Agent[] }
  | { type: 'UPDATE_TRUST_SCORES'; payload: TrustScoreData[] }
  | { type: 'SET_CONNECTION_STATUS'; payload: boolean }
  | { type: 'SET_LAST_UPDATE'; payload: number }
  | { type: 'ADD_AGENT'; payload: Agent }
  | { type: 'UPDATE_AGENT'; payload: { id: string; updates: Partial<Agent> } }
  | { type: 'REMOVE_AGENT'; payload: string }
  | { type: 'ADD_TRUST_SCORE'; payload: TrustScoreData }
  | { type: 'UPDATE_TRUST_SCORE'; payload: { id: string; updates: Partial<TrustScoreData> } }
  | { type: 'REMOVE_TRUST_SCORE'; payload: string };

const initialSimulationState: SimulationState = {
  status: 'stopped',
  timestamp: Date.now(),
  activeAgents: 0,
  totalConnections: 0,
  averageTrustScore: 0,
  anomalies: []
};

const initialState: SimulationContextType = {
  simulationState: initialSimulationState,
  agents: [],
  trustScores: [],
  isConnected: false,
  lastUpdate: Date.now(),
  dispatch: () => {}
};

const SimulationContext = createContext<SimulationContextType>(initialState);

export const useSimulation = () => {
  const context = useContext(SimulationContext);
  if (!context) {
    throw new Error('useSimulation must be used within a SimulationProvider');
  }
  return context;
};

interface SimulationProviderProps {
  children: ReactNode;
}

export const SimulationProvider: React.FC<SimulationProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(simulationReducer, initialState);

  // WebSocket connection for real-time updates
  useEffect(() => {
    let ws: WebSocket | null = null;
    let reconnectTimeout: NodeJS.Timeout;

    const connectWebSocket = () => {
      try {
        // In a real application, this would connect to your backend WebSocket server
        ws = new WebSocket('ws://localhost:8080/simulation');

        ws.onopen = () => {
          console.log('WebSocket connected');
          dispatch({ type: 'SET_CONNECTION_STATUS', payload: true });
        };

        ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            handleWebSocketMessage(message, dispatch);
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        };

        ws.onclose = () => {
          console.log('WebSocket disconnected');
          dispatch({ type: 'SET_CONNECTION_STATUS', payload: false });

          // Attempt to reconnect after 5 seconds
          reconnectTimeout = setTimeout(connectWebSocket, 5000);
        };

        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          dispatch({ type: 'SET_CONNECTION_STATUS', payload: false });
        };
      } catch (error) {
        console.error('Failed to connect WebSocket:', error);
        dispatch({ type: 'SET_CONNECTION_STATUS', payload: false });
      }
    };

    connectWebSocket();

    return () => {
      if (ws) {
        ws.close();
      }
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }
    };
  }, []);

  // Auto-refresh simulation data when connected
  useEffect(() => {
    if (!state.isConnected) return;

    const interval = setInterval(() => {
      // In a real application, this would fetch fresh data from your backend
      // For now, we'll simulate some data updates
      simulateDataUpdates(dispatch);
    }, 1000);

    return () => clearInterval(interval);
  }, [state.isConnected]);

  return (
    <SimulationContext.Provider value={{ ...state, dispatch }}>
      {children}
    </SimulationContext.Provider>
  );
};

// Reducer function for simulation state management
function simulationReducer(state: SimulationContextType, action: SimulationAction): SimulationContextType {
  switch (action.type) {
    case 'SET_SIMULATION_STATE':
      return {
        ...state,
        simulationState: action.payload,
        lastUpdate: Date.now()
      };

    case 'UPDATE_AGENTS':
      return {
        ...state,
        agents: action.payload,
        lastUpdate: Date.now()
      };

    case 'UPDATE_TRUST_SCORES':
      return {
        ...state,
        trustScores: action.payload,
        lastUpdate: Date.now()
      };

    case 'SET_CONNECTION_STATUS':
      return {
        ...state,
        isConnected: action.payload,
        lastUpdate: Date.now()
      };

    case 'SET_LAST_UPDATE':
      return {
        ...state,
        lastUpdate: action.payload
      };

    case 'ADD_AGENT':
      return {
        ...state,
        agents: [...state.agents, action.payload],
        simulationState: {
          ...state.simulationState,
          activeAgents: state.agents.length + 1,
          lastUpdate: Date.now()
        }
      };

    case 'UPDATE_AGENT':
      return {
        ...state,
        agents: state.agents.map(agent =>
          agent.id === action.payload.id
            ? { ...agent, ...action.payload.updates }
            : agent
        ),
        lastUpdate: Date.now()
      };

    case 'REMOVE_AGENT':
      return {
        ...state,
        agents: state.agents.filter(agent => agent.id !== action.payload),
        simulationState: {
          ...state.simulationState,
          activeAgents: state.agents.length - 1,
          lastUpdate: Date.now()
        }
      };

    case 'ADD_TRUST_SCORE':
      return {
        ...state,
        trustScores: [...state.trustScores, action.payload],
        lastUpdate: Date.now()
      };

    case 'UPDATE_TRUST_SCORE':
      return {
        ...state,
        trustScores: state.trustScores.map(score =>
          score.id === action.payload.id
            ? { ...score, ...action.payload.updates }
            : score
        ),
        lastUpdate: Date.now()
      };

    case 'REMOVE_TRUST_SCORE':
      return {
        ...state,
        trustScores: state.trustScores.filter(score => score.id !== action.payload),
        lastUpdate: Date.now()
      };

    default:
      return state;
  }
}

// Handle incoming WebSocket messages
function handleWebSocketMessage(message: WebSocketMessage, dispatch: React.Dispatch<SimulationAction>) {
  switch (message.type) {
    case 'simulation_update':
      dispatch({ type: 'SET_SIMULATION_STATE', payload: message.data });
      break;

    case 'agent_update':
      if (Array.isArray(message.data)) {
        dispatch({ type: 'UPDATE_AGENTS', payload: message.data });
      } else {
        dispatch({ type: 'UPDATE_AGENT', payload: message.data });
      }
      break;

    case 'trust_update':
      if (Array.isArray(message.data)) {
        dispatch({ type: 'UPDATE_TRUST_SCORES', payload: message.data });
      } else {
        dispatch({ type: 'UPDATE_TRUST_SCORE', payload: message.data });
      }
      break;

    case 'anomaly_alert':
      // Handle anomaly alerts
      console.log('Anomaly detected:', message.data);
      break;
  }
}

// Simulate data updates for demonstration
function simulateDataUpdates(dispatch: React.Dispatch<SimulationAction>) {
  // Generate mock agents
  const mockAgents: Agent[] = Array.from({ length: 20 }, (_, i) => ({
    id: `agent-${i + 1}`,
    position: {
      x: (Math.random() - 0.5) * 50,
      y: (Math.random() - 0.5) * 50,
      z: (Math.random() - 0.5) * 50
    },
    trustScore: Math.floor(Math.random() * 100),
    status: Math.random() > 0.8 ? 'inactive' : 'active',
    connections: [],
    lastUpdate: Date.now()
  }));

  // Generate mock trust scores
  const mockTrustScores: TrustScoreData[] = Array.from({ length: 15 }, (_, i) => ({
    id: `trust-${i + 1}`,
    position: {
      x: (Math.random() - 0.5) * 40,
      y: (Math.random() - 0.5) * 40,
      z: 0
    },
    value: Math.floor(Math.random() * 100),
    timestamp: Date.now(),
    source: `sensor-${i + 1}`
  }));

  // Update state with mock data
  dispatch({ type: 'UPDATE_AGENTS', payload: mockAgents });
  dispatch({ type: 'UPDATE_TRUST_SCORES', payload: mockTrustScores });

  // Update simulation state
  const avgTrustScore = mockTrustScores.reduce((sum, score) => sum + score.value, 0) / mockTrustScores.length;
  const simulationState: SimulationState = {
    status: 'running',
    timestamp: Date.now(),
    activeAgents: mockAgents.filter(a => a.status === 'active').length,
    totalConnections: Math.floor(mockAgents.length * 0.7),
    averageTrustScore: Math.floor(avgTrustScore),
    anomalies: []
  };

  dispatch({ type: 'SET_SIMULATION_STATE', payload: simulationState });
}