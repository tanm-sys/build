import React, { useState, useCallback, useEffect } from 'react';
import styled from 'styled-components';
import { NavigationItem } from '../../types/simulation';

const NavContainer = styled.nav`
  background: rgba(0, 0, 0, 0.9);
  padding: 1rem;
  border-bottom: 1px solid #00ffff;
  color: white;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  position: relative;
`;

const NavHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
`;

const NavTitle = styled.h1`
  margin: 0;
  color: #00ffff;
  font-size: 1.5rem;
  font-weight: 300;
  cursor: pointer;
  transition: color var(--transition-base);

  &:hover {
    color: #33ffff;
  }
`;

const NavSubtitle = styled.p`
  margin: 0.25rem 0 0 0;
  color: #cccccc;
  font-size: 0.875rem;
  font-weight: 300;
`;

const NavMenu = styled.div`
  display: flex;
  gap: 0.5rem;
  align-items: center;
`;

const NavButton = styled.button<{ active?: boolean; variant?: 'primary' | 'secondary' }>`
  background: ${props => props.active ? 'rgba(0, 255, 255, 0.2)' : 'rgba(255, 255, 255, 0.1)'};
  border: 1px solid ${props => props.active ? '#00ffff' : 'rgba(255, 255, 255, 0.2)'};
  color: white;
  padding: 0.5rem 0.75rem;
  border-radius: 4px;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all var(--transition-base);
  position: relative;

  &:hover {
    background: rgba(255, 255, 255, 0.2);
    border-color: #00ffff;
    transform: translateY(-1px);
  }

  &:active {
    transform: translateY(0);
  }

  ${props => props.variant === 'primary' && `
    background: linear-gradient(135deg, #4a90e2, #7b68ee);
    border-color: #4a90e2;
  `}
`;

const Tooltip = styled.div`
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.9);
  color: white;
  padding: 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  white-space: nowrap;
  z-index: 1000;
  margin-top: 0.25rem;
  opacity: 0;
  pointer-events: none;
  transition: opacity var(--transition-base);

  &::before {
    content: '';
    position: absolute;
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%);
    border: 5px solid transparent;
    border-bottom-color: rgba(0, 0, 0, 0.9);
  }
`;

const TooltipContainer = styled.div`
  position: relative;

  &:hover ${Tooltip} {
    opacity: 1;
  }
`;

const StatusIndicator = styled.div<{ status: 'online' | 'offline' | 'syncing' }>`
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-left: 0.5rem;

  ${props => {
    switch (props.status) {
      case 'online':
        return `background: #00ff88;`;
      case 'syncing':
        return `
          background: #ffaa00;
          animation: pulse 1s infinite;
        `;
      case 'offline':
        return `background: #ff4444;`;
      default:
        return `background: #666;`;
    }
  }}
`;

const KeyboardHint = styled.span`
  font-size: 0.7rem;
  opacity: 0.7;
  margin-left: 0.25rem;
  font-family: var(--font-family-mono);
`;

const SettingsMenu = styled.div`
  position: absolute;
  top: 100%;
  right: 0;
  background: rgba(0, 0, 0, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 0.5rem;
  min-width: 200px;
  z-index: 1000;
  margin-top: 0.5rem;
`;

const SettingsItem = styled.button`
  width: 100%;
  background: none;
  border: none;
  color: white;
  padding: 0.5rem;
  text-align: left;
  cursor: pointer;
  border-radius: 4px;
  font-size: 0.875rem;
  transition: background var(--transition-base);

  &:hover {
    background: rgba(255, 255, 255, 0.1);
  }
`;

const Navigation: React.FC = () => {
  const [activeView, setActiveView] = useState('overview');
  const [showSettings, setShowSettings] = useState(false);
  const [connectionStatus] = useState<'online' | 'offline' | 'syncing'>('online');
  const [showKeyboardHints, setShowKeyboardHints] = useState(false);

  // Keyboard shortcuts handler
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.ctrlKey || event.metaKey) {
        switch (event.key) {
          case 'k':
            event.preventDefault();
            setShowKeyboardHints(!showKeyboardHints);
            break;
          case '/':
            event.preventDefault();
            // Focus search or help
            break;
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [showKeyboardHints]);

  const navigationItems: NavigationItem[] = [
    {
      id: 'overview',
      label: 'Overview',
      icon: '🏠',
      path: '/overview',
      shortcut: 'Ctrl+1',
      description: 'Main dashboard view'
    },
    {
      id: 'agents',
      label: 'Agents',
      icon: '🤖',
      path: '/agents',
      shortcut: 'Ctrl+2',
      description: 'Agent network visualization'
    },
    {
      id: 'analytics',
      label: 'Analytics',
      icon: '📊',
      path: '/analytics',
      shortcut: 'Ctrl+3',
      description: 'Performance analytics'
    },
    {
      id: 'settings',
      label: 'Settings',
      icon: '⚙️',
      path: '/settings',
      shortcut: 'Ctrl+,',
      description: 'Application settings'
    }
  ];

  const handleNavigation = useCallback((itemId: string) => {
    setActiveView(itemId);
    // In a real app, this would handle routing
    console.log(`Navigating to: ${itemId}`);
  }, []);

  const handleSettingsAction = useCallback((action: string) => {
    switch (action) {
      case 'shortcuts':
        setShowKeyboardHints(!showKeyboardHints);
        break;
      case 'about':
        alert('Decentralized AI Simulation v1.0.0');
        break;
      case 'help':
        window.open('/help', '_blank');
        break;
    }
    setShowSettings(false);
  }, [showKeyboardHints]);

  return (
    <NavContainer>
      <NavHeader>
        <div>
          <NavTitle onClick={() => handleNavigation('overview')}>
            Decentralized AI Simulation
          </NavTitle>
          <NavSubtitle>
            3D Visualization Platform
            <StatusIndicator status={connectionStatus} />
          </NavSubtitle>
        </div>

        <NavMenu>
          {navigationItems.map((item) => (
            <TooltipContainer key={item.id}>
              <NavButton
                active={activeView === item.id}
                onClick={() => handleNavigation(item.id)}
                variant={item.id === 'overview' ? 'primary' : 'secondary'}
              >
                {item.icon} {item.label}
                {showKeyboardHints && (
                  <KeyboardHint>{item.shortcut}</KeyboardHint>
                )}
              </NavButton>
              <Tooltip>{item.description}</Tooltip>
            </TooltipContainer>
          ))}

          <TooltipContainer>
            <NavButton onClick={() => setShowSettings(!showSettings)}>
              ⋯
            </NavButton>
            {showSettings && (
              <SettingsMenu>
                <SettingsItem onClick={() => handleSettingsAction('shortcuts')}>
                  ⌨️ Keyboard Shortcuts {showKeyboardHints ? '✓' : ''}
                </SettingsItem>
                <SettingsItem onClick={() => handleSettingsAction('help')}>
                  ❓ Help & Documentation
                </SettingsItem>
                <SettingsItem onClick={() => handleSettingsAction('about')}>
                  ℹ️ About
                </SettingsItem>
              </SettingsMenu>
            )}
          </TooltipContainer>
        </NavMenu>
      </NavHeader>

      {showKeyboardHints && (
        <div style={{
          fontSize: '0.75rem',
          color: '#999',
          marginTop: '0.5rem',
          padding: '0.5rem',
          background: 'rgba(255, 255, 255, 0.05)',
          borderRadius: '4px'
        }}>
          💡 <strong>Tip:</strong> Use Ctrl+K to toggle this help • Press Ctrl+/ for search
        </div>
      )}
    </NavContainer>
  );
};

export default Navigation;