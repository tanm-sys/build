import streamlit as st
import plotly.graph_objects as go
import networkx as nx
import pandas as pd
import threading
from src.core.simulation import Simulation
from src.core.database import DatabaseLedger
import ray
from src.utils.monitoring import get_monitoring

# Page config
st.set_page_config(page_title="Decentralized AI Simulation", layout="wide")

# Sidebar for parameters
st.sidebar.header("Simulation Parameters")
num_agents = st.sidebar.slider("Number of Agents", 10, 200, 50)
anomaly_rate = st.sidebar.slider("Anomaly Rate", 0.0, 0.1, 0.05)  # Note: Integrate into Simulation if needed
steps = st.sidebar.slider("Number of Steps", 10, 100, 50)

# Auto-enable Ray for scalability
use_ray = num_agents > 50

# Initialize session state
if 'sim' not in st.session_state:
    st.session_state.sim = None
if 'ledger' not in st.session_state:
    st.session_state.ledger = DatabaseLedger()
if 'running' not in st.session_state:
    st.session_state.running = False
if 'thread' not in st.session_state:
    st.session_state.thread = None
if 'stop_event' not in st.session_state:
    st.session_state.stop_event = threading.Event()
if 'monitoring' not in st.session_state:
    st.session_state.monitoring = get_monitoring()

# Control buttons
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("Initialize Simulation"):
        if st.session_state.sim is not None:
            st.session_state.sim.__del__()  # Cleanup previous
        if use_ray:
            ray.init(ignore_reinit_error=True)
        st.session_state.sim = Simulation(num_agents=num_agents)
        st.session_state.sim.use_parallel = use_ray
        st.rerun()
with col2:
    if st.button("Start Simulation") and st.session_state.sim is not None:
        if not st.session_state.running:
            st.session_state.stop_event.clear()
            # Capture the sim object locally for thread safety
            sim_instance = st.session_state.sim
            st.session_state.thread = threading.Thread(
                target=lambda: sim_instance.run(steps=steps),
                daemon=True
            )
            st.session_state.thread.start()
            st.session_state.running = True
            st.rerun()
with col3:
    if st.button("Stop Simulation"):
        st.session_state.stop_event.set()
        st.session_state.running = False
        if st.session_state.thread:
            st.session_state.thread.join(timeout=1)
        st.rerun()
with col4:
    if st.button("Refresh Health Checks"):
        st.rerun()

# Main dashboard
st.title("Decentralized AI Simulation Dashboard")

if st.session_state.sim is None:
    st.info("Initialize the simulation to begin.")
elif not st.session_state.running:
    st.info("Simulation initialized. Click Start to run.")
else:
    st.success(f"Simulation running... ({use_ray and 'Using Ray' or 'Sequential'})")

# Cached DB query for anomaly logs
@st.cache_data(ttl=5)  # Refresh every 5s
def get_anomaly_logs():
    entries = st.session_state.ledger.read_ledger()
    if not entries:
        return pd.DataFrame()
    df = pd.DataFrame([
        {
            'ID': e['id'],
            'Timestamp': e['timestamp'],
            'Node ID': e['node_id'],
            'Features': str(e['features']),
            'Confidence': e['confidence']
        }
        for e in entries
    ])
    return df

# Display anomaly logs
st.subheader("Anomaly Logs")
logs_df = get_anomaly_logs()
if not logs_df.empty:
    st.dataframe(logs_df, width='stretch')
else:
    st.info("No anomalies logged yet.")

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