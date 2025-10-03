import React, { useRef, useMemo, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { Text } from '@react-three/drei';
import { Agent, QualitySettings } from '../../types/simulation';

interface AgentNetwork3DProps {
  agents: Agent[];
  qualitySettings: QualitySettings;
}

/**
 * 3D Agent Network Visualization Component
 * Renders agents as 3D nodes with connection lines and real-time updates
 * Implements performance optimizations and accessibility features
 */
const AgentNetwork3D: React.FC<AgentNetwork3DProps> = ({
  agents,
  qualitySettings
}) => {
  const groupRef = useRef<THREE.Group>(null);
  const linesRef = useRef<THREE.Group>(null);
  const nodesRef = useRef<THREE.Group>(null);

  // Memoize agent positions for performance
  const agentPositions = useMemo(() => {
    return agents.map(agent => {
      const phi = Math.acos(-0.5 + Math.random());
      const theta = Math.random() * Math.PI * 2;
      const radius = 20 + Math.random() * 15;

      return {
        id: agent.id,
        position: new THREE.Vector3(
          radius * Math.sin(phi) * Math.cos(theta),
          radius * Math.sin(phi) * Math.sin(theta),
          radius * Math.cos(phi)
        ),
        trustScore: agent.trustScore,
        status: agent.status,
        connections: agent.connections
      };
    });
  }, [agents]);

  // Create connection lines between agents
  const connectionLines = useMemo(() => {
    const lines: Array<{
      start: THREE.Vector3;
      end: THREE.Vector3;
      strength: number;
    }> = [];

    agentPositions.forEach((agent, index) => {
      agent.connections.forEach(connectionId => {
        const targetAgent = agentPositions.find(a => a.id === connectionId);
        if (targetAgent && index < agentPositions.findIndex(a => a.id === connectionId)) {
          lines.push({
            start: agent.position,
            end: targetAgent.position,
            strength: Math.min(agent.trustScore, targetAgent.trustScore) / 100
          });
        }
      });
    });

    return lines;
  }, [agentPositions]);

  // Animation loop for agent pulsing and movement
  useFrame((state) => {
    if (!nodesRef.current) return;

    const time = state.clock.getElapsedTime();

    // Animate agent nodes
    nodesRef.current.children.forEach((node, index) => {
      const agent = agentPositions[index];
      if (!agent) return;

      // Pulsing effect based on trust score
      const pulseScale = 1 + Math.sin(time * 2 + index) * 0.1 * (agent.trustScore / 100);
      node.scale.setScalar(pulseScale);

      // Color animation based on status
      const material = (node as THREE.Mesh).material as THREE.MeshStandardMaterial;
      if (material) {
        const hue = agent.status === 'active' ? 0.3 :
                   agent.status === 'inactive' ? 0.1 : 0.6;
        material.color.setHSL(hue, 0.8, 0.5);
      }
    });

    // Animate connection lines
    if (linesRef.current) {
      linesRef.current.children.forEach((line, index) => {
        const connection = connectionLines[index];
        if (!connection) return;

        const opacity = 0.3 + Math.sin(time * 1.5 + index) * 0.2;
        (line as THREE.Line).material.opacity = opacity * connection.strength;
      });
    }
  });

  // Update geometry when agents change
  useEffect(() => {
    if (!nodesRef.current || !linesRef.current) return;

    // Clear existing nodes
    while (nodesRef.current.children.length > 0) {
      nodesRef.current.remove(nodesRef.current.children[0]);
    }

    // Clear existing lines
    while (linesRef.current.children.length > 0) {
      linesRef.current.remove(linesRef.current.children[0]);
    }

    // Create agent nodes
    agentPositions.forEach((agent) => {
      if (!nodesRef.current) return;

      // Agent node geometry based on quality settings
      const geometry = qualitySettings.geometryDetail === 'low'
        ? new THREE.SphereGeometry(0.3, 8, 6)
        : new THREE.SphereGeometry(0.4, 12, 8);

      const material = new THREE.MeshStandardMaterial({
        color: new THREE.Color().setHSL(0.3, 0.8, 0.5),
        metalness: 0.1,
        roughness: 0.4,
        emissive: new THREE.Color().setHSL(0.3, 0.8, 0.1),
        emissiveIntensity: 0.2
      });

      const node = new THREE.Mesh(geometry, material);
      node.position.copy(agent.position);
      node.userData = { agentId: agent.id, trustScore: agent.trustScore };

      nodesRef.current.add(node);
    });

    // Create connection lines
    connectionLines.forEach((connection) => {
      if (!linesRef.current) return;

      const geometry = new THREE.BufferGeometry().setFromPoints([
        connection.start,
        connection.end
      ]);

      const material = new THREE.LineBasicMaterial({
        color: 0x00ffff,
        transparent: true,
        opacity: connection.strength * 0.5
      });

      const line = new THREE.Line(geometry, material);
      linesRef.current.add(line);
    });
  }, [agentPositions, connectionLines, qualitySettings]);

  return (
    <group ref={groupRef}>
      {/* Agent nodes container */}
      <group ref={nodesRef} />

      {/* Connection lines container */}
      <group ref={linesRef} />

      {/* Agent labels (only for high quality or when focused) */}
      {qualitySettings.geometryDetail === 'high' && agentPositions.map((agent) => (
        <Text
          key={`label-${agent.id}`}
          position={[
            agent.position.x,
            agent.position.y + 1,
            agent.position.z
          ]}
          fontSize={0.5}
          color={0xffffff}
          anchorX="center"
          anchorY="middle"
          visible={agent.trustScore > 80} // Only show labels for high-trust agents
        >
          {`Agent ${agent.id.slice(-4)}`}
        </Text>
      ))}
    </group>
  );
};

export default AgentNetwork3D;