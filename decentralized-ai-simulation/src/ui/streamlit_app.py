import streamlit as st
import plotly.graph_objects as go
import networkx as nx
import pandas as pd
import threading
from typing import Optional, Dict, Any, Tuple, List
from dataclasses import dataclass
from simulation import Simulation
from database import DatabaseLedger
import ray
from monitoring import get_monitoring
from config_loader import get_config
import time
import logging


@dataclass
class SimulationState:
    """Enhanced state management for the simulation."""
    simulation: Optional[Simulation] = None
    ledger: Optional[DatabaseLedger] = None
    running: bool = False
    thread: Optional[threading.Thread] = None
    stop_event: threading.Event = field(default_factory=threading.Event)
    monitoring = field(default_factory=get_monitoring)
    start_time: float = 0.0
    step_count: int = 0


@dataclass
class UIParameters:
    """UI parameter management with validation."""
    num_agents: int = 50
    anomaly_rate: float = 0.05
    steps: int = 50

    def __post_init__(self) -> None:
        """Validate parameters after initialization."""
        if not 10 <= self.num_agents <= 200:
            raise ValueError("Number of agents must be between 10 and 200")
        if not 0.0 <= self.anomaly_rate <= 0.1:
            raise ValueError("Anomaly rate must be between 0.0 and 0.1")
        if not 10 <= self.steps <= 100:
            raise ValueError("Steps must be between 10 and 100")


# Page config with enhanced settings
st.set_page_config(
    page_title=get_config('streamlit.page_title', 'Decentralized AI Simulation'),
    layout=get_config('streamlit.layout', 'wide'),
    initial_sidebar_state="expanded"
)

# Initialize logger
logger = logging.getLogger(__name__)

# Get UI parameters with validation and configuration integration
def get_ui_parameters() -> UIParameters:
    """Get UI parameters with validation and configuration integration."""
    st.sidebar.header("Simulation Parameters")

    # Get parameters from sliders with config-based defaults and ranges
    num_agents = st.sidebar.slider(
        "Number of Agents",
        get_config('streamlit.agent_slider_min', 10),
        get_config('streamlit.agent_slider_max', 200),
        get_config('streamlit.agent_slider_default', 50)
    )

    anomaly_rate = st.sidebar.slider(
        "Anomaly Rate",
        get_config('streamlit.anomaly_slider_min', 0.0),
        get_config('streamlit.anomaly_slider_max', 0.1),
        get_config('streamlit.anomaly_slider_default', 0.05)
    )

    steps = st.sidebar.slider(
        "Number of Steps",
        get_config('streamlit.steps_slider_min', 10),
        get_config('streamlit.steps_slider_max', 100),
        get_config('streamlit.steps_slider_default', 50)
    )

    try:
        return UIParameters(
            num_agents=num_agents,
            anomaly_rate=anomaly_rate,
            steps=steps
        )
    except ValueError as e:
        st.error(f"Invalid parameters: {e}")
        # Return safe defaults
        return UIParameters()


# Get current parameters
params = get_ui_parameters()

# Initialize enhanced session state
def initialize_session_state() -> SimulationState:
    """Initialize enhanced session state with proper structure."""
    if 'app_state' not in st.session_state:
        st.session_state.app_state = SimulationState(
            ledger=DatabaseLedger(),
            start_time=time.time()
        )
    return st.session_state.app_state


# Initialize state
state = initialize_session_state()

# Render control buttons with enhanced functionality
def render_control_buttons(state: SimulationState, params: UIParameters) -> None:
    """Render control buttons with enhanced functionality."""
    st.sidebar.header("Simulation Control")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("Initialize Simulation", type="primary"):
            _initialize_simulation(state, params)

    with col2:
        if st.button("Start Simulation",
                    disabled=(state.simulation is None),
                    type="secondary"):
            _start_simulation(state, params)

    with col3:
        if st.button("Stop Simulation",
                    disabled=not state.running,
                    type="secondary"):
            _stop_simulation(state)

    with col4:
        if st.button("Refresh Health Checks"):
            st.rerun()


def _initialize_simulation(state: SimulationState, params: UIParameters) -> None:
    """Initialize simulation with enhanced error handling."""
    try:
        # Cleanup previous simulation
        if state.simulation is not None:
            state.simulation.cleanup()

        # Auto-enable parallel execution for scalability
        use_parallel = params.num_agents > get_config('simulation.use_parallel_threshold', 50)

        if use_parallel:
            ray.init(ignore_reinit_error=True)

        # Create new simulation
        state.simulation = Simulation(num_agents=params.num_agents)
        state.simulation.use_parallel = use_parallel

        st.success(f"Simulation initialized with {params.num_agents} agents")
        st.rerun()

    except Exception as e:
        logger.error(f"Failed to initialize simulation: {e}")
        st.error(f"Failed to initialize simulation: {e}")


def _start_simulation(state: SimulationState, params: UIParameters) -> None:
    """Start simulation with enhanced thread management."""
    if state.running:
        st.warning("Simulation is already running")
        return

    try:
        state.stop_event.clear()
        state.running = True

        # Create simulation thread with proper error handling
        state.thread = threading.Thread(
            target=_run_simulation_thread,
            args=(state, params),
            daemon=True
        )
        state.thread.start()

        st.success("Simulation started")
        st.rerun()

    except Exception as e:
        logger.error(f"Failed to start simulation: {e}")
        state.running = False
        st.error(f"Failed to start simulation: {e}")


def _stop_simulation(state: SimulationState) -> None:
    """Stop simulation with proper cleanup."""
    try:
        state.stop_event.set()
        state.running = False

        if state.thread and state.thread.is_alive():
            state.thread.join(timeout=1.0)

        st.info("Simulation stopped")
        st.rerun()

    except Exception as e:
        logger.error(f"Error stopping simulation: {e}")
        st.error(f"Error stopping simulation: {e}")


def _run_simulation_thread(state: SimulationState, params: UIParameters) -> None:
    """Run simulation in background thread with error handling."""
    try:
        if state.simulation:
            state.simulation.run(steps=params.steps)
    except Exception as e:
        logger.error(f"Simulation thread error: {e}")
        st.error(f"Simulation error: {e}")
    finally:
        state.running = False


# Render control buttons
render_control_buttons(state, params)

# Main dashboard with enhanced state management
def render_main_dashboard(state: SimulationState, params: UIParameters) -> None:
    """Render main dashboard with enhanced state management."""
    st.title("Decentralized AI Simulation Dashboard")

    if state.simulation is None:
        st.info("Initialize the simulation to begin.")
    elif not state.running:
        st.info("Simulation initialized. Click Start to run.")
    else:
        use_parallel = params.num_agents > get_config('simulation.use_parallel_threshold', 50)
        st.success(f"Simulation running... ({use_parallel and 'Using Parallel' or 'Sequential'})")


# Render main dashboard
render_main_dashboard(state, params)

# Enhanced anomaly logs with better caching and error handling
@st.cache_data(ttl=get_config('streamlit.cache_ttl', 5))
def get_anomaly_logs(ledger: DatabaseLedger) -> pd.DataFrame:
    """Get anomaly logs with enhanced error handling and validation."""
    try:
        entries = ledger.read_ledger()
        if not entries:
            return pd.DataFrame()

        # Validate and format entries
        formatted_entries = []
        for entry in entries:
            try:
                formatted_entry = {
                    'ID': int(entry.get('id', 0)),
                    'Timestamp': float(entry.get('timestamp', 0)),
                    'Node ID': str(entry.get('node_id', 'Unknown')),
                    'Features': str(entry.get('features', [])),
                    'Confidence': float(entry.get('confidence', 0.0))
                }
                formatted_entries.append(formatted_entry)
            except (ValueError, TypeError) as e:
                logger.warning(f"Skipping invalid entry: {e}")
                continue

        if not formatted_entries:
            return pd.DataFrame()

        return pd.DataFrame(formatted_entries)

    except Exception as e:
        logger.error(f"Error getting anomaly logs: {e}")
        st.error(f"Error loading anomaly logs: {e}")
        return pd.DataFrame()


def render_anomaly_logs(state: SimulationState) -> None:
    """Render anomaly logs section with enhanced functionality."""
    st.subheader("Anomaly Logs")

    if state.ledger is None:
        st.warning("Ledger not initialized")
        return

    logs_df = get_anomaly_logs(state.ledger)

    if not logs_df.empty:
        st.dataframe(logs_df, use_container_width=True)

        # Add summary statistics
        with st.expander("Anomaly Statistics"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Anomalies", len(logs_df))
            with col2:
                st.metric("Unique Nodes", logs_df['Node ID'].nunique())
            with col3:
                avg_confidence = logs_df['Confidence'].mean() if not logs_df.empty else 0
                st.metric("Avg Confidence", f"{avg_confidence:.3f}")
    else:
        st.info("No anomalies logged yet.")


# Render anomaly logs
render_anomaly_logs(state)

# Network visualization (simple random graph for demo; enhance with agent connections)
st.subheader("Agent Network Visualization")
if st.session_state.sim is not None:
    G = nx.erdos_renyi_graph(num_agents, 0.1)  # Random graph for visualization
    pos = nx.spring_layout(G)
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(x=edge_x, y=edge_y, line={'width': 0.5, 'color': '#888'}, hoverinfo='none', mode='lines')

    node_x, node_y = [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        marker={'showscale': True, 'colorscale': 'YlGnBu', 'size': 10, 'color': [G.degree[node] for node in G.nodes()], 'colorbar': {'thickness': 15}},
        text=list(G.nodes()), textposition="middle center"
    )

    fig = go.Figure(data=[edge_trace, node_trace], layout=go.Layout(showlegend=False, hovermode='closest', margin={'b': 20, 'l': 5, 'r': 5, 't': 40}))
    fig.update_layout(title="Agent Network (Degree-based coloring)", width=800, height=600)
    st.plotly_chart(fig, width='stretch')
else:
    st.info("Initialize simulation for network view.")

# Health checks and monitoring
st.subheader("System Health")
health_status = st.session_state.monitoring.get_system_health()
health_color = {
    'healthy': '🟢',
    'degraded': '🟡',
    'unhealthy': '🔴'
}.get(health_status.status, '⚪')

st.metric("Overall Status", f"{health_color} {health_status.status.upper()}", health_status.message)

# Detailed health checks
with st.expander("Detailed Health Checks"):
    all_checks = st.session_state.monitoring.perform_all_health_checks()
    for check_name, check_status in all_checks.items():
        status_color = {
            'healthy': '🟢',
            'degraded': '🟡',
            'unhealthy': '🔴'
        }.get(check_status.status, '⚪')
        st.write(f"{status_color} **{check_name}**: {check_status.message}")
        if check_status.details:
            st.json(check_status.details)

# System metrics
with st.expander("System Metrics"):
    uptime = st.session_state.monitoring.get_uptime()
    st.metric("Uptime", f"{uptime:.2f} seconds")
    
    # Record some simulation metrics if running
    if st.session_state.sim is not None and st.session_state.running:
        st.session_state.monitoring.record_metric('agent_count', len(st.session_state.sim.node_agents))
        st.session_state.monitoring.record_metric('steps_completed', steps)
    
    # Display metric statistics
    metrics = ['agent_count', 'steps_completed']
    for metric in metrics:
        stats = st.session_state.monitoring.get_metric_stats(metric)
        if stats:
            st.write(f"**{metric}**: {stats}")

# Status info
st.subheader("Simulation Status")
if st.session_state.sim is not None:
    agent_count = len(st.session_state.sim.node_agents)
    st.metric("Agents", agent_count)
    st.metric("Steps to Run", steps)
    st.metric("Using Parallel", use_ray)

# Cleanup on script end (Streamlit reruns, but handle Ray)
if st.session_state.sim is not None and not st.session_state.running:
    if use_ray and ray.is_initialized():
        ray.shutdown()