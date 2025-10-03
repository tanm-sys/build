import React, { useMemo, useRef, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { TrustScoreData } from '../../types/simulation';

interface TrustScoreTerrainProps {
  trustScores: TrustScoreData[];
  detailLevel: 'low' | 'medium' | 'high';
}

/**
 * 3D Terrain Visualization Component
 * Renders trust scores as 3D terrain with height mapping
 * Implements LOD (Level of Detail) for performance optimization
 */
const TrustScoreTerrain: React.FC<TrustScoreTerrainProps> = ({
  trustScores,
  detailLevel
}) => {
  const terrainRef = useRef<THREE.Mesh>(null);
  const wireframeRef = useRef<THREE.LineSegments>(null);

  // Generate terrain geometry based on trust scores
  const { geometry, wireframeGeometry } = useMemo(() => {
    const segments = detailLevel === 'low' ? 32 :
                    detailLevel === 'medium' ? 64 : 128;
    const geometry = new THREE.PlaneGeometry(100, 100, segments, segments);

    // Create height map from trust scores
    const positions = geometry.attributes.position.array as Float32Array;

    for (let i = 0; i < positions.length; i += 3) {
      const x = positions[i];
      const y = positions[i + 1];

      // Generate height based on trust score data
      const height = generateHeightAtPosition(x, y, trustScores);

      // Apply height with some noise for realism
      positions[i + 2] = height + (Math.random() - 0.5) * 0.5;
    }

    geometry.computeVertexNormals();

    // Create wireframe geometry
    const wireframeGeometry = new THREE.WireframeGeometry(geometry);

    return { geometry, wireframeGeometry };
  }, [trustScores, detailLevel]);

  // Generate height value at specific position based on trust scores
  const generateHeightAtPosition = (
    x: number,
    y: number,
    trustScores: TrustScoreData[]
  ): number => {
    let height = 0;
    let totalWeight = 0;

    trustScores.forEach(score => {
      const distance = Math.sqrt(
        Math.pow(x - score.position.x, 2) +
        Math.pow(y - score.position.y, 2)
      );

      // Inverse distance weighting for smooth interpolation
      const weight = 1 / (1 + distance * 0.1);
      height += score.value * weight;
      totalWeight += weight;
    });

    return totalWeight > 0 ? height / totalWeight : 0;
  };

  // Animate terrain colors based on trust levels
  useFrame((state) => {
    if (!terrainRef.current) return;

    const material = terrainRef.current.material as THREE.MeshStandardMaterial;
    const time = state.clock.getElapsedTime();

    if (material && material.color) {
      // Color based on average trust level
      const avgTrust = trustScores.reduce((sum, score) => sum + score.value, 0) / trustScores.length;

      // Interpolate between colors based on trust level
      const hue = avgTrust > 70 ? 0.3 : avgTrust > 40 ? 0.1 : 0.0;
      const saturation = avgTrust > 50 ? 0.8 : 0.5;
      const lightness = 0.4 + (avgTrust / 100) * 0.3;

      const color = new THREE.Color().setHSL(hue, saturation, lightness);
      material.color.lerp(color, 0.1);

      // Subtle animation
      material.emissiveIntensity = 0.1 + Math.sin(time * 0.5) * 0.05;
    }
  });

  // Update geometry when trust scores change
  useEffect(() => {
    if (!terrainRef.current) return;

    const positions = (terrainRef.current.geometry as THREE.PlaneGeometry).attributes.position.array as Float32Array;

    for (let i = 0; i < positions.length; i += 3) {
      const x = positions[i];
      const y = positions[i + 1];

      const height = generateHeightAtPosition(x, y, trustScores);
      positions[i + 2] = height + (Math.random() - 0.5) * 0.5;
    }

    (terrainRef.current.geometry as THREE.PlaneGeometry).attributes.position.needsUpdate = true;
    (terrainRef.current.geometry as THREE.PlaneGeometry).computeVertexNormals();
  }, [trustScores]);

  // Create terrain material
  const terrainMaterial = useMemo(() => {
    return new THREE.MeshStandardMaterial({
      color: 0x4a90e2,
      metalness: 0.1,
      roughness: 0.8,
      transparent: true,
      opacity: 0.9,
      side: THREE.DoubleSide
    });
  }, []);

  // Create wireframe material
  const wireframeMaterial = useMemo(() => {
    return new THREE.LineBasicMaterial({
      color: 0x00ffff,
      transparent: true,
      opacity: 0.3
    });
  }, []);

  return (
    <group>
      {/* Main terrain mesh */}
      <mesh
        ref={terrainRef}
        geometry={geometry}
        material={terrainMaterial}
        rotation={[-Math.PI / 2, 0, 0]}
        position={[0, -5, 0]}
        receiveShadow
      />

      {/* Wireframe overlay for technical view */}
      <lineSegments
        ref={wireframeRef}
        geometry={wireframeGeometry}
        material={wireframeMaterial}
        rotation={[-Math.PI / 2, 0, 0]}
        position={[0, -5, 0]}
      />

      {/* Trust score markers */}
      {trustScores.map((score, index) => (
        <mesh
          key={`marker-${index}`}
          position={[score.position.x, score.position.y + 0.5, score.position.z]}
        >
          <sphereGeometry args={[0.2, 8, 8]} />
          <meshBasicMaterial
            color={score.value > 70 ? 0x00ff00 : score.value > 40 ? 0xffff00 : 0xff0000}
            transparent
            opacity={0.8}
          />
        </mesh>
      ))}
    </group>
  );
};

export default TrustScoreTerrain;