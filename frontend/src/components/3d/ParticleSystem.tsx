import React, { useRef, useMemo, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { SimulationState } from '../../types/simulation';

interface ParticleSystemProps {
  count: number;
  simulationState: SimulationState;
}

/**
 * Dynamic Particle System Component
 * GPU-accelerated visual effects for anomalies and data flow
 * Implements performance optimizations and real-time updates
 */
const ParticleSystem: React.FC<ParticleSystemProps> = ({
  count,
  simulationState
}) => {
  const pointsRef = useRef<THREE.Points>(null);
  const velocitiesRef = useRef<Float32Array>();
  const originalPositionsRef = useRef<Float32Array>();

  // Initialize particle positions and velocities
  const { positions, velocities } = useMemo(() => {
    const positions = new Float32Array(count * 3);
    const velocities = new Float32Array(count * 3);

    for (let i = 0; i < count; i++) {
      const i3 = i * 3;

      // Random spherical distribution
      const radius = Math.random() * 30 + 5;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);

      positions[i3] = radius * Math.sin(phi) * Math.cos(theta);
      positions[i3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
      positions[i3 + 2] = radius * Math.cos(phi);

      // Random initial velocities
      velocities[i3] = (Math.random() - 0.5) * 0.02;
      velocities[i3 + 1] = (Math.random() - 0.5) * 0.02;
      velocities[i3 + 2] = (Math.random() - 0.5) * 0.02;
    }

    return { positions, velocities };
  }, [count]);

  // Store original positions for reset
  useEffect(() => {
    originalPositionsRef.current = positions.slice();
    velocitiesRef.current = velocities.slice();
  }, [positions, velocities]);

  // Particle animation based on simulation state
  useFrame((state, delta) => {
    if (!pointsRef.current || !velocitiesRef.current) return;

    const positions = pointsRef.current.geometry.attributes.position.array as Float32Array;
    const time = state.clock.getElapsedTime();

    for (let i = 0; i < count; i++) {
      const i3 = i * 3;

      // Base movement
      positions[i3] += velocitiesRef.current![i3];
      positions[i3 + 1] += velocitiesRef.current![i3 + 1];
      positions[i3 + 2] += velocitiesRef.current![i3 + 2];

      // Simulation state-based effects
      switch (simulationState.status) {
        case 'running':
          // Normal data flow patterns
          positions[i3] += Math.sin(time + i * 0.1) * 0.01;
          positions[i3 + 1] += Math.cos(time + i * 0.1) * 0.01;
          break;

        case 'anomaly_detected':
          // Chaotic movement during anomalies
          positions[i3] += Math.sin(time * 3 + i) * 0.05;
          positions[i3 + 1] += Math.cos(time * 2 + i) * 0.05;
          positions[i3 + 2] += Math.sin(time * 1.5 + i) * 0.03;
          break;

        case 'paused':
          // Slow drift when paused
          positions[i3] += Math.sin(i * 0.01) * 0.001;
          positions[i3 + 1] += Math.cos(i * 0.01) * 0.001;
          break;
      }

      // Boundary constraints with bounce
      const distance = Math.sqrt(
        positions[i3] ** 2 +
        positions[i3 + 1] ** 2 +
        positions[i3 + 2] ** 2
      );

      if (distance > 40) {
        // Bounce back with damping
        const normal = new THREE.Vector3(
          positions[i3],
          positions[i3 + 1],
          positions[i3 + 2]
        ).normalize();

        velocitiesRef.current![i3] = -velocitiesRef.current![i3] * 0.8 - normal.x * 0.1;
        velocitiesRef.current![i3 + 1] = -velocitiesRef.current![i3 + 1] * 0.8 - normal.y * 0.1;
        velocitiesRef.current![i3 + 2] = -velocitiesRef.current![i3 + 2] * 0.8 - normal.z * 0.1;

        // Push back inside boundary
        positions[i3] = normal.x * 39;
        positions[i3 + 1] = normal.y * 39;
        positions[i3 + 2] = normal.z * 39;
      }
    }

    pointsRef.current.geometry.attributes.position.needsUpdate = true;
  });

  // Create particle material based on simulation state
  const particleMaterial = useMemo(() => {
    const color = simulationState.status === 'anomaly_detected'
      ? 0xff4444
      : simulationState.status === 'running'
      ? 0x4444ff
      : 0x888888;

    return new THREE.PointsMaterial({
      color,
      size: 0.1,
      transparent: true,
      opacity: 0.8,
      vertexColors: false,
      sizeAttenuation: true,
      blending: THREE.AdditiveBlending
    });
  }, [simulationState.status]);

  // Update material when simulation state changes
  useEffect(() => {
    if (particleMaterial) {
      const color = simulationState.status === 'anomaly_detected'
        ? 0xff4444
        : simulationState.status === 'running'
        ? 0x4444ff
        : 0x888888;

      particleMaterial.color.setHex(color);
      particleMaterial.needsUpdate = true;
    }
  }, [simulationState.status, particleMaterial]);

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={count}
          array={positions}
          itemSize={3}
        />
      </bufferGeometry>
      <primitive object={particleMaterial} />
    </points>
  );
};

export default ParticleSystem;