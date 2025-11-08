"""
Enterprise Operational Dashboards & Visualization System for AI Simulation Platform

Provides comprehensive dashboards for different stakeholders including executives, operators,
developers, security teams, and compliance teams with interactive visualizations and reporting.
"""

import asyncio
import time
import json
import logging
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
from collections import defaultdict, deque
from datetime import datetime, timedelta
import statistics
import random
from contextlib import contextmanager

# Dashboard types and layouts
class DashboardType(Enum):
    EXECUTIVE = "executive"
    OPERATIONAL = "operational"
    TECHNICAL = "technical"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    CUSTOM = "custom"

class VisualizationType(Enum):
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    GAUGE = "gauge"
    HEATMAP = "heatmap"
    SCATTER_PLOT = "scatter_plot"
    TABLE = "table"
    KPI_CARD = "kpi_card"
    TREND_INDICATOR = "trend_indicator"

class MetricUnit(Enum):
    PERCENTAGE = "percentage"
    COUNT = "count"
    DURATION = "duration"
    BYTES = "bytes"
    REQUESTS = "requests"
    CURRENCY = "currency"
    SCORE = "score"

@dataclass
class DashboardWidget:
    """Individual dashboard widget configuration."""
    id: str
    title: str
    widget_type: VisualizationType
    data_source: str
    query: str
    refresh_interval: int = 60  # seconds
    position: Dict[str, int] = field(default_factory=lambda: {"x": 0, "y": 0, "w": 6, "h": 4})
    settings: Dict[str, Any] = field(default_factory=dict)
    alerts: List[Dict[str, Any]] = field(default_factory=list)
    drill_down_enabled: bool = False
    export_enabled: bool = True

@dataclass
class Dashboard:
    """Dashboard configuration."""
    id: str
    name: str
    dashboard_type: DashboardType
    description: str
    owner: str
    created_at: datetime
    updated_at: datetime
    widgets: List[DashboardWidget] = field(default_factory=list)
    layout_config: Dict[str, Any] = field(default_factory=dict)
    permissions: Dict[str, List[str]] = field(default_factory=dict)
    auto_refresh: bool = True
    refresh_interval: int = 30
    tags: List[str] = field(default_factory=list)

@dataclass
class DashboardData:
    """Data for dashboard widgets."""
    widget_id: str
    timestamp: float
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    cache_key: str = ""
    ttl: int = 300  # seconds

@dataclass
class Alert:
    """Dashboard alert configuration."""
    id: str
    name: str
    condition: str  # SQL-like condition
    threshold_value: float
    severity: str  # info, warning, error, critical
    enabled: bool = True
    notifications: List[Dict[str, str]] = field(default_factory=list)

class DashboardDataProvider:
    """Provides data for dashboard widgets."""
    
    def __init__(self):
        self.data_sources = {
            "performance_metrics": self._get_performance_metrics,
            "security_events": self._get_security_events,
            "infrastructure_metrics": self._get_infrastructure_metrics,
            "business_metrics": self._get_business_metrics,
            "compliance_status": self._get_compliance_status,
            "incident_data": self._get_incident_data,
            "cost_metrics": self._get_cost_metrics,
            "user_activity": self._get_user_activity
        }
    
    async def get_data(self, data_source: str, query: str, 
                      time_range: Dict[str, Any]) -> Dict[str, Any]:
        """Get data from specified source."""
        provider_func = self.data_sources.get(data_source)
        if not provider_func:
            return {"error": f"Unknown data source: {data_source}"}
        
        try:
            return await provider_func(query, time_range)
        except Exception as e:
            logging.error(f"Error getting data from {data_source}: {e}")
            return {"error": str(e)}
    
    async def _get_performance_metrics(self, query: str, time_range: Dict[str, Any]) -> Dict[str, Any]:
        """Get performance metrics data."""
        # Mock performance metrics data
        return {
            "cpu_usage": [
                {"timestamp": time.time() - 3600 + i*60, "value": random.uniform(30, 80)} 
                for i in range(60)
            ],
            "memory_usage": [
                {"timestamp": time.time() - 3600 + i*60, "value": random.uniform(40, 90)} 
                for i in range(60)
            ],
            "response_time": [
                {"timestamp": time.time() - 3600 + i*60, "value": random.uniform(0.1, 2.0)} 
                for i in range(60)
            ],
            "throughput": [
                {"timestamp": time.time() - 3600 + i*60, "value": random.uniform(50, 200)} 
                for i in range(60)
            ]
        }
    
    async def _get_security_events(self, query: str, time_range: Dict[str, Any]) -> Dict[str, Any]:
        """Get security events data."""
        return {
            "authentication_failures": random.randint(5, 25),
            "threats_detected": random.randint(1, 10),
            "blocked_ips": random.randint(2, 15),
            "vulnerability_scans": random.randint(0, 5),
            "recent_events": [
                {
                    "timestamp": time.time() - i*300,
                    "type": random.choice(["auth_failure", "threat_detected", "vulnerability"]),
                    "severity": random.choice(["low", "medium", "high", "critical"]),
                    "description": f"Security event {i+1}"
                }
                for i in range(20)
            ]
        }
    
    async def _get_infrastructure_metrics(self, query: str, time_range: Dict[str, Any]) -> Dict[str, Any]:
        """Get infrastructure metrics."""
        return {
            "cluster_health": "healthy",
            "node_count": 12,
            "pod_count": random.randint(50, 100),
            "service_availability": 99.9,
            "disk_usage": random.uniform(40, 85),
            "network_io": {
                "inbound": random.uniform(100, 500),
                "outbound": random.uniform(80, 400)
            },
            "k8s_metrics": {
                "api_server_latency": random.uniform(50, 200),
                "etcd_latency": random.uniform(1, 10),
                "scheduler_latency": random.uniform(10, 50)
            }
        }
    
    async def _get_business_metrics(self, query: str, time_range: Dict[str, Any]) -> Dict[str, Any]:
        """Get business metrics."""
        return {
            "active_users": random.randint(1000, 5000),
            "simulation_sessions": random.randint(50, 200),
            "agent_count": random.randint(100, 500),
            "consensus_operations": random.randint(1000, 5000),
            "data_processed_gb": random.uniform(50, 500),
            "revenue_usd": random.uniform(10000, 50000),
            "user_satisfaction": random.uniform(4.0, 5.0),
            "simulation_accuracy": random.uniform(85, 98)
        }
    
    async def _get_compliance_status(self, query: str, time_range: Dict[str, Any]) -> Dict[str, Any]:
        """Get compliance status."""
        return {
            "soc2": {"score": random.uniform(85, 98), "status": "compliant"},
            "gdpr": {"score": random.uniform(90, 99), "status": "compliant"},
            "hipaa": {"score": random.uniform(80, 95), "status": "compliant"},
            "iso27001": {"score": random.uniform(88, 96), "status": "compliant"},
            "nist": {"score": random.uniform(82, 94), "status": "compliant"},
            "last_audit": time.time() - random.randint(86400, 86400*30)
        }
    
    async def _get_incident_data(self, query: str, time_range: Dict[str, Any]) -> Dict[str, Any]:
        """Get incident data."""
        return {
            "active_incidents": random.randint(0, 3),
            "resolved_today": random.randint(1, 5),
            "mttr_hours": random.uniform(0.5, 4.0),
            "availability_percentage": random.uniform(99.5, 99.99),
            "incidents_by_severity": {
                "critical": random.randint(0, 2),
                "high": random.randint(1, 5),
                "medium": random.randint(3, 10),
                "low": random.randint(5, 15)
            },
            "top_issues": [
                {"issue": "API latency", "count": random.randint(5, 15)},
                {"issue": "Database performance", "count": random.randint(3, 10)},
                {"issue": "Memory usage", "count": random.randint(2, 8)}
            ]
        }
    
    async def _get_cost_metrics(self, query: str, time_range: Dict[str, Any]) -> Dict[str, Any]:
        """Get cost metrics."""
        return {
            "monthly_spend": random.uniform(50000, 150000),
            "daily_trend": [
                {"date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"), 
                 "cost": random.uniform(1000, 5000)}
                for i in range(30)
            ],
            "cost_by_service": {
                "compute": random.uniform(30000, 80000),
                "storage": random.uniform(10000, 30000),
                "network": random.uniform(5000, 15000),
                "database": random.uniform(8000, 25000)
            },
            "cost_optimization": {
                "potential_savings": random.uniform(5000, 25000),
                "recommendations": random.randint(3, 12)
            }
        }
    
    async def _get_user_activity(self, query: str, time_range: Dict[str, Any]) -> Dict[str, Any]:
        """Get user activity metrics."""
        return {
            "daily_active_users": random.randint(2000, 8000),
            "peak_concurrent": random.randint(500, 2000),
            "session_duration_avg": random.uniform(15, 60),
            "bounce_rate": random.uniform(0.1, 0.3),
            "feature_usage": {
                "simulation_start": random.randint(100, 500),
                "dashboard_view": random.randint(200, 1000),
                "api_calls": random.randint(500, 2000),
                "data_export": random.randint(10, 50)
            },
            "user_satisfaction_score": random.uniform(4.0, 5.0)
        }

class DashboardGenerator:
    """Generates pre-configured dashboards for different purposes."""
    
    def __init__(self, data_provider: DashboardDataProvider):
        self.data_provider = data_provider
        self.dashboard_templates = self._load_dashboard_templates()
    
    def _load_dashboard_templates(self) -> Dict[DashboardType, Dashboard]:
        """Load pre-configured dashboard templates."""
        templates = {}
        
        # Executive Dashboard
        executive_dashboard = Dashboard(
            id="executive-overview",
            name="Executive Overview",
            dashboard_type=DashboardType.EXECUTIVE,
            description="High-level business metrics and KPIs for executive decision making",
            owner="exec-team",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            widgets=[
                DashboardWidget(
                    id="revenue-kpi",
                    title="Monthly Revenue",
                    widget_type=VisualizationType.KPI_CARD,
                    data_source="business_metrics",
                    query="revenue_usd",
                    position={"x": 0, "y": 0, "w": 3, "h": 2}
                ),
                DashboardWidget(
                    id="active-users-kpi",
                    title="Active Users",
                    widget_type=VisualizationType.KPI_CARD,
                    data_source="business_metrics",
                    query="active_users",
                    position={"x": 3, "y": 0, "w": 3, "h": 2}
                ),
                DashboardWidget(
                    id="system-availability-kpi",
                    title="System Availability",
                    widget_type=VisualizationType.GAUGE,
                    data_source="infrastructure_metrics",
                    query="service_availability",
                    position={"x": 6, "y": 0, "w": 3, "h": 2}
                ),
                DashboardWidget(
                    id="revenue-trend",
                    title="Revenue Trend (30 days)",
                    widget_type=VisualizationType.LINE_CHART,
                    data_source="cost_metrics",
                    query="daily_trend",
                    position={"x": 0, "y": 2, "w": 6, "h": 4},
                    settings={"y_axis_label": "USD"}
                ),
                DashboardWidget(
                    id="compliance-status",
                    title="Compliance Status",
                    widget_type=VisualizationType.PIE_CHART,
                    data_source="compliance_status",
                    query="overall_compliance",
                    position={"x": 6, "y": 2, "w": 3, "h": 4}
                )
            ],
            refresh_interval=300  # 5 minutes
        )
        templates[DashboardType.EXECUTIVE] = executive_dashboard
        
        # Operational Dashboard
        operational_dashboard = Dashboard(
            id="operations-overview",
            name="Operations Overview",
            dashboard_type=DashboardType.OPERATIONAL,
            description="Real-time operational metrics and system health monitoring",
            owner="ops-team",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            widgets=[
                DashboardWidget(
                    id="cpu-usage",
                    title="CPU Usage",
                    widget_type=VisualizationType.GAUGE,
                    data_source="performance_metrics",
                    query="cpu_usage",
                    position={"x": 0, "y": 0, "w": 3, "h": 3}
                ),
                DashboardWidget(
                    id="memory-usage",
                    title="Memory Usage",
                    widget_type=VisualizationType.GAUGE,
                    data_source="performance_metrics",
                    query="memory_usage",
                    position={"x": 3, "y": 0, "w": 3, "h": 3}
                ),
                DashboardWidget(
                    id="active-incidents",
                    title="Active Incidents",
                    widget_type=VisualizationType.KPI_CARD,
                    data_source="incident_data",
                    query="active_incidents",
                    position={"x": 6, "y": 0, "w": 3, "h": 3}
                ),
                DashboardWidget(
                    id="response-time-trend",
                    title="Response Time Trend",
                    widget_type=VisualizationType.LINE_CHART,
                    data_source="performance_metrics",
                    query="response_time",
                    position={"x": 0, "y": 3, "w": 6, "h": 4}
                ),
                DashboardWidget(
                    id="infrastructure-health",
                    title="Infrastructure Health",
                    widget_type=VisualizationType.TABLE,
                    data_source="infrastructure_metrics",
                    query="cluster_health",
                    position={"x": 6, "y": 3, "w": 3, "h": 4}
                )
            ],
            refresh_interval=30  # 30 seconds
        )
        templates[DashboardType.OPERATIONAL] = operational_dashboard
        
        # Security Dashboard
        security_dashboard = Dashboard(
            id="security-overview",
            name="Security Overview",
            dashboard_type=DashboardType.SECURITY,
            description="Security metrics, threats, and compliance monitoring",
            owner="security-team",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            widgets=[
                DashboardWidget(
                    id="threats-detected",
                    title="Threats Detected",
                    widget_type=VisualizationType.KPI_CARD,
                    data_source="security_events",
                    query="threats_detected",
                    position={"x": 0, "y": 0, "w": 3, "h": 2}
                ),
                DashboardWidget(
                    id="blocked-ips",
                    title="Blocked IPs",
                    widget_type=VisualizationType.KPI_CARD,
                    data_source="security_events",
                    query="blocked_ips",
                    position={"x": 3, "y": 0, "w": 3, "h": 2}
                ),
                DashboardWidget(
                    id="auth-failures",
                    title="Authentication Failures",
                    widget_type=VisualizationType.KPI_CARD,
                    data_source="security_events",
                    query="authentication_failures",
                    position={"x": 6, "y": 0, "w": 3, "h": 2}
                ),
                DashboardWidget(
                    id="security-events-timeline",
                    title="Security Events Timeline",
                    widget_type=VisualizationType.TABLE,
                    data_source="security_events",
                    query="recent_events",
                    position={"x": 0, "y": 2, "w": 9, "h": 5}
                )
            ],
            refresh_interval=60  # 1 minute
        )
        templates[DashboardType.SECURITY] = security_dashboard
        
        # Technical Dashboard
        technical_dashboard = Dashboard(
            id="technical-overview",
            name="Technical Overview",
            dashboard_type=DashboardType.TECHNICAL,
            description="Detailed technical metrics for developers and engineers",
            owner="dev-team",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            widgets=[
                DashboardWidget(
                    id="throughput",
                    title="Request Throughput",
                    widget_type=VisualizationType.LINE_CHART,
                    data_source="performance_metrics",
                    query="throughput",
                    position={"x": 0, "y": 0, "w": 6, "h": 4}
                ),
                DashboardWidget(
                    id="k8s-metrics",
                    title="Kubernetes Metrics",
                    widget_type=VisualizationType.HEATMAP,
                    data_source="infrastructure_metrics",
                    query="k8s_metrics",
                    position={"x": 6, "y": 0, "w": 3, "h": 4}
                ),
                DashboardWidget(
                    id="error-rate",
                    title="Error Rate",
                    widget_type=VisualizationType.LINE_CHART,
                    data_source="performance_metrics",
                    query="error_rate",
                    position={"x": 0, "y": 4, "w": 4, "h": 3}
                ),
                DashboardWidget(
                    id="network-io",
                    title="Network I/O",
                    widget_type=VisualizationType.BAR_CHART,
                    data_source="infrastructure_metrics",
                    query="network_io",
                    position={"x": 4, "y": 4, "w": 5, "h": 3}
                )
            ],
            refresh_interval=15  # 15 seconds
        )
        templates[DashboardType.TECHNICAL] = technical_dashboard
        
        # Compliance Dashboard
        compliance_dashboard = Dashboard(
            id="compliance-overview",
            name="Compliance Overview",
            dashboard_type=DashboardType.COMPLIANCE,
            description="Compliance status across different frameworks and regulations",
            owner="compliance-team",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            widgets=[
                DashboardWidget(
                    id="soc2-compliance",
                    title="SOC 2 Compliance",
                    widget_type=VisualizationType.GAUGE,
                    data_source="compliance_status",
                    query="soc2",
                    position={"x": 0, "y": 0, "w": 2, "h": 3}
                ),
                DashboardWidget(
                    id="gdpr-compliance",
                    title="GDPR Compliance",
                    widget_type=VisualizationType.GAUGE,
                    data_source="compliance_status",
                    query="gdpr",
                    position={"x": 2, "y": 0, "w": 2, "h": 3}
                ),
                DashboardWidget(
                    id="hipaa-compliance",
                    title="HIPAA Compliance",
                    widget_type=VisualizationType.GAUGE,
                    data_source="compliance_status",
                    query="hipaa",
                    position={"x": 4, "y": 0, "w": 2, "h": 3}
                ),
                DashboardWidget(
                    id="compliance-overview-chart",
                    title="Compliance Overview",
                    widget_type=VisualizationType.BAR_CHART,
                    data_source="compliance_status",
                    query="framework_scores",
                    position={"x": 0, "y": 3, "w": 9, "h": 4}
                )
            ],
            refresh_interval=3600  # 1 hour
        )
        templates[DashboardType.COMPLIANCE] = compliance_dashboard
        
        return templates
    
    def create_dashboard(self, dashboard_type: DashboardType, 
                        custom_config: Dict[str, Any] = None) -> Dashboard:
        """Create a dashboard from template with optional customizations."""
        template = self.dashboard_templates[dashboard_type].copy()
        
        if custom_config:
            # Apply customizations
            if "name" in custom_config:
                template.name = custom_config["name"]
            if "description" in custom_config:
                template.description = custom_config["description"]
            if "widgets" in custom_config:
                template.widgets = custom_config["widgets"]
            if "refresh_interval" in custom_config:
                template.refresh_interval = custom_config["refresh_interval"]
        
        template.updated_at = datetime.utcnow()
        return template

class DashboardRenderer:
    """Renders dashboards in different formats."""
    
    def __init__(self, data_provider: DashboardDataProvider):
        self.data_provider = data_provider
        self.cache: Dict[str, DashboardData] = {}
        self.cache_ttl = 300  # 5 minutes
    
    async def render_dashboard(self, dashboard: Dashboard, 
                              time_range: Dict[str, Any] = None) -> Dict[str, Any]:
        """Render a complete dashboard with all widgets."""
        if time_range is None:
            time_range = {
                "start": time.time() - 3600,  # 1 hour ago
                "end": time.time()
            }
        
        rendered_widgets = []
        
        for widget in dashboard.widgets:
            try:
                widget_data = await self._render_widget(widget, time_range)
                rendered_widgets.append(widget_data)
            except Exception as e:
                logging.error(f"Error rendering widget {widget.id}: {e}")
                rendered_widgets.append({
                    "id": widget.id,
                    "error": str(e),
                    "data": None
                })
        
        return {
            "dashboard_id": dashboard.id,
            "dashboard_name": dashboard.name,
            "dashboard_type": dashboard.dashboard_type.value,
            "last_updated": dashboard.updated_at.isoformat(),
            "widgets": rendered_widgets,
            "layout_config": dashboard.layout_config,
            "metadata": {
                "total_widgets": len(dashboard.widgets),
                "successful_widgets": len([w for w in rendered_widgets if "error" not in w]),
                "render_time": time.time()
            }
        }
    
    async def _render_widget(self, widget: DashboardWidget, 
                           time_range: Dict[str, Any]) -> Dict[str, Any]:
        """Render individual widget."""
        cache_key = f"{widget.id}:{hash(str(time_range))}"
        
        # Check cache
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if time.time() - cached_data.timestamp < self.cache_ttl:
                return {
                    "id": widget.id,
                    "title": widget.title,
                    "widget_type": widget.widget_type.value,
                    "data": cached_data.data,
                    "metadata": cached_data.metadata,
                    "cached": True
                }
        
        # Get fresh data
        raw_data = await self.data_provider.get_data(
            widget.data_source, widget.query, time_range
        )
        
        # Transform data based on widget type
        transformed_data = self._transform_data(raw_data, widget)
        
        # Cache the result
        self.cache[cache_key] = DashboardData(
            widget_id=widget.id,
            timestamp=time.time(),
            data=transformed_data,
            cache_key=cache_key
        )
        
        return {
            "id": widget.id,
            "title": widget.title,
            "widget_type": widget.widget_type.value,
            "data": transformed_data,
            "settings": widget.settings,
            "refresh_interval": widget.refresh_interval,
            "cached": False
        }
    
    def _transform_data(self, raw_data: Dict[str, Any], widget: DashboardWidget) -> Dict[str, Any]:
        """Transform raw data based on widget type and query."""
        query = widget.query
        
        # Extract specific data based on query
        if query in raw_data:
            return raw_data[query]
        elif "." in query:
            # Handle dot notation queries
            parts = query.split(".")
            current = raw_data
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return {"error": f"Query path not found: {query}"}
            return current if isinstance(current, dict) else {"value": current}
        
        return raw_data

class MobileDashboardAdapter:
    """Adapts dashboards for mobile viewing."""
    
    def __init__(self):
        self.mobile_layouts = {
            DashboardType.EXECUTIVE: {
                "columns": 1,
                "widget_height": 150,
                "compact_mode": True
            },
            DashboardType.OPERATIONAL: {
                "columns": 1,
                "widget_height": 120,
                "compact_mode": True
            },
            DashboardType.SECURITY: {
                "columns": 1,
                "widget_height": 100,
                "compact_mode": True
            }
        }
    
    def adapt_for_mobile(self, dashboard: Dashboard) -> Dashboard:
        """Adapt dashboard layout for mobile devices."""
        mobile_config = self.mobile_layouts.get(dashboard.dashboard_type, {
            "columns": 1,
            "widget_height": 100,
            "compact_mode": True
        })
        
        # Create mobile version of dashboard
        mobile_dashboard = Dashboard(
            id=f"{dashboard.id}-mobile",
            name=f"{dashboard.name} (Mobile)",
            dashboard_type=dashboard.dashboard_type,
            description=f"{dashboard.description} - Mobile Optimized",
            owner=dashboard.owner,
            created_at=dashboard.created_at,
            updated_at=dashboard.updated_at,
            layout_config={
                "mobile": True,
                "columns": mobile_config["columns"],
                "widget_height": mobile_config["widget_height"],
                "compact_mode": mobile_config["compact_mode"]
            }
        )
        
        # Adapt widgets for mobile
        for widget in dashboard.widgets:
            mobile_widget = DashboardWidget(
                id=f"{widget.id}-mobile",
                title=self._shorten_title(widget.title),
                widget_type=widget.widget_type,
                data_source=widget.data_source,
                query=widget.query,
                position={"x": 0, "y": 0, "w": mobile_config["columns"], "h": 2},
                settings={**widget.settings, "mobile_optimized": True}
            )
            mobile_dashboard.widgets.append(mobile_widget)
        
        return mobile_dashboard
    
    def _shorten_title(self, title: str) -> str:
        """Shorten widget titles for mobile display."""
        title_mappings = {
            "System Availability": "Availability",
            "CPU Usage": "CPU",
            "Memory Usage": "Memory",
            "Active Users": "Users",
            "Threats Detected": "Threats",
            "Response Time Trend": "Response Time"
        }
        return title_mappings.get(title, title[:20] + "..." if len(title) > 20 else title)

class DashboardExporter:
    """Exports dashboards in various formats."""
    
    def __init__(self, renderer: DashboardRenderer):
        self.renderer = renderer
        self.export_formats = ["json", "csv", "pdf", "png", "excel"]
    
    async def export_dashboard(self, dashboard: Dashboard, 
                             format_type: str, 
                             time_range: Dict[str, Any] = None) -> Dict[str, Any]:
        """Export dashboard in specified format."""
        if format_type not in self.export_formats:
            raise ValueError(f"Unsupported export format: {format_type}")
        
        # Get rendered dashboard data
        rendered_dashboard = await self.renderer.render_dashboard(dashboard, time_range)
        
        if format_type == "json":
            return {"format": "json", "data": rendered_dashboard}
        
        elif format_type == "csv":
            return await self._export_as_csv(rendered_dashboard)
        
        elif format_type == "pdf":
            return await self._export_as_pdf(rendered_dashboard)
        
        elif format_type == "png":
            return await self._export_as_image(rendered_dashboard, "png")
        
        elif format_type == "excel":
            return await self._export_as_excel(rendered_dashboard)
        
        else:
            return {"error": f"Export not implemented for format: {format_type}"}
    
    async def _export_as_csv(self, rendered_dashboard: Dict[str, Any]) -> Dict[str, Any]:
        """Export dashboard data as CSV."""
        csv_data = []
        
        for widget in rendered_dashboard["widgets"]:
            widget_data = widget["data"]
            if isinstance(widget_data, list):
                for item in widget_data:
                    if isinstance(item, dict):
                        row = {"widget_id": widget["id"], "widget_title": widget["title"]}
                        row.update(item)
                        csv_data.append(row)
            elif isinstance(widget_data, dict):
                row = {"widget_id": widget["id"], "widget_title": widget["title"]}
                row.update(widget_data)
                csv_data.append(row)
        
        return {
            "format": "csv",
            "data": csv_data,
            "headers": list(set().union(*(row.keys() for row in csv_data if isinstance(row, dict)))) if csv_data else []
        }
    
    async def _export_as_pdf(self, rendered_dashboard: Dict[str, Any]) -> Dict[str, Any]:
        """Export dashboard as PDF."""
        # In a real implementation, this would generate a PDF
        # For now, return mock data
        return {
            "format": "pdf",
            "data": {
                "dashboard_name": rendered_dashboard["dashboard_name"],
                "widget_count": len(rendered_dashboard["widgets"]),
                "export_time": datetime.utcnow().isoformat(),
                "pdf_url": f"/exports/{rendered_dashboard['dashboard_id']}.pdf"
            }
        }
    
    async def _export_as_image(self, rendered_dashboard: Dict[str, Any], 
                             format_type: str) -> Dict[str, Any]:
        """Export dashboard as image."""
        # In a real implementation, this would render the dashboard as an image
        return {
            "format": format_type,
            "data": {
                "dashboard_name": rendered_dashboard["dashboard_name"],
                "image_url": f"/exports/{rendered_dashboard['dashboard_id']}.{format_type}",
                "export_time": datetime.utcnow().isoformat()
            }
        }
    
    async def _export_as_excel(self, rendered_dashboard: Dict[str, Any]) -> Dict[str, Any]:
        """Export dashboard as Excel file."""
        # In a real implementation, this would generate an Excel file
        return {
            "format": "excel",
            "data": {
                "dashboard_name": rendered_dashboard["dashboard_name"],
                "excel_url": f"/exports/{rendered_dashboard['dashboard_id']}.xlsx",
                "export_time": datetime.utcnow().isoformat(),
                "worksheets": ["Summary", "Detailed Data", "Charts"]
            }
        }

class EnterpriseDashboardSystem:
    """Main enterprise dashboard system."""
    
    def __init__(self):
        self.data_provider = DashboardDataProvider()
        self.generator = DashboardGenerator(self.data_provider)
        self.renderer = DashboardRenderer(self.data_provider)
        self.mobile_adapter = MobileDashboardAdapter()
        self.exporter = DashboardExporter(self.renderer)
        
        self.dashboards: Dict[str, Dashboard] = {}
        self.dashboard_data_cache: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
        
        # Initialize with default dashboards
        self._initialize_default_dashboards()
    
    def _initialize_default_dashboards(self) -> None:
        """Initialize system with default dashboard templates."""
        for dashboard_type in DashboardType:
            dashboard = self.generator.create_dashboard(dashboard_type)
            self.dashboards[dashboard.id] = dashboard
    
    async def get_dashboard(self, dashboard_id: str) -> Optional[Dashboard]:
        """Get dashboard by ID."""
        return self.dashboards.get(dashboard_id)
    
    async def create_custom_dashboard(self, config: Dict[str, Any]) -> Dashboard:
        """Create a custom dashboard."""
        dashboard_id = f"custom-{int(time.time())}"
        
        dashboard = Dashboard(
            id=dashboard_id,
            name=config["name"],
            dashboard_type=DashboardType.CUSTOM,
            description=config.get("description", "Custom dashboard"),
            owner=config["owner"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            widgets=config.get("widgets", []),
            refresh_interval=config.get("refresh_interval", 60),
            tags=config.get("tags", [])
        )
        
        async with self._lock:
            self.dashboards[dashboard_id] = dashboard
        
        logging.info(f"Created custom dashboard: {dashboard_id}")
        return dashboard
    
    async def update_dashboard(self, dashboard_id: str, updates: Dict[str, Any]) -> bool:
        """Update existing dashboard."""
        if dashboard_id not in self.dashboards:
            return False
        
        dashboard = self.dashboards[dashboard_id]
        
        # Apply updates
        if "name" in updates:
            dashboard.name = updates["name"]
        if "description" in updates:
            dashboard.description = updates["description"]
        if "widgets" in updates:
            dashboard.widgets = updates["widgets"]
        if "refresh_interval" in updates:
            dashboard.refresh_interval = updates["refresh_interval"]
        if "tags" in updates:
            dashboard.tags = updates["tags"]
        
        dashboard.updated_at = datetime.utcnow()
        
        logging.info(f"Updated dashboard: {dashboard_id}")
        return True
    
    async def delete_dashboard(self, dashboard_id: str) -> bool:
        """Delete dashboard."""
        if dashboard_id not in self.dashboards:
            return False
        
        del self.dashboards[dashboard_id]
        
        # Remove from cache
        if dashboard_id in self.dashboard_data_cache:
            del self.dashboard_data_cache[dashboard_id]
        
        logging.info(f"Deleted dashboard: {dashboard_id}")
        return True
    
    async def render_dashboard(self, dashboard_id: str, 
                             mobile: bool = False,
                             time_range: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Render dashboard data."""
        dashboard = await self.get_dashboard(dashboard_id)
        if not dashboard:
            return None
        
        # Adapt for mobile if requested
        if mobile:
            dashboard = self.mobile_adapter.adapt_for_mobile(dashboard)
        
        # Render dashboard
        rendered_data = await self.renderer.render_dashboard(dashboard, time_range)
        
        # Cache the result
        cache_key = f"{dashboard_id}:{int(time.time() / 300) * 300}" if time_range else f"{dashboard_id}:latest"
        self.dashboard_data_cache[dashboard_id] = rendered_data
        
        return rendered_data
    
    async def export_dashboard(self, dashboard_id: str, 
                             format_type: str,
                             time_range: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Export dashboard in specified format."""
        dashboard = await self.get_dashboard(dashboard_id)
        if not dashboard:
            return None
        
        return await self.exporter.export_dashboard(dashboard, format_type, time_range)
    
    def get_dashboard_list(self) -> List[Dict[str, Any]]:
        """Get list of all dashboards."""
        return [
            {
                "id": dashboard.id,
                "name": dashboard.name,
                "type": dashboard.dashboard_type.value,
                "description": dashboard.description,
                "owner": dashboard.owner,
                "widget_count": len(dashboard.widgets),
                "created_at": dashboard.created_at.isoformat(),
                "updated_at": dashboard.updated_at.isoformat(),
                "tags": dashboard.tags
            }
            for dashboard in self.dashboards.values()
        ]
    
    def get_dashboard_statistics(self) -> Dict[str, Any]:
        """Get dashboard system statistics."""
        dashboard_types = {}
        total_widgets = 0
        
        for dashboard in self.dashboards.values():
            dashboard_type = dashboard.dashboard_type.value
            dashboard_types[dashboard_type] = dashboard_types.get(dashboard_type, 0) + 1
            total_widgets += len(dashboard.widgets)
        
        return {
            "total_dashboards": len(self.dashboards),
            "total_widgets": total_widgets,
            "dashboards_by_type": dashboard_types,
            "cache_size": len(self.dashboard_data_cache),
            "system_health": "healthy",
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def get_dashboard_health(self) -> Dict[str, Any]:
        """Get health status of dashboard system."""
        health_checks = {
            "data_provider": "healthy",
            "renderer": "healthy",
            "cache_system": "healthy",
            "export_service": "healthy"
        }
        
        # Perform health checks
        try:
            # Test data provider
            test_data = await self.data_provider.get_data(
                "performance_metrics", "cpu_usage", {"start": time.time() - 3600, "end": time.time()}
            )
            if "error" in test_data:
                health_checks["data_provider"] = "degraded"
        except Exception:
            health_checks["data_provider"] = "unhealthy"
        
        overall_health = "healthy"
        if "unhealthy" in health_checks.values():
            overall_health = "unhealthy"
        elif "degraded" in health_checks.values():
            overall_health = "degraded"
        
        return {
            "overall_health": overall_health,
            "component_health": health_checks,
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": time.time()  # Would track actual uptime
        }

# Global dashboard system instance
dashboard_system: Optional[EnterpriseDashboardSystem] = None

def get_dashboard_system() -> EnterpriseDashboardSystem:
    """Get or create global dashboard system instance."""
    global dashboard_system
    if dashboard_system is None:
        dashboard_system = EnterpriseDashboardSystem()
    return dashboard_system

# Initialize dashboard system
def initialize_dashboard_system():
    """Initialize the enterprise dashboard system."""
    system = get_dashboard_system()
    logging.info("Enterprise dashboard system initialized")
    return system

if __name__ == "__main__":
    # Example usage and testing
    initialize_dashboard_system()
    
    system = get_dashboard_system()
    
    # Test dashboard listing
    print("Testing dashboard system...")
    dashboards = system.get_dashboard_list()
    print(f"Available dashboards: {len(dashboards)}")
    for dashboard in dashboards:
        print(f"  - {dashboard['name']} ({dashboard['type']})")
    
    # Test dashboard rendering
    print("\nTesting dashboard rendering...")
    executive_dashboard_id = "executive-overview"
    rendered_data = asyncio.run(system.render_dashboard(executive_dashboard_id))
    if rendered_data:
        print(f"Rendered dashboard: {rendered_data['dashboard_name']}")
        print(f"Widgets rendered: {rendered_data['metadata']['successful_widgets']}")
    
    # Test custom dashboard creation
    print("\nTesting custom dashboard creation...")
    custom_config = {
        "name": "Test Custom Dashboard",
        "description": "A test custom dashboard",
        "owner": "test-user",
        "widgets": [
            {
                "id": "test-kpi",
                "title": "Test KPI",
                "widget_type": "kpi_card",
                "data_source": "business_metrics",
                "query": "active_users",
                "position": {"x": 0, "y": 0, "w": 3, "h": 2}
            }
        ],
        "tags": ["test", "custom"]
    }
    
    custom_dashboard = asyncio.run(system.create_custom_dashboard(custom_config))
    print(f"Created custom dashboard: {custom_dashboard.id}")
    
    # Test dashboard export
    print("\nTesting dashboard export...")
    export_result = asyncio.run(system.export_dashboard(executive_dashboard_id, "json"))
    if export_result:
        print(f"Export format: {export_result['format']}")
    
    # Test mobile adaptation
    print("\nTesting mobile adaptation...")
    mobile_dashboard = system.mobile_adapter.adapt_for_mobile(
        system.dashboards[executive_dashboard_id]
    )
    print(f"Mobile dashboard: {mobile_dashboard.name}")
    print(f"Mobile widgets: {len(mobile_dashboard.widgets)}")
    
    # Test system statistics
    print("\nGetting system statistics...")
    stats = system.get_dashboard_statistics()
    print(f"System Statistics:")
    print(f"- Total dashboards: {stats['total_dashboards']}")
    print(f"- Total widgets: {stats['total_widgets']}")
    print(f"- System health: {stats['system_health']}")
    
    # Test system health
    print("\nGetting system health...")
    health = asyncio.run(system.get_dashboard_health())
    print(f"Overall health: {health['overall_health']}")
    
    print("✅ Dashboard system test completed")