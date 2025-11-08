#!/usr/bin/env python3
"""
Simple FastAPI server for decentralized AI simulation platform
Bypasses complex dependencies for startup testing
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# Basic imports that should be available
import sys
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError as e:
    logger.warning(f"FastAPI dependencies not available: {e}")
    FASTAPI_AVAILABLE = False

# Mock data for testing
MOCK_AGENTS = [
    {
        "id": f"agent_{i}",
        "name": f"Agent {i}",
        "agent_type": "anomaly_detector",
        "status": "active" if i % 3 == 0 else "inactive",
        "capabilities": ["detection", "validation"],
        "created_at": datetime.now().isoformat(),
        "last_seen": datetime.now().isoformat(),
        "performance_metrics": {"accuracy": 0.95, "throughput": 100}
    }
    for i in range(1, 11)
]

MOCK_SIMULATIONS = [
    {
        "id": f"sim_{i}",
        "name": f"Simulation {i}",
        "status": "running" if i % 2 == 0 else "completed",
        "progress": 0.75 if i % 2 == 0 else 1.0,
        "created_at": datetime.now().isoformat(),
        "results": {"anomalies_detected": 15, "agents_active": 20}
    }
    for i in range(1, 6)
]

if FASTAPI_AVAILABLE:
    # Create FastAPI app
    app = FastAPI(
        title="Decentralized AI Simulation Platform",
        description="Simplified API for testing startup",
        version="1.0.0"
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    async def root():
        return {"message": "Decentralized AI Simulation Platform API", "status": "running"}

    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "services": {
                "api": "running",
                "database": "connected",
                "agents": len(MOCK_AGENTS)
            }
        }

    @app.get("/agents")
    async def list_agents():
        return {
            "success": True,
            "data": MOCK_AGENTS,
            "total": len(MOCK_AGENTS),
            "timestamp": datetime.now().isoformat()
        }

    @app.get("/agents/{agent_id}")
    async def get_agent(agent_id: str):
        for agent in MOCK_AGENTS:
            if agent["id"] == agent_id:
                return {
                    "success": True,
                    "data": agent,
                    "timestamp": datetime.now().isoformat()
                }
        
        raise HTTPException(status_code=404, detail="Agent not found")

    @app.get("/simulations")
    async def list_simulations():
        return {
            "success": True,
            "data": MOCK_SIMULATIONS,
            "total": len(MOCK_SIMULATIONS),
            "timestamp": datetime.now().isoformat()
        }

    @app.get("/simulations/{simulation_id}")
    async def get_simulation(simulation_id: str):
        for sim in MOCK_SIMULATIONS:
            if sim["id"] == simulation_id:
                return {
                    "success": True,
                    "data": sim,
                    "timestamp": datetime.now().isoformat()
                }
        
        raise HTTPException(status_code=404, detail="Simulation not found")

    @app.get("/system/info")
    async def system_info():
        return {
            "system": "Decentralized AI Simulation Platform",
            "version": "1.0.0",
            "status": "operational",
            "components": {
                "agents": {"total": len(MOCK_AGENTS), "active": len([a for a in MOCK_AGENTS if a["status"] == "active"])},
                "simulations": {"total": len(MOCK_SIMULATIONS), "running": len([s for s in MOCK_SIMULATIONS if s["status"] == "running"])}
            },
            "performance": {
                "uptime": "00:15:30",
                "response_time_ms": 45,
                "throughput_rps": 1250
            }
        }

    def start_server():
        """Start the FastAPI server"""
        logger.info("Starting Decentralized AI Simulation Platform API...")
        logger.info("API Documentation: http://localhost:8000/docs")
        logger.info("API ReDoc: http://localhost:8000/redoc")
        
        try:
            uvicorn.run(
                app, 
                host="0.0.0.0", 
                port=8000,
                log_level="info",
                access_log=True
            )
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            return False
        
        return True

else:
    # Fallback: Simple HTTP server using built-in modules
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import json
    import urllib.parse

    class SimpleHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            path = urllib.parse.urlparse(self.path).path
            
            # Set CORS headers
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            # Handle different endpoints
            if path == '/' or path == '/health':
                response = {
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "version": "1.0.0",
                    "message": "Decentralized AI Simulation Platform API"
                }
            elif path == '/agents':
                response = {
                    "success": True,
                    "data": MOCK_AGENTS,
                    "total": len(MOCK_AGENTS)
                }
            elif path == '/simulations':
                response = {
                    "success": True,
                    "data": MOCK_SIMULATIONS,
                    "total": len(MOCK_SIMULATIONS)
                }
            elif path == '/system/info':
                response = {
                    "system": "Decentralized AI Simulation Platform",
                    "version": "1.0.0",
                    "status": "operational"
                }
            else:
                response = {"error": "Not found"}
            
            # Send response
            self.wfile.write(json.dumps(response).encode())

        def log_message(self, format, *args):
            logger.info(f"{self.address_string()} - {format % args}")

    def start_server():
        """Start the simple HTTP server"""
        logger.info("Starting Simple HTTP API Server...")
        logger.info("Server will be available at http://localhost:8000")
        
        try:
            server = HTTPServer(('0.0.0.0', 8000), SimpleHandler)
            logger.info("Server started successfully on port 8000")
            server.serve_forever()
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            return False
        
        return True

if __name__ == "__main__":
    logger.info("Starting Decentralized AI Simulation Platform...")
    logger.info(f"FastAPI Available: {FASTAPI_AVAILABLE}")
    
    start_server()