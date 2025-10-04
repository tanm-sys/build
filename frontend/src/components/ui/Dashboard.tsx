import React, { useState, useCallback } from 'react';
import styled, { keyframes } from 'styled-components';
import { useSimulation } from '../../contexts/SimulationContext';

const DashboardContainer = styled.div`
  padding: 1rem;
  background: rgba(0, 0, 0, 0.8);
  border-radius: 8px;
  color: white;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
`;

const StatCard = styled.div`
  margin-bottom: 1rem;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  border-left: 3px solid #00ffff;
`;

const StatTitle = styled.div`
  font-size: 0.875rem;
  color: #cccccc;
  margin-bottom: 0.25rem;
`;

const StatValue = styled.div`
  font-size: 1.25rem;
  font-weight: bold;
  color: #00ffff;
`;

// Loading skeleton animation
const pulse = keyframes`
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
`;

const LoadingSkeleton = styled.div`
  height: 1.5rem;
  background: linear-gradient(90deg, #333 25%, #444 50%, #333 75%);
  background-size: 200% 100%;
  animation: ${pulse} 1.5s infinite;
  border-radius: 4px;
  margin-top: 0.25rem;
`;

const ErrorMessage = styled.div`
  color: #ff6b6b;
  background: rgba(255, 107, 107, 0.1);
  border: 1px solid #ff6b6b;
  border-radius: 4px;
  padding: 0.75rem;
  margin-bottom: 1rem;
  font-size: 0.875rem;
`;

const RetryButton = styled.button`
  background: #00ffff;
  color: #000;
  border: none;
  border-radius: 4px;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  cursor: pointer;
  margin-top: 0.5rem;

  &:hover {
    background: #00cccc;
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const ConnectionStatus = styled.div<{ connected: boolean }>`
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: ${props => props.connected ? '#4CAF50' : '#f44336'};
  margin-right: 0.5rem;
  animation: ${props => props.connected ? 'none' : `${pulse} 2s infinite`};
`;

const Dashboard: React.FC = () => {
  const { simulationState, agents, trustScores, isConnected, lastUpdate } = useSimulation();
  const [retryCount, setRetryCount] = useState(0);
  const [isRetrying, setIsRetrying] = useState(false);

  const isLoading = !isConnected && retryCount === 0;
  const hasError = !isConnected && retryCount > 0 && retryCount < 3;

  const handleRetry = useCallback(async () => {
    setIsRetrying(true);
    setRetryCount(prev => prev + 1);

    // Simulate retry delay
    await new Promise(resolve => setTimeout(resolve, 2000));

    setIsRetrying(false);

    // Reset retry count after 3 attempts
    if (retryCount >= 2) {
      setTimeout(() => setRetryCount(0), 5000);
    }
  }, [retryCount]);

  const formatLastUpdate = (timestamp: number) => {
    const now = Date.now();
    const diff = now - timestamp;
    const seconds = Math.floor(diff / 1000);

    if (seconds < 60) return `${seconds}s ago`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    return `${hours}h ago`;
  };

  return (
    <DashboardContainer>
      <h2 style={{ marginTop: 0, color: '#00ffff', borderBottom: '1px solid #00ffff', paddingBottom: '0.5rem' }}>
        <ConnectionStatus connected={isConnected} />
        Simulation Dashboard
      </h2>

      {/* Connection Status */}
      <StatCard>
        <StatTitle>Connection Status</StatTitle>
        <StatValue style={{ color: isConnected ? '#4CAF50' : '#f44336' }}>
          {isConnected ? 'Connected' : 'Disconnected'}
        </StatValue>
        {lastUpdate && (
          <div style={{ fontSize: '0.75rem', color: '#cccccc', marginTop: '0.25rem' }}>
            Last update: {formatLastUpdate(lastUpdate)}
          </div>
        )}
      </StatCard>

      {/* Error State */}
      {hasError && (
        <ErrorMessage>
          <div>Failed to connect to simulation server</div>
          <div style={{ fontSize: '0.75rem', marginTop: '0.25rem' }}>
            Attempt {retryCount}/3
          </div>
          <RetryButton onClick={handleRetry} disabled={isRetrying}>
            {isRetrying ? 'Retrying...' : 'Retry Connection'}
          </RetryButton>
        </ErrorMessage>
      )}

      {/* Loading State */}
      {isLoading && (
        <>
          <StatCard>
            <StatTitle>Status</StatTitle>
            <LoadingSkeleton />
          </StatCard>

          <StatCard>
            <StatTitle>Active Agents</StatTitle>
            <LoadingSkeleton />
          </StatCard>

          <StatCard>
            <StatTitle>Total Connections</StatTitle>
            <LoadingSkeleton />
          </StatCard>

          <StatCard>
            <StatTitle>Average Trust Score</StatTitle>
            <LoadingSkeleton />
          </StatCard>

          <StatCard>
            <StatTitle>Trust Data Points</StatTitle>
            <LoadingSkeleton />
          </StatCard>

          <StatCard>
            <StatTitle>Connected Agents</StatTitle>
            <LoadingSkeleton />
          </StatCard>
        </>
      )}

      {/* Loaded State */}
      {!isLoading && isConnected && (
        <>
          <StatCard>
            <StatTitle>Status</StatTitle>
            <StatValue>{simulationState?.status || 'Unknown'}</StatValue>
          </StatCard>

          <StatCard>
            <StatTitle>Active Agents</StatTitle>
            <StatValue>{simulationState?.activeAgents || 0}</StatValue>
          </StatCard>

          <StatCard>
            <StatTitle>Total Connections</StatTitle>
            <StatValue>{simulationState?.totalConnections || 0}</StatValue>
          </StatCard>

          <StatCard>
            <StatTitle>Average Trust Score</StatTitle>
            <StatValue>
              {simulationState?.averageTrustScore ?
                (simulationState.averageTrustScore * 100).toFixed(1) + '%' :
                '0%'
              }
            </StatValue>
          </StatCard>

          <StatCard>
            <StatTitle>Trust Data Points</StatTitle>
            <StatValue>{trustScores?.length || 0}</StatValue>
          </StatCard>

          <StatCard>
            <StatTitle>Connected Agents</StatTitle>
            <StatValue>{agents?.length || 0}</StatValue>
          </StatCard>
        </>
      )}
    </DashboardContainer>
  );
};

export default Dashboard;