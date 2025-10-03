#!/bin/bash
# Startup script for Streamlit container with API server

set -e

echo "🚀 Starting 3D AI Simulation Platform..."

# Initialize simulation for API server
echo "📊 Initializing simulation for API server..."
python -c "
import sys, os
sys.path.append('/app')

from decentralized_ai_simulation.src.ui.api_server import initialize_api_simulation

print('Initializing simulation...')
success = initialize_api_simulation(100)
if success:
    print('✅ Simulation initialized successfully')
else:
    print('❌ Failed to initialize simulation')
    exit 1
"

# Start API server in background
echo "🌐 Starting API server on port 8502..."
python -c "
import sys, os
import threading
sys.path.append('/app')

from decentralized_ai_simulation.src.ui.api_server import start_api_server

print('Starting API server...')
server = start_api_server(8502)
print('✅ API server started')
" &

# Wait a moment for API server to start
sleep 3

# Start Streamlit
echo "📱 Starting Streamlit UI on port 8501..."
exec streamlit run decentralized-ai-simulation/src/ui/streamlit_app.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --server.headless true \
    --browser.gatherUsageStats false