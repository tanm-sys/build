import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import {
  Agent,
  SimulationState,
  TrustScoreData,
  WebSocketMessage,
  Anomaly,
  Vector3D,
  AgentMetadata
} from '../types/simulation';

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

  // WebSocket connection for real-time updates with advanced error recovery
  useEffect(() => {
    let ws: WebSocket | null = null;
    let reconnectTimeout: NodeJS.Timeout;
    let heartbeatInterval: NodeJS.Timeout;
    let reconnectAttempts = 0;
    let isManualDisconnect = false;
    const maxReconnectAttempts = 10;
    const baseReconnectDelay = 1000; // 1 second
    const maxReconnectDelay = 30000; // 30 seconds

    const getReconnectDelay = (attempt: number) => {
      // Exponential backoff with jitter
      const exponentialDelay = Math.min(baseReconnectDelay * Math.pow(2, attempt), maxReconnectDelay);
      const jitter = Math.random() * 0.1 * exponentialDelay; // 10% jitter
      return exponentialDelay + jitter;
    };

    const startHeartbeat = (websocket: WebSocket) => {
      heartbeatInterval = setInterval(() => {
        if (websocket.readyState === WebSocket.OPEN) {
          // Send ping frame to check connection health (no response expected)
          try {
            websocket.send(JSON.stringify({ type: 'heartbeat', timestamp: Date.now() }));
          } catch (error) {
            console.warn('Failed to send heartbeat:', error);
          }
        }
      }, 30000); // Ping every 30 seconds
    };

    const stopHeartbeat = () => {
      if (heartbeatInterval) {
        clearInterval(heartbeatInterval);
      }
    };

    const connectWebSocket = () => {
      try {
        // Connect to backend WebSocket server using environment variable
        const wsUrl = import.meta.env.VITE_WEBSOCKET_URL || 'ws://localhost:8000/ws/simulation';
        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
          console.log('WebSocket connected successfully');
          dispatch({ type: 'SET_CONNECTION_STATUS', payload: true });
          reconnectAttempts = 0; // Reset reconnect attempts on successful connection

          // Start heartbeat monitoring
          if (ws) {
            startHeartbeat(ws);
          }
        };

        ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);

            // Handle heartbeat messages (don't process them as regular messages)
            if (message.type === 'heartbeat') {
              return; // Heartbeat message, no need to process further
            }

            handleWebSocketMessage(message, dispatch);
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
            // Don't trigger reconnection for message parsing errors
          }
        };

        ws.onclose = (event) => {
          console.log(`WebSocket disconnected. Code: ${event.code}, Reason: ${event.reason}`);
          dispatch({ type: 'SET_CONNECTION_STATUS', payload: false });
          stopHeartbeat();

          // Don't attempt reconnection if manually disconnected or max attempts reached
          if (isManualDisconnect || reconnectAttempts >= maxReconnectAttempts) {
            console.log('WebSocket reconnection disabled');
            return;
          }

          // Calculate delay with exponential backoff
          const delay = getReconnectDelay(reconnectAttempts);
          reconnectAttempts++;

          console.log(`Attempting to reconnect (${reconnectAttempts}/${maxReconnectAttempts}) in ${Math.round(delay/1000)}s`);

          reconnectTimeout = setTimeout(() => {
            connectWebSocket();
          }, delay);
        };

        ws.onerror = (error) => {
          console.error('WebSocket error occurred:', error);
          // Error event is followed by close event, so we don't need to handle reconnection here
        };
      } catch (error) {
        console.error('Failed to initialize WebSocket connection:', error);
        dispatch({ type: 'SET_CONNECTION_STATUS', payload: false });

        // Attempt reconnection even on initialization failure
        if (!isManualDisconnect && reconnectAttempts < maxReconnectAttempts) {
          const delay = getReconnectDelay(reconnectAttempts);
          reconnectAttempts++;

          reconnectTimeout = setTimeout(connectWebSocket, delay);
        }
      }
    };

    connectWebSocket();

    return () => {
      isManualDisconnect = true; // Mark as manual disconnect
      stopHeartbeat();

      if (ws) {
        ws.close(1000, 'Component unmounting'); // Clean close
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
          activeAgents: state.agents.length + 1
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
          activeAgents: state.agents.length - 1
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
      const simulationData = message.data as { status: SimulationState['status']; activeAgents: number; totalConnections: number; averageTrustScore: number; anomalies: Anomaly[] };
      const simulationState: SimulationState = {
        status: simulationData.status,
        timestamp: message.timestamp,
        activeAgents: simulationData.activeAgents,
        totalConnections: simulationData.totalConnections,
        averageTrustScore: simulationData.averageTrustScore,
        anomalies: simulationData.anomalies
      };
      dispatch({ type: 'SET_SIMULATION_STATE', payload: simulationState });
      break;

    case 'agent_update':
      if (Array.isArray(message.data)) {
        dispatch({ type: 'UPDATE_AGENTS', payload: message.data as Agent[] });
      } else {
        const agentData = message.data as { id: string; position?: Vector3D; trustScore?: number; status?: Agent['status']; connections?: string[]; metadata?: AgentMetadata };
        dispatch({ type: 'UPDATE_AGENT', payload: { id: agentData.id, updates: agentData } });
      }
      break;

    case 'trust_update':
      if (Array.isArray(message.data)) {
        dispatch({ type: 'UPDATE_TRUST_SCORES', payload: message.data as TrustScoreData[] });
      } else {
        const trustData = message.data as { id: string; position?: Vector3D; value?: number; source?: string };
        dispatch({ type: 'UPDATE_TRUST_SCORE', payload: { id: trustData.id, updates: trustData } });
      }
      break;

    case 'anomaly_alert':
      const anomalyData = message.data as { id: string; type: Anomaly['type']; severity: Anomaly['severity']; position: Vector3D; description: string };
      console.log('Anomaly detected:', anomalyData);
      // Could dispatch an action to add anomaly to state if needed
      break;

    case 'heartbeat':
      // Heartbeat message - no action needed
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