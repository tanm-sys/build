import React, { useRef, useEffect, useMemo } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Stats } from '@react-three/drei';
import * as THREE from 'three';
import AgentNetwork3D from './AgentNetwork3D';
import ParticleSystem from './ParticleSystem';
import TrustScoreTerrain from './TrustScoreTerrain';
import { useSimulation } from '../../contexts/SimulationContext';
import { useAccessibility } from '../../contexts/AccessibilityContext';
import { usePerformance } from '../../contexts/PerformanceContext';

/**
 * Core 3D Scene Manager
 * Handles Three.js scene management with performance optimization
 * Implements adaptive quality based on device capabilities
 */
const SceneManager: React.FC = () => {
  const { gl, scene } = useThree();
  const { simulationState, agents, trustScores } = useSimulation();
  const { isReducedMotion } = useAccessibility();
  const { performanceLevel, adaptiveQuality } = usePerformance();

  const sceneRef = useRef<THREE.Scene>(scene);
  const animationFrameRef = useRef<number>();

  // Adaptive quality settings based on performance monitoring
  const qualitySettings = useMemo((): {
    shadowMapSize: number;
    particleCount: number;
    geometryDetail: 'low' | 'medium' | 'high';
    antialias: boolean;
  } => {
    const baseSettings = {
      shadowMapSize: 1024,
      particleCount: 1000,
      geometryDetail: 'high' as const,
      antialias: true
    };

    switch (performanceLevel) {
      case 'low':
        return {
          ...baseSettings,
          shadowMapSize: 512,
          particleCount: 300,
          geometryDetail: 'low' as const,
          antialias: false
        };
      case 'medium':
        return {
          ...baseSettings,
          shadowMapSize: 1024,
          particleCount: 600,
          geometryDetail: 'medium' as const,
          antialias: true
        };
      default:
        return baseSettings;
    }
  }, [performanceLevel]);

  // Initialize scene with performance optimizations
  useEffect(() => {
    // Track created objects for cleanup
    const createdObjects: THREE.Object3D[] = [];

    // Configure renderer for optimal performance
    gl.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    gl.setSize(window.innerWidth, window.innerHeight);
    gl.outputColorSpace = THREE.SRGBColorSpace;
    gl.toneMapping = THREE.ACESFilmicToneMapping;
    gl.toneMappingExposure = 1.0;

    // Enable shadows with adaptive quality
    gl.shadowMap.enabled = true;
    gl.shadowMap.type = THREE.PCFSoftShadowMap;

    // Set up fog for depth perception
    scene.fog = new THREE.Fog(0x000511, 50, 200);

    // Lighting setup
    const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
    scene.add(ambientLight);
    createdObjects.push(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(50, 50, 25);
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width = qualitySettings.shadowMapSize;
    directionalLight.shadow.mapSize.height = qualitySettings.shadowMapSize;
    scene.add(directionalLight);
    createdObjects.push(directionalLight);

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }

      // Clean up Three.js objects to prevent memory leaks in StrictMode
      createdObjects.forEach(obj => {
        scene.remove(obj);
        if (obj instanceof THREE.Light) {
          // Lights don't need explicit disposal in this context
          // but we remove them from the scene
        }
      });

      // Reset fog
      scene.fog = null;
    };
  }, [gl, scene, qualitySettings]);

  // Animation loop with performance monitoring
  useFrame((_, delta) => {
    if (isReducedMotion) return;

    // Adaptive frame rate based on performance
    const targetFPS = adaptiveQuality ? 30 : 60;
    const frameTime = 1000 / targetFPS;

    if (delta > frameTime / 1000) {
      // Skip frame if performance is poor
      return;
    }

    // Update particle systems
    if (sceneRef.current) {
      sceneRef.current.children.forEach(child => {
        if (child.userData.update) {
          child.userData.update(delta);
        }
      });
    }
  });

  return (
    <>
      {/* Camera Controls */}
      <OrbitControls
        enablePan={true}
        enableZoom={true}
        enableRotate={true}
        zoomSpeed={0.6}
        panSpeed={0.5}
        rotateSpeed={0.4}
        minDistance={5}
        maxDistance={200}
        maxPolarAngle={Math.PI}
        aria-label="3D scene navigation controls"
      />

      {/* Performance Stats (development only) */}
      {process.env.NODE_ENV === 'development' && <Stats />}

      {/* Core 3D Components */}
      <AgentNetwork3D
        agents={agents}
        qualitySettings={qualitySettings}
      />

      <ParticleSystem
        count={qualitySettings.particleCount}
        simulationState={simulationState}
      />

      <TrustScoreTerrain
        trustScores={trustScores}
        detailLevel={qualitySettings.geometryDetail}
      />

      {/* Accessibility helpers */}
      <mesh position={[0, -10, 0]} visible={false}>
        <boxGeometry args={[200, 1, 200]} />
        <meshBasicMaterial color={0x000000} />
      </mesh>
    </>
  );
};

export default SceneManager;