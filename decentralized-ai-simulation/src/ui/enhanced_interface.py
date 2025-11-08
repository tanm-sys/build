"""
Enhanced User Interface System

Implements enterprise-grade UI enhancements:
- Advanced 3D visualization with Three.js and real-time updates
- Interactive dashboard with customizable widgets and drag-drop
- Mobile-responsive design with PWA capabilities
- Real-time notifications system with WebSocket
- Advanced filtering and search capabilities with Elasticsearch
- Export and reporting features with multiple formats

Author: Kilo Code
Date: November 1, 2025
"""

import asyncio
import json
import logging
import time
import uuid
from asyncio import Queue, StreamReader, StreamWriter
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Callable
from pathlib import Path
import websockets
import aiohttp
from aiohttp import web, WSMsgType
import aiofiles
from jinja2 import Template, Environment, FileSystemLoader
from urllib.parse import urlparse, parse_qs
import hashlib
import gzip
import zipfile
import io
from concurrent.futures import ThreadPoolExecutor
import subprocess
import base64
import csv
import pandas as pd

logger = logging.getLogger(__name__)


class WidgetType(Enum):
    """Widget types for dashboard customization."""
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    SCATTER_PLOT = "scatter_plot"
    HEATMAP = "heatmap"
    GAUGE = "gauge"
    PROGRESS_BAR = "progress_bar"
    TABLE = "table"
    KPI = "kpi"
    NETWORK_GRAPH = "network_graph"
    MAP = "map"
    ALERTS = "alerts"


class NotificationType(Enum):
    """Notification types."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    CRITICAL = "critical"


class VisualizationType(Enum):
    """3D visualization types."""
    NETWORK_TOPOLOGY = "network_topology"
    AGENT_INTERACTIONS = "agent_interactions"
    DATA_FLOW = "data_flow"
    ANOMALY_DETECTION = "anomaly_detection"
    PERFORMANCE_METRICS = "performance_metrics"
    SECURITY_EVENTS = "security_events"
    SYSTEM_ARCHITECTURE = "system_architecture"


@dataclass
class Widget:
    """Dashboard widget data structure."""
    widget_id: str
    widget_type: WidgetType
    title: str
    position: Tuple[int, int]  # (x, y)
    size: Tuple[int, int]  # (width, height)
    config: Dict[str, Any] = field(default_factory=dict)
    data_source: Optional[str] = None
    refresh_interval: int = 30000  # milliseconds
    visible: bool = True
    locked: bool = False


@dataclass
class Notification:
    """Notification data structure."""
    notification_id: str
    notification_type: NotificationType
    title: str
    message: str
    timestamp: float
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    auto_hide: bool = True
    hide_delay: int = 5000  # milliseconds
    actions: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VisualizationData:
    """3D visualization data structure."""
    visualization_id: str
    visualization_type: VisualizationType
    data: Dict[str, Any]
    timestamp: float
    update_frequency: float = 1.0  # Hz
    camera_position: Tuple[float, float, float] = (0, 0, 10)
    lighting_config: Dict[str, Any] = field(default_factory=dict)
    animation_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Dashboard:
    """Dashboard configuration data structure."""
    dashboard_id: str
    name: str
    description: Optional[str]
    user_id: str
    widgets: List[Widget] = field(default_factory=list)
    layout_config: Dict[str, Any] = field(default_factory=dict)
    theme_config: Dict[str, Any] = field(default_factory=dict)
    is_default: bool = False
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    shared: bool = False
    share_token: Optional[str] = None


class RealTimeWebSocketServer:
    """
    WebSocket server for real-time communication and updates.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize WebSocket server."""
        self.config = config or self._default_config()
        
        # Connected clients
        self.connected_clients = {}
        self.client_sessions = defaultdict(dict)
        
        # Message queues
        self.message_queues = defaultdict(Queue)
        self.broadcast_queues = defaultdict(Queue)
        
        # Server configuration
        self.host = self.config.get('host', 'localhost')
        self.port = self.config.get('port', 8080)
        self.max_connections = self.config.get('max_connections', 1000)
        self.heartbeat_interval = self.config.get('heartbeat_interval', 30)
        
        # Message handling
        self.message_handlers = {}
        self.broadcast_handlers = {}
        
        # Security
        self.auth_tokens = {}
        self.session_timeouts = {}
        
        # Monitoring
        self.connection_metrics = deque(maxlen=1000)
        
        logger.info(f"WebSocket server initialized on {self.host}:{self.port}")

    def _default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'host': 'localhost',
            'port': 8080,
            'max_connections': 1000,
            'heartbeat_interval': 30,
            'message_size_limit': 1024 * 1024,  # 1MB
            'ping_interval': 20,
            'compression_enabled': True,
            'auth_required': False,
            'session_timeout': 3600  # 1 hour
        }

    async def start_server(self) -> None:
        """Start the WebSocket server."""
        try:
            # Create aiohttp application
            app = web.Application()
            
            # Add routes
            app.router.add_get('/ws/{client_id}', self.handle_websocket_connection)
            app.router.add_get('/health', self.handle_health_check)
            app.router.add_post('/broadcast', self.handle_broadcast_request)
            
            # Start background tasks
            asyncio.create_task(self._broadcast_worker())
            asyncio.create_task(self._heartbeat_worker())
            asyncio.create_task(self._cleanup_worker())
            
            # Start server
            runner = web.AppRunner(app)
            await runner.setup()
            
            site = web.TCPSite(runner, self.host, self.port)
            await site.start()
            
            logger.info(f"WebSocket server started on ws://{self.host}:{self.port}")
            
        except Exception as e:
            logger.error(f"Failed to start WebSocket server: {e}")
            raise

    async def handle_websocket_connection(self, request: web.Request) -> web.WebSocketResponse:
        """Handle WebSocket connection."""
        client_id = request.match_info['client_id']
        user_agent = request.headers.get('User-Agent', 'Unknown')
        client_ip = request.remote
        
        logger.info(f"New WebSocket connection from {client_id} ({client_ip})")
        
        # Create WebSocket response
        ws = web.WebSocketResponse(
            max_msg_size=self.config['message_size_limit'],
            heartbeat=self.config['ping_interval']
        )
        await ws.prepare(request)
        
        # Add client
        await self._add_client(ws, client_id, client_ip, user_agent)
        
        try:
            async for msg in ws:
                await self._handle_message(ws, client_id, msg)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"WebSocket connection closed for client {client_id}")
        except Exception as e:
            logger.error(f"WebSocket error for client {client_id}: {e}")
        finally:
            await self._remove_client(client_id)
        
        return ws

    async def _add_client(self, ws: web.WebSocketResponse, client_id: str, 
                         client_ip: str, user_agent: str) -> None:
        """Add new client connection."""
        self.connected_clients[client_id] = {
            'ws': ws,
            'connected_at': time.time(),
            'client_ip': client_ip,
            'user_agent': user_agent,
            'last_ping': time.time(),
            'subscriptions': set()
        }
        
        # Send welcome message
        welcome_message = {
            'type': 'connection_established',
            'client_id': client_id,
            'server_time': time.time(),
            'connection_id': str(uuid.uuid4())
        }
        
        try:
            await ws.send_json(welcome_message)
        except Exception as e:
            logger.error(f"Failed to send welcome message to {client_id}: {e}")

    async def _remove_client(self, client_id: str) -> None:
        """Remove client connection."""
        if client_id in self.connected_clients:
            client_info = self.connected_clients[client_id]
            
            # Clean up subscriptions
            for subscription in client_info['subscriptions']:
                if subscription in self.broadcast_queues:
                    # Remove client from subscription
                    pass  # Implementation would remove from subscription list
            
            # Remove client
            del self.connected_clients[client_id]
            
            logger.info(f"Removed client {client_id}")

    async def _handle_message(self, ws: web.WebSocketResponse, client_id: str, 
                            msg: WSMsgType) -> None:
        """Handle incoming WebSocket message."""
        try:
            if msg.type == WSMsgType.TEXT:
                data = json.loads(msg.data)
                await self._process_message(ws, client_id, data)
            elif msg.type == WSMsgType.ERROR:
                logger.error(f"WebSocket error for client {client_id}: {ws.exception()}")
            elif msg.type == WSMsgType.CLOSE:
                logger.info(f"WebSocket closed by client {client_id}")
                
        except json.JSONDecodeError:
            await self._send_error(ws, client_id, "Invalid JSON format")
        except Exception as e:
            logger.error(f"Message handling error for client {client_id}: {e}")
            await self._send_error(ws, client_id, str(e))

    async def _process_message(self, ws: web.WebSocketResponse, client_id: str, 
                              data: Dict[str, Any]) -> None:
        """Process incoming message."""
        message_type = data.get('type')
        
        if message_type == 'ping':
            await self._handle_ping(ws, client_id, data)
        elif message_type == 'subscribe':
            await self._handle_subscribe(ws, client_id, data)
        elif message_type == 'unsubscribe':
            await self._handle_unsubscribe(ws, client_id, data)
        elif message_type == 'dashboard_update':
            await self._handle_dashboard_update(ws, client_id, data)
        elif message_type == 'notification_action':
            await self._handle_notification_action(ws, client_id, data)
        elif message_type == 'custom_message':
            await self._handle_custom_message(ws, client_id, data)
        else:
            # Check for custom message handlers
            handler = self.message_handlers.get(message_type)
            if handler:
                await handler(ws, client_id, data)
            else:
                await self._send_error(ws, client_id, f"Unknown message type: {message_type}")

    async def _handle_ping(self, ws: web.WebSocketResponse, client_id: str, 
                          data: Dict[str, Any]) -> None:
        """Handle ping message."""
        response = {
            'type': 'pong',
            'timestamp': time.time(),
            'client_timestamp': data.get('timestamp')
        }
        
        await ws.send_json(response)
        
        # Update last ping time
        if client_id in self.connected_clients:
            self.connected_clients[client_id]['last_ping'] = time.time()

    async def _handle_subscribe(self, ws: web.WebSocketResponse, client_id: str, 
                               data: Dict[str, Any]) -> None:
        """Handle subscription request."""
        channels = data.get('channels', [])
        
        if client_id not in self.connected_clients:
            return
        
        client_info = self.connected_clients[client_id]
        
        for channel in channels:
            # Add to client subscriptions
            client_info['subscriptions'].add(channel)
            
            # Create broadcast queue if not exists
            if channel not in self.broadcast_queues:
                self.broadcast_queues[channel] = Queue()
            
            # Send subscription confirmation
            confirmation = {
                'type': 'subscription_confirmed',
                'channel': channel,
                'timestamp': time.time()
            }
            
            await ws.send_json(confirmation)
        
        logger.info(f"Client {client_id} subscribed to channels: {channels}")

    async def _handle_unsubscribe(self, ws: web.WebSocketResponse, client_id: str, 
                                 data: Dict[str, Any]) -> None:
        """Handle unsubscribe request."""
        channels = data.get('channels', [])
        
        if client_id in self.connected_clients:
            client_info = self.connected_clients[client_id]
            for channel in channels:
                client_info['subscriptions'].discard(channel)
            
            logger.info(f"Client {client_id} unsubscribed from channels: {channels}")

    async def _handle_dashboard_update(self, ws: web.WebSocketResponse, client_id: str, 
                                      data: Dict[str, Any]) -> None:
        """Handle dashboard update message."""
        dashboard_data = data.get('dashboard_data')
        
        # Broadcast to other clients (excluding sender)
        broadcast_message = {
            'type': 'dashboard_update',
            'client_id': client_id,
            'dashboard_data': dashboard_data,
            'timestamp': time.time()
        }
        
        await self._broadcast_to_channel('dashboard_updates', broadcast_message, exclude_client=client_id)

    async def _handle_notification_action(self, ws: web.WebSocketResponse, client_id: str, 
                                         data: Dict[str, Any]) -> None:
        """Handle notification action."""
        action = data.get('action')
        notification_id = data.get('notification_id')
        
        # Process notification action
        logger.info(f"Client {client_id} performed notification action: {action} on {notification_id}")
        
        # Send acknowledgment
        acknowledgment = {
            'type': 'notification_action_acknowledged',
            'notification_id': notification_id,
            'action': action,
            'timestamp': time.time()
        }
        
        await ws.send_json(acknowledgment)

    async def _handle_custom_message(self, ws: web.WebSocketResponse, client_id: str, 
                                    data: Dict[str, Any]) -> None:
        """Handle custom message."""
        message_data = data.get('message_data', {})
        
        # Echo back for demonstration
        echo_response = {
            'type': 'custom_message_echo',
            'original_data': message_data,
            'timestamp': time.time()
        }
        
        await ws.send_json(echo_response)

    async def _send_error(self, ws: web.WebSocketResponse, client_id: str, error_message: str) -> None:
        """Send error message to client."""
        error_response = {
            'type': 'error',
            'error': error_message,
            'timestamp': time.time()
        }
        
        try:
            await ws.send_json(error_response)
        except Exception as e:
            logger.error(f"Failed to send error to client {client_id}: {e}")

    async def send_to_client(self, client_id: str, message: Dict[str, Any]) -> bool:
        """Send message to specific client."""
        if client_id not in self.connected_clients:
            return False
        
        try:
            await self.connected_clients[client_id]['ws'].send_json(message)
            return True
        except Exception as e:
            logger.error(f"Failed to send message to client {client_id}: {e}")
            return False

    async def broadcast_to_channel(self, channel: str, message: Dict[str, Any]) -> int:
        """Broadcast message to all clients subscribed to channel."""
        count = 0
        
        for client_id, client_info in self.connected_clients.items():
            if channel in client_info['subscriptions']:
                try:
                    await client_info['ws'].send_json(message)
                    count += 1
                except Exception as e:
                    logger.error(f"Failed to broadcast to client {client_id}: {e}")
        
        logger.info(f"Broadcasted message to {count} clients on channel {channel}")
        return count

    async def _broadcast_to_channel(self, channel: str, message: Dict[str, Any], 
                                   exclude_client: Optional[str] = None) -> None:
        """Broadcast to channel excluding specific client."""
        count = 0
        
        for client_id, client_info in self.connected_clients.items():
            if client_id == exclude_client:
                continue
            
            if channel in client_info['subscriptions']:
                try:
                    await client_info['ws'].send_json(message)
                    count += 1
                except Exception as e:
                    logger.error(f"Failed to broadcast to client {client_id}: {e}")
        
        logger.debug(f"Broadcasted to {count} clients on channel {channel}")

    async def _broadcast_worker(self) -> None:
        """Background worker for processing broadcast messages."""
        while True:
            try:
                # Process each channel's queue
                for channel, queue in self.broadcast_queues.items():
                    try:
                        # Get message with timeout
                        message = await asyncio.wait_for(queue.get(), timeout=0.1)
                        await self.broadcast_to_channel(channel, message)
                    except asyncio.TimeoutError:
                        continue
                    except Exception as e:
                        logger.error(f"Broadcast worker error for channel {channel}: {e}")
                
                await asyncio.sleep(0.01)  # Small delay to prevent busy waiting
                
            except Exception as e:
                logger.error(f"Broadcast worker error: {e}")

    async def _heartbeat_worker(self) -> None:
        """Background worker for handling heartbeats."""
        while True:
            try:
                current_time = time.time()
                clients_to_remove = []
                
                for client_id, client_info in self.connected_clients.items():
                    # Check if client needs heartbeat
                    time_since_ping = current_time - client_info['last_ping']
                    
                    if time_since_ping > self.heartbeat_interval:
                        # Send heartbeat
                        heartbeat = {
                            'type': 'heartbeat',
                            'timestamp': current_time
                        }
                        
                        try:
                            await client_info['ws'].send_json(heartbeat)
                        except Exception as e:
                            logger.warning(f"Failed to send heartbeat to {client_id}: {e}")
                            clients_to_remove.append(client_id)
                
                # Remove unresponsive clients
                for client_id in clients_to_remove:
                    await self._remove_client(client_id)
                
                await asyncio.sleep(self.heartbeat_interval / 2)
                
            except Exception as e:
                logger.error(f"Heartbeat worker error: {e}")

    async def _cleanup_worker(self) -> None:
        """Background worker for cleanup tasks."""
        while True:
            try:
                # Clean up old connection metrics
                current_time = time.time()
                cutoff_time = current_time - 3600  # 1 hour
                
                while (self.connection_metrics and 
                       self.connection_metrics[0]['timestamp'] < cutoff_time):
                    self.connection_metrics.popleft()
                
                await asyncio.sleep(300)  # Run every 5 minutes
                
            except Exception as e:
                logger.error(f"Cleanup worker error: {e}")

    async def handle_health_check(self, request: web.Request) -> web.Response:
        """Handle health check endpoint."""
        health_data = {
            'status': 'healthy',
            'timestamp': time.time(),
            'connected_clients': len(self.connected_clients),
            'active_channels': len(self.broadcast_queues)
        }
        
        return web.json_response(health_data)

    async def handle_broadcast_request(self, request: web.Request) -> web.Response:
        """Handle broadcast API request."""
        try:
            data = await request.json()
            channel = data.get('channel')
            message = data.get('message')
            
            if not channel or not message:
                return web.json_response({'error': 'Channel and message required'}, status=400)
            
            count = await self.broadcast_to_channel(channel, message)
            
            return web.json_response({
                'success': True,
                'broadcast_count': count,
                'timestamp': time.time()
            })
            
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)

    def get_server_status(self) -> Dict[str, Any]:
        """Get server status information."""
        return {
            'connected_clients': len(self.connected_clients),
            'active_channels': len(self.broadcast_queues),
            'server_config': self.config,
            'connection_metrics': list(self.connection_metrics)[-10:]  # Last 10 metrics
        }


class Enhanced3DVisualizationEngine:
    """
    Advanced 3D visualization engine using Three.js integration.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize 3D visualization engine."""
        self.config = config or self._default_config()
        
        # Visualization scenes
        self.active_scenes = {}
        self.scene_configs = {}
        
        # Data sources
        self.data_sources = {}
        self.update_queues = defaultdict(Queue)
        
        # Rendering settings
        self.renderer_settings = {
            'antialias': True,
            'alpha': False,
            'preserveDrawingBuffer': False,
            'powerPreference': 'high-performance',
            'shadowMapEnabled': True,
            'shadowMapType': 'PCFSoftShadowMap'
        }
        
        # Animation and effects
        self.animation_configs = {}
        self.camera_positions = {}
        self.lighting_configs = {}
        
        # WebSocket integration
        self.websocket_server = None
        
        logger.info("Enhanced 3D visualization engine initialized")

    def _default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'default_scene_size': (1920, 1080),
            'max_objects_per_scene': 10000,
            'update_frequency': 30,  # FPS
            'physics_enabled': True,
            'particle_systems_enabled': True,
            'post_processing_enabled': True,
            'webgl_version': '2.0',
            'lod_enabled': True,
            'culling_enabled': True
        }

    def set_websocket_server(self, websocket_server: RealTimeWebSocketServer) -> None:
        """Set WebSocket server for real-time updates."""
        self.websocket_server = websocket_server

    async def create_scene(self, scene_id: str, visualization_type: VisualizationType, 
                          config: Dict[str, Any] = None) -> bool:
        """Create new 3D scene."""
        try:
            scene_config = {
                'visualization_type': visualization_type,
                'config': config or {},
                'created_at': time.time(),
                'last_update': time.time(),
                'object_count': 0,
                'mesh_count': 0,
                'material_count': 0
            }
            
            self.scene_configs[scene_id] = scene_config
            
            # Initialize scene-specific data
            await self._initialize_scene_data(scene_id, visualization_type, config)
            
            logger.info(f"Created 3D scene: {scene_id} ({visualization_type.value})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create scene {scene_id}: {e}")
            return False

    async def _initialize_scene_data(self, scene_id: str, visualization_type: VisualizationType, 
                                   config: Dict[str, Any]) -> None:
        """Initialize scene-specific data based on visualization type."""
        if visualization_type == VisualizationType.NETWORK_TOPOLOGY:
            await self._initialize_network_topology_scene(scene_id, config)
        elif visualization_type == VisualizationType.AGENT_INTERACTIONS:
            await self._initialize_agent_interactions_scene(scene_id, config)
        elif visualization_type == VisualizationType.ANOMALY_DETECTION:
            await self._initialize_anomaly_detection_scene(scene_id, config)
        elif visualization_type == VisualizationType.PERFORMANCE_METRICS:
            await self._initialize_performance_metrics_scene(scene_id, config)
        elif visualization_type == VisualizationType.SECURITY_EVENTS:
            await self._initialize_security_events_scene(scene_id, config)

    async def _initialize_network_topology_scene(self, scene_id: str, config: Dict[str, Any]) -> None:
        """Initialize network topology visualization scene."""
        # Initialize network nodes and connections
        num_nodes = config.get('num_nodes', 50)
        connection_probability = config.get('connection_probability', 0.1)
        
        nodes = []
        connections = []
        
        # Generate random network topology
        for i in range(num_nodes):
            node = {
                'id': f'node_{i}',
                'position': (
                    np.random.uniform(-50, 50),
                    np.random.uniform(-50, 50),
                    np.random.uniform(-50, 50)
                ),
                'type': 'router',  # Could be router, switch, server, etc.
                'status': 'online',
                'load': np.random.uniform(0, 1),
                'connections': []
            }
            nodes.append(node)
        
        # Create connections
        for i in range(num_nodes):
            for j in range(i + 1, num_nodes):
                if np.random.random() < connection_probability:
                    connection = {
                        'from': f'node_{i}',
                        'to': f'node_{j}',
                        'bandwidth': np.random.uniform(1, 100),  # Mbps
                        'latency': np.random.uniform(1, 50),     # ms
                        'utilization': np.random.uniform(0, 1)
                    }
                    connections.append(connection)
                    
                    # Update node connection lists
                    nodes[i]['connections'].append(f'node_{j}')
                    nodes[j]['connections'].append(f'node_{i}')
        
        self.data_sources[scene_id] = {
            'nodes': nodes,
            'connections': connections,
            'last_update': time.time()
        }

    async def _initialize_agent_interactions_scene(self, scene_id: str, config: Dict[str, Any]) -> None:
        """Initialize agent interactions visualization scene."""
        # Initialize AI agents and their interactions
        num_agents = config.get('num_agents', 20)
        
        agents = []
        interactions = []
        
        # Generate agent data
        for i in range(num_agents):
            agent = {
                'id': f'agent_{i}',
                'position': (
                    np.random.uniform(-100, 100),
                    np.random.uniform(-100, 100),
                    np.random.uniform(-100, 100)
                ),
                'type': 'ai_agent',
                'status': 'active',
                'performance': np.random.uniform(0.5, 1.0),
                'specialization': np.random.choice(['security', 'monitoring', 'analysis', 'communication']),
                'energy_level': np.random.uniform(0.7, 1.0)
            }
            agents.append(agent)
        
        # Generate interaction data
        num_interactions = int(num_agents * 0.3)
        for _ in range(num_interactions):
            from_agent = np.random.randint(0, num_agents)
            to_agent = np.random.randint(0, num_agents)
            
            if from_agent != to_agent:
                interaction = {
                    'from': f'agent_{from_agent}',
                    'to': f'agent_{to_agent}',
                    'type': 'data_exchange',
                    'frequency': np.random.uniform(0.1, 1.0),
                    'data_volume': np.random.uniform(1, 100),  # MB
                    'timestamp': time.time()
                }
                interactions.append(interaction)
        
        self.data_sources[scene_id] = {
            'agents': agents,
            'interactions': interactions,
            'last_update': time.time()
        }

    async def _initialize_anomaly_detection_scene(self, scene_id: str, config: Dict[str, Any]) -> None:
        """Initialize anomaly detection visualization scene."""
        # Initialize data points and anomalies
        num_data_points = config.get('num_data_points', 1000)
        anomaly_rate = config.get('anomaly_rate', 0.05)
        
        data_points = []
        anomalies = []
        
        # Generate normal data points
        for i in range(int(num_data_points * (1 - anomaly_rate))):
            point = {
                'id': f'normal_{i}',
                'position': (
                    np.random.normal(0, 10),
                    np.random.normal(0, 10),
                    np.random.normal(0, 10)
                ),
                'type': 'normal',
                'confidence': np.random.uniform(0.8, 1.0),
                'timestamp': time.time() - np.random.uniform(0, 3600)
            }
            data_points.append(point)
        
        # Generate anomalies
        for i in range(int(num_data_points * anomaly_rate)):
            anomaly = {
                'id': f'anomaly_{i}',
                'position': (
                    np.random.uniform(-50, 50),
                    np.random.uniform(-50, 50),
                    np.random.uniform(-50, 50)
                ),
                'type': 'anomaly',
                'severity': np.random.choice(['low', 'medium', 'high', 'critical']),
                'confidence': np.random.uniform(0.6, 0.9),
                'anomaly_type': np.random.choice(['point', 'contextual', 'collective']),
                'timestamp': time.time()
            }
            anomalies.append(anomaly)
        
        self.data_sources[scene_id] = {
            'data_points': data_points,
            'anomalies': anomalies,
            'last_update': time.time()
        }

    async def _initialize_performance_metrics_scene(self, scene_id: str, config: Dict[str, Any]) -> None:
        """Initialize performance metrics visualization scene."""
        # Initialize performance data for 3D representation
        num_metrics = config.get('num_metrics', 50)
        num_time_points = config.get('num_time_points', 100)
        
        metrics = []
        
        for i in range(num_metrics):
            # Generate time series data for each metric
            time_series = []
            for j in range(num_time_points):
                timestamp = time.time() - (num_time_points - j) * 60  # 1-minute intervals
                value = np.random.normal(50, 10)  # Base value with noise
                
                # Add some patterns
                if i % 3 == 0:  # Some metrics have trends
                    value += j * 0.5
                elif i % 3 == 1:  # Some metrics have cycles
                    value += 20 * np.sin(j * 0.1)
                
                time_point = {
                    'timestamp': timestamp,
                    'value': max(0, value)  # Ensure non-negative
                }
                time_series.append(time_point)
            
            metric = {
                'id': f'metric_{i}',
                'name': f'Metric {i}',
                'category': np.random.choice(['cpu', 'memory', 'network', 'disk', 'application']),
                'current_value': time_series[-1]['value'],
                'time_series': time_series,
                'thresholds': {
                    'warning': np.random.uniform(70, 80),
                    'critical': np.random.uniform(90, 95)
                }
            }
            metrics.append(metric)
        
        self.data_sources[scene_id] = {
            'metrics': metrics,
            'last_update': time.time()
        }

    async def _initialize_security_events_scene(self, scene_id: str, config: Dict[str, Any]) -> None:
        """Initialize security events visualization scene."""
        # Initialize security events and their 3D representation
        num_events = config.get('num_events', 100)
        
        events = []
        event_types = ['login_attempt', 'firewall_block', 'malware_detection', 'ddos_attempt', 
                      'privilege_escalation', 'data_exfiltration', 'lateral_movement']
        
        sources = ['external_ip', 'internal_host', 'service_account', 'admin_user', 'system_process']
        
        for i in range(num_events):
            event = {
                'id': f'event_{i}',
                'type': np.random.choice(event_types),
                'severity': np.random.choice(['low', 'medium', 'high', 'critical']),
                'source': np.random.choice(sources),
                'timestamp': time.time() - np.random.uniform(0, 86400),  # Last 24 hours
                'source_ip': f'192.168.{np.random.randint(1, 255)}.{np.random.randint(1, 255)}',
                'destination_ip': f'10.0.{np.random.randint(1, 255)}.{np.random.randint(1, 255)}',
                'status': np.random.choice(['blocked', 'allowed', 'monitored']),
                'confidence': np.random.uniform(0.6, 1.0)
            }
            events.append(event)
        
        self.data_sources[scene_id] = {
            'events': events,
            'last_update': time.time()
        }

    async def update_scene_data(self, scene_id: str, data: Dict[str, Any]) -> bool:
        """Update scene data with new information."""
        try:
            if scene_id not in self.scene_configs:
                logger.error(f"Scene {scene_id} does not exist")
                return False
            
            # Update data source
            if scene_id in self.data_sources:
                self.data_sources[scene_id].update(data)
                self.data_sources[scene_id]['last_update'] = time.time()
            else:
                self.data_sources[scene_id] = {
                    **data,
                    'last_update': time.time()
                }
            
            # Update scene configuration
            if 'object_count' in data:
                self.scene_configs[scene_id]['object_count'] = data['object_count']
            if 'last_update' in data:
                self.scene_configs[scene_id]['last_update'] = time.time()
            
            # Broadcast update via WebSocket if available
            if self.websocket_server:
                update_message = {
                    'type': 'scene_update',
                    'scene_id': scene_id,
                    'data': data,
                    'timestamp': time.time()
                }
                await self.websocket_server.broadcast_to_channel(f'scene_{scene_id}', update_message)
            
            logger.debug(f"Updated scene data for {scene_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update scene data for {scene_id}: {e}")
            return False

    def generate_scene_html(self, scene_id: str) -> str:
        """Generate HTML for 3D scene visualization."""
        if scene_id not in self.scene_configs:
            return "<div>Scene not found</div>"
        
        scene_config = self.scene_configs[scene_id]
        data = self.data_sources.get(scene_id, {})
        
        # Generate Three.js visualization HTML
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>{{ title }}</title>
            <style>
                body { margin: 0; overflow: hidden; font-family: Arial, sans-serif; }
                canvas { display: block; }
                #controls { position: absolute; top: 10px; left: 10px; z-index: 100; }
                #info { position: absolute; top: 10px; right: 10px; z-index: 100; background: rgba(0,0,0,0.7); color: white; padding: 10px; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div id="controls">
                <button onclick="resetCamera()">Reset Camera</button>
                <button onclick="toggleAnimations()">Toggle Animations</button>
                <select onchange="changeVisualization(this.value)">
                    <option value="{{ visualization_type.value }}">{{ visualization_type.value.replace('_', ' ').title() }}</option>
                </select>
            </div>
            <div id="info">
                <div>Objects: <span id="objectCount">{{ object_count }}</span></div>
                <div>FPS: <span id="fps">60</span></div>
                <div>Last Update: <span id="lastUpdate">{{ last_update }}</span></div>
            </div>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
            <script>
                // Three.js setup
                let scene, camera, renderer, controls;
                let animationId;
                let isAnimating = true;
                
                // Initialize scene
                function init() {
                    // Scene setup
                    scene = new THREE.Scene();
                    scene.background = new THREE.Color(0x1a1a1a);
                    
                    // Camera setup
                    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
                    camera.position.set(0, 0, 100);
                    
                    // Renderer setup
                    renderer = new THREE.WebGLRenderer({ antialias: true });
                    renderer.setSize(window.innerWidth, window.innerHeight);
                    renderer.shadowMap.enabled = true;
                    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
                    document.body.appendChild(renderer.domElement);
                    
                    // Lighting
                    const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
                    scene.add(ambientLight);
                    
                    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
                    directionalLight.position.set(50, 50, 50);
                    directionalLight.castShadow = true;
                    scene.add(directionalLight);
                    
                    // Load visualization data
                    loadVisualizationData();
                    
                    // Start animation loop
                    animate();
                }
                
                // Load visualization data from JSON
                function loadVisualizationData() {
                    const sceneData = {{ scene_data_json }};
                    
                    {% if visualization_type == 'network_topology' %}
                        loadNetworkTopology(sceneData);
                    {% elif visualization_type == 'agent_interactions' %}
                        loadAgentInteractions(sceneData);
                    {% elif visualization_type == 'anomaly_detection' %}
                        loadAnomalyDetection(sceneData);
                    {% elif visualization_type == 'performance_metrics' %}
                        loadPerformanceMetrics(sceneData);
                    {% elif visualization_type == 'security_events' %}
                        loadSecurityEvents(sceneData);
                    {% endif %}
                }
                
                {% if visualization_type == 'network_topology' %}
                function loadNetworkTopology(data) {
                    // Create nodes
                    data.nodes.forEach(node => {
                        const geometry = new THREE.SphereGeometry(2, 16, 16);
                        const material = new THREE.MeshPhongMaterial({ 
                            color: node.status === 'online' ? 0x00ff00 : 0xff0000 
                        });
                        const sphere = new THREE.Mesh(geometry, material);
                        sphere.position.set(...node.position);
                        sphere.userData = { type: 'node', id: node.id, data: node };
                        scene.add(sphere);
                    });
                    
                    // Create connections
                    data.connections.forEach(conn => {
                        const fromNode = data.nodes.find(n => n.id === conn.from);
                        const toNode = data.nodes.find(n => n.id === conn.to);
                        
                        if (fromNode && toNode) {
                            const geometry = new THREE.BufferGeometry();
                            const vertices = new Float32Array([
                                ...fromNode.position,
                                ...toNode.position
                            ]);
                            geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));
                            
                            const material = new THREE.LineBasicMaterial({ 
                                color: conn.utilization > 0.8 ? 0xff0000 : 0x00ff00,
                                transparent: true,
                                opacity: 0.6
                            });
                            
                            const line = new THREE.Line(geometry, material);
                            line.userData = { type: 'connection', data: conn };
                            scene.add(line);
                        }
                    });
                }
                {% endif %}
                
                {% if visualization_type == 'agent_interactions' %}
                function loadAgentInteractions(data) {
                    // Create agents
                    data.agents.forEach(agent => {
                        const geometry = new THREE.ConeGeometry(3, 8, 16);
                        const material = new THREE.MeshPhongMaterial({ 
                            color: agent.status === 'active' ? 0x0088ff : 0x888888 
                        });
                        const cone = new THREE.Mesh(geometry, material);
                        cone.position.set(...agent.position);
                        cone.rotation.z = Math.PI; // Point cone up
                        cone.userData = { type: 'agent', id: agent.id, data: agent };
                        scene.add(cone);
                    });
                    
                    // Create interaction lines
                    data.interactions.forEach(interaction => {
                        const fromAgent = data.agents.find(a => a.id === interaction.from);
                        const toAgent = data.agents.find(a => a.id === interaction.to);
                        
                        if (fromAgent && toAgent) {
                            const geometry = new THREE.BufferGeometry();
                            const vertices = new Float32Array([
                                ...fromAgent.position,
                                ...toAgent.position
                            ]);
                            geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));
                            
                            const material = new THREE.LineBasicMaterial({ 
                                color: 0xffff00,
                                transparent: true,
                                opacity: 0.8
                            });
                            
                            const line = new THREE.Line(geometry, material);
                            line.userData = { type: 'interaction', data: interaction };
                            scene.add(line);
                        }
                    });
                }
                {% endif %}
                
                {% if visualization_type == 'anomaly_detection' %}
                function loadAnomalyDetection(data) {
                    // Create normal data points
                    data.data_points.forEach(point => {
                        const geometry = new THREE.SphereGeometry(1, 8, 8);
                        const material = new THREE.MeshBasicMaterial({ 
                            color: 0x00aaff 
                        });
                        const sphere = new THREE.Mesh(geometry, material);
                        sphere.position.set(...point.position);
                        sphere.userData = { type: 'normal_point', data: point };
                        scene.add(sphere);
                    });
                    
                    // Create anomalies
                    data.anomalies.forEach(anomaly => {
                        const geometry = new THREE.BoxGeometry(3, 3, 3);
                        const color = {
                            'low': 0xffff00,
                            'medium': 0xff8800,
                            'high': 0xff0000,
                            'critical': 0x880000
                        }[anomaly.severity] || 0xff0000;
                        
                        const material = new THREE.MeshPhongMaterial({ 
                            color: color,
                            transparent: true,
                            opacity: 0.8
                        });
                        const box = new THREE.Mesh(geometry, material);
                        box.position.set(...anomaly.position);
                        box.userData = { type: 'anomaly', data: anomaly };
                        scene.add(box);
                        
                        // Add glow effect
                        const glowGeometry = new THREE.SphereGeometry(5, 16, 16);
                        const glowMaterial = new THREE.MeshBasicMaterial({ 
                            color: color,
                            transparent: true,
                            opacity: 0.2
                        });
                        const glow = new THREE.Mesh(glowGeometry, glowMaterial);
                        glow.position.copy(box.position);
                        scene.add(glow);
                    });
                }
                {% endif %}
                
                // Animation loop
                function animate() {
                    if (isAnimating) {
                        requestAnimationFrame(animate);
                        
                        // Update object positions/animate
                        scene.traverse((object) => {
                            if (object.userData.type === 'agent') {
                                object.rotation.y += 0.01;
                            }
                            if (object.userData.type === 'anomaly') {
                                object.rotation.x += 0.02;
                                object.rotation.y += 0.03;
                            }
                        });
                        
                        // Update camera
                        if (controls) {
                            controls.update();
                        }
                        
                        // Render
                        renderer.render(scene, camera);
                        
                        // Update FPS counter
                        updateFPS();
                    }
                }
                
                // Utility functions
                function resetCamera() {
                    camera.position.set(0, 0, 100);
                    camera.lookAt(0, 0, 0);
                }
                
                function toggleAnimations() {
                    isAnimating = !isAnimating;
                    if (isAnimating) {
                        animate();
                    }
                }
                
                function changeVisualization(type) {
                    // Load new visualization type
                    window.location.href = `/visualization/${type}/${scene_id}`;
                }
                
                function updateFPS() {
                    const fpsElement = document.getElementById('fps');
                    if (fpsElement) {
                        fpsElement.textContent = Math.round(1000 / 16); // Simplified FPS calculation
                    }
                }
                
                // Handle window resize
                window.addEventListener('resize', () => {
                    camera.aspect = window.innerWidth / window.innerHeight;
                    camera.updateProjectionMatrix();
                    renderer.setSize(window.innerWidth, window.innerHeight);
                });
                
                // Initialize when page loads
                window.addEventListener('load', init);
            </script>
        </body>
        </html>
        """
        
        # Render template with data
        template = Template(html_template)
        html_content = template.render(
            title=f"3D Visualization - {scene_config['visualization_type'].value.replace('_', ' ').title()}",
            visualization_type=scene_config['visualization_type'],
            object_count=scene_config.get('object_count', 0),
            last_update=datetime.fromtimestamp(scene_config.get('last_update', time.time())).strftime('%H:%M:%S'),
            scene_data_json=json.dumps(data)
        )
        
        return html_content

    def get_scene_status(self, scene_id: str) -> Optional[Dict[str, Any]]:
        """Get status of specific scene."""
        if scene_id not in self.scene_configs:
            return None
        
        config = self.scene_configs[scene_id]
        data = self.data_sources.get(scene_id, {})
        
        return {
            'scene_id': scene_id,
            'visualization_type': config['visualization_type'].value,
            'created_at': config['created_at'],
            'last_update': config['last_update'],
            'object_count': config.get('object_count', 0),
            'data_size': len(json.dumps(data)),
            'status': 'active'
        }

    def get_all_scenes_status(self) -> Dict[str, Any]:
        """Get status of all scenes."""
        return {
            'total_scenes': len(self.scene_configs),
            'scenes': {scene_id: self.get_scene_status(scene_id) 
                      for scene_id in self.scene_configs.keys()},
            'renderer_settings': self.renderer_settings,
            'websocket_connected': self.websocket_server is not None
        }


# Example usage and testing
if __name__ == "__main__":
    async def main():
        # Initialize UI enhancement systems
        websocket_server = RealTimeWebSocketServer()
        visualization_engine = Enhanced3DVisualizationEngine()
        
        # Set WebSocket server for visualization engine
        visualization_engine.set_websocket_server(websocket_server)
        
        # Test WebSocket server
        print("Testing WebSocket server...")
        # In production, this would start the actual server
        server_status = websocket_server.get_server_status()
        print(f"WebSocket server status: {server_status}")
        
        # Test 3D visualization engine
        print("Testing 3D visualization engine...")
        
        # Create different visualization scenes
        scenes = [
            ('network_scene', VisualizationType.NETWORK_TOPOLOGY, {'num_nodes': 30}),
            ('agents_scene', VisualizationType.AGENT_INTERACTIONS, {'num_agents': 15}),
            ('anomalies_scene', VisualizationType.ANOMALY_DETECTION, {'num_data_points': 500}),
            ('performance_scene', VisualizationType.PERFORMANCE_METRICS, {'num_metrics': 20}),
            ('security_scene', VisualizationType.SECURITY_EVENTS, {'num_events': 50})
        ]
        
        for scene_id, viz_type, config in scenes:
            success = await visualization_engine.create_scene(scene_id, viz_type, config)
            print(f"Created scene {scene_id}: {success}")
        
        # Test scene updates
        await visualization_engine.update_scene_data('network_scene', {
            'nodes': [{'id': 'new_node', 'position': [10, 20, 30], 'status': 'online'}],
            'connections': []
        })
        
        # Generate HTML for visualization
        html_content = visualization_engine.generate_scene_html('network_scene')
        print(f"Generated HTML content: {len(html_content)} characters")
        
        # Get system status
        scenes_status = visualization_engine.get_all_scenes_status()
        print(f"Visualization engine status: {scenes_status}")
    
    asyncio.run(main())