# Streamlit UI Dockerfile for 3D AI Simulation Platform

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY decentralized-ai-simulation/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy additional requirements for 3D API server
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY decentralized-ai-simulation/ ./decentralized-ai-simulation/
COPY backend/ ./backend/

# Create data directory
RUN mkdir -p /data

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app /data
USER app

# Set Python path
ENV PYTHONPATH=/app

# Expose ports
EXPOSE 8501 8502 8503

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8502/health || exit 1

# Copy startup script
COPY docker/streamlit/start.sh /start.sh
RUN chmod +x /start.sh

# Start command
CMD ["/start.sh"]