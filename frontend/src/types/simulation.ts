/**
 * Type definitions for the 3D AI Simulation Visualization Platform
 * Provides type safety for all simulation data structures
 */

export interface Vector3D {
  x: number;
  y: number;
  z: number;
}

export interface AgentMetadata {
  name?: string;
  description?: string;
  version?: string;
  capabilities?: string[];
  performance?: {
    cpuUsage?: number;
    memoryUsage?: number;
    networkLatency?: number;
  };
  security?: {
    clearanceLevel?: 'low' | 'medium' | 'high';
    encryptionEnabled?: boolean;
    lastSecurityAudit?: number;
  };
}

export interface Agent {
  id: string;
  position: Vector3D;
  trustScore: number;
  status: 'active' | 'inactive' | 'suspended';
  connections: string[];
  lastUpdate: number;
  metadata?: AgentMetadata;
}

export interface TrustScoreData {
  id: string;
  position: Vector3D;
  value: number;
  timestamp: number;
  source: string;
}

export interface SimulationState {
  status: 'running' | 'paused' | 'stopped' | 'anomaly_detected';
  timestamp: number;
  activeAgents: number;
  totalConnections: number;
  averageTrustScore: number;
  anomalies: Anomaly[];
}

export interface Anomaly {
  id: string;
  type: 'trust_drop' | 'unusual_activity' | 'connection_spike';
  severity: 'low' | 'medium' | 'high' | 'critical';
  position: Vector3D;
  timestamp: number;
  description: string;
}

export interface QualitySettings {
  shadowMapSize: number;
  particleCount: number;
  geometryDetail: 'low' | 'medium' | 'high';
  antialias: boolean;
}

export interface PerformanceMetrics {
  fps: number;
  frameTime: number;
  memoryUsage: number;
  drawCalls: number;
  triangles: number;
}

export interface SimulationUpdateData {
  status: SimulationState['status'];
  activeAgents: number;
  totalConnections: number;
  averageTrustScore: number;
  anomalies: Anomaly[];
}

export interface AgentUpdateData {
  id: string;
  position?: Vector3D;
  trustScore?: number;
  status?: Agent['status'];
  connections?: string[];
  metadata?: AgentMetadata;
}

export interface TrustUpdateData {
  id: string;
  position?: Vector3D;
  value?: number;
  source?: string;
}

export interface AnomalyAlertData {
  id: string;
  type: Anomaly['type'];
  severity: Anomaly['severity'];
  position: Vector3D;
  description: string;
}

export type WebSocketMessageData =
  | SimulationUpdateData
  | Agent[] // For agent_update with array
  | AgentUpdateData // For agent_update with single object
  | TrustScoreData[] // For trust_update with array
  | TrustUpdateData // For trust_update with single object
  | AnomalyAlertData
  | Record<string, never>; // For heartbeat (no data)

export interface WebSocketMessage {
  type: 'simulation_update' | 'agent_update' | 'trust_update' | 'anomaly_alert' | 'heartbeat';
  data: WebSocketMessageData;
  timestamp: number;
}

export interface AccessibilitySettings {
  highContrast: boolean;
  reducedMotion: boolean;
  screenReader: boolean;
  fontSize: 'small' | 'medium' | 'large';
  colorBlindMode: boolean;
}

export interface ViewportSettings {
  width: number;
  height: number;
  pixelRatio: number;
  isMobile: boolean;
  orientation: 'portrait' | 'landscape';
}

export interface CameraSettings {
  position: Vector3D;
  target: Vector3D;
  fov: number;
  near: number;
  far: number;
}

export interface ControlSettings {
  enablePan: boolean;
  enableZoom: boolean;
  enableRotate: boolean;
  zoomSpeed: number;
  panSpeed: number;
  rotateSpeed: number;
  minDistance: number;
  maxDistance: number;
  maxPolarAngle: number;
}

export interface ThemeSettings {
  primaryColor: string;
  secondaryColor: string;
  backgroundColor: string;
  surfaceColor: string;
  textColor: string;
  accentColor: string;
}

export interface DashboardMetrics {
  totalAgents: number;
  activeConnections: number;
  averageTrustScore: number;
  systemHealth: number;
  dataThroughput: number;
  anomalyCount: number;
  uptime: number;
  lastUpdate: number;
}

export interface NavigationItem {
  id: string;
  label: string;
  icon: string;
  path: string;
  children?: NavigationItem[];
  shortcut?: string;
  description?: string;
}

export interface TooltipData {
  title: string;
  content: string;
  position: Vector3D;
  persistent?: boolean;
  interactive?: boolean;
}

export interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
  errorInfo?: React.ErrorInfo;
}

export interface LoadingState {
  isLoading: boolean;
  progress?: number;
  message?: string;
  canCancel?: boolean;
}

export interface ExportSettings {
  format: 'png' | 'jpg' | 'svg' | 'pdf' | 'json';
  quality: 'low' | 'medium' | 'high';
  includeAnnotations: boolean;
  includeMetadata: boolean;
  resolution?: number;
}

export interface FilterSettings {
  agentStatus?: Agent['status'][];
  trustScoreRange?: [number, number];
  timeRange?: [number, number];
  anomalyTypes?: Anomaly['type'][];
  showConnections: boolean;
  showLabels: boolean;
  showTerrain: boolean;
  showParticles: boolean;
}

export interface AnimationSettings {
  enabled: boolean;
  speed: number;
  interpolation: 'linear' | 'ease-in' | 'ease-out' | 'ease-in-out';
  loop: boolean;
  autoplay: boolean;
}

export interface AudioSettings {
  enabled: boolean;
  volume: number;
  soundEffects: boolean;
  ambientAudio: boolean;
  audioCues: boolean;
}

export interface CollaborationSettings {
  realTimeSync: boolean;
  sharedViews: boolean;
  annotationSharing: boolean;
  voiceChat: boolean;
  screenSharing: boolean;
}

export interface BackupSettings {
  autoSave: boolean;
  saveInterval: number; // minutes
  maxBackups: number;
  compression: boolean;
  encryption: boolean;
}

export interface NotificationSettings {
  desktopNotifications: boolean;
  soundNotifications: boolean;
  anomalyAlerts: boolean;
  systemUpdates: boolean;
  collaborationInvites: boolean;
}

export interface KeyboardShortcut {
  key: string;
  ctrl?: boolean;
  alt?: boolean;
  shift?: boolean;
  meta?: boolean;
  action: string;
  description: string;
  category: 'navigation' | 'view' | 'simulation' | 'export' | 'accessibility';
}

export interface PluginPermissions {
  read?: boolean;
  write?: boolean;
  execute?: boolean;
  network?: boolean;
  filesystem?: boolean;
}

export interface PluginSettings {
  apiEndpoint?: string;
  timeout?: number;
  retryCount?: number;
  cacheEnabled?: boolean;
  debugMode?: boolean;
  customConfig?: Record<string, string | number | boolean>;
}

export interface PluginConfig {
  id: string;
  name: string;
  version: string;
  enabled: boolean;
  permissions: (keyof PluginPermissions)[];
  settings: PluginSettings;
}

export interface WorkspaceSettings {
  name: string;
  description?: string;
  created: number;
  modified: number;
  tags: string[];
  isPublic: boolean;
  collaborators: string[];
  plugins: PluginConfig[];
}

export interface SystemInfo {
  version: string;
  build: string;
  platform: string;
  webGLSupport: boolean;
  maxTextureSize: number;
  maxViewportSize: number;
  supportedExtensions: string[];
}

export interface LogData {
  error?: Error;
  stack?: string;
  component?: string;
  action?: string;
  duration?: number;
  metadata?: Record<string, string | number | boolean>;
}

export interface LogEntry {
  timestamp: number;
  level: 'debug' | 'info' | 'warn' | 'error';
  category: string;
  message: string;
  data?: LogData;
  userId?: string;
  sessionId?: string;
}

export interface CacheSettings {
  enabled: boolean;
  maxSize: number; // MB
  ttl: number; // seconds
  strategy: 'lru' | 'lfu' | 'fifo';
  compression: boolean;
}

export interface NetworkSettings {
  timeout: number;
  retryAttempts: number;
  retryDelay: number;
  maxConcurrentRequests: number;
  enableCompression: boolean;
  enableCaching: boolean;
}

export interface SecuritySettings {
  encryption: boolean;
  authentication: boolean;
  authorization: boolean;
  auditLogging: boolean;
  dataSanitization: boolean;
  corsEnabled: boolean;
}

export interface LocalizationSettings {
  language: string;
  timezone: string;
  dateFormat: string;
  timeFormat: string;
  numberFormat: string;
  currency: string;
}

export interface CustomizationSettings {
  theme: ThemeSettings;
  layout: 'default' | 'compact' | 'expanded';
  sidebarCollapsed: boolean;
  toolbarPosition: 'top' | 'bottom' | 'left' | 'right';
  panelArrangement: string[];
  customCSS?: string;
  customJS?: string;
}

export interface WebhookConfig {
  id: string;
  url: string;
  events: ('agent_update' | 'trust_update' | 'anomaly_alert' | 'simulation_state_change')[];
  enabled: boolean;
  secret?: string;
  retryPolicy?: {
    maxAttempts: number;
    backoffMultiplier: number;
    initialDelay: number;
  };
}

export interface DataSourceConfig {
  endpoint?: string;
  authentication?: {
    type: 'none' | 'basic' | 'bearer' | 'apikey';
    credentials?: Record<string, string>;
  };
  pollingInterval?: number;
  timeout?: number;
  headers?: Record<string, string>;
}

export interface DataSource {
  id: string;
  type: 'rest' | 'graphql' | 'websocket' | 'database' | 'file';
  config: DataSourceConfig;
  enabled: boolean;
  lastSync?: number;
  status: 'active' | 'error' | 'syncing';
}

export interface IntegrationSettings {
  apiKeys: Record<string, string>;
  webhooks: WebhookConfig[];
  dataSources: DataSource[];
}

export interface DebugSettings {
  enabled: boolean;
  verboseLogging: boolean;
  performanceMonitoring: boolean;
  memoryProfiling: boolean;
  networkTracing: boolean;
  showFPS: boolean;
  showMetrics: boolean;
}

export interface HelpSettings {
  showTips: boolean;
  showShortcuts: boolean;
  tutorialMode: boolean;
  documentationUrl: string;
  supportUrl: string;
  feedbackUrl: string;
}

export interface Settings {
  accessibility: AccessibilitySettings;
  viewport: ViewportSettings;
  camera: CameraSettings;
  controls: ControlSettings;
  theme: ThemeSettings;
  dashboard: DashboardMetrics;
  navigation: NavigationItem[];
  filters: FilterSettings;
  animation: AnimationSettings;
  audio: AudioSettings;
  collaboration: CollaborationSettings;
  backup: BackupSettings;
  notifications: NotificationSettings;
  keyboard: KeyboardShortcut[];
  workspace: WorkspaceSettings;
  system: SystemInfo;
  cache: CacheSettings;
  network: NetworkSettings;
  security: SecuritySettings;
  localization: LocalizationSettings;
  customization: CustomizationSettings;
  integrations: IntegrationSettings;
  debug: DebugSettings;
  help: HelpSettings;
}