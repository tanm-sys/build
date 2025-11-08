# AI Simulation Python Environment Setup Guide

## Overview
This guide provides instructions for activating and using the Python virtual environment for the Decentralized AI Simulation Platform.

## Environment Details
- **Python Version**: 3.13.7
- **Virtual Environment Location**: `/home/tanmay/Music/build/venv_ai_simulation/`
- **Installation Date**: November 2, 2025
- **Total Dependencies**: 150+ packages installed

## Quick Activation

### Option 1: Direct Python Execution
For commands, use the full path to the virtual environment's Python:
```bash
# Navigate to project directory
cd /home/tanmay/Music/build

# Run Python scripts directly
./venv_ai_simulation/bin/python your_script.py

# Install new packages
./venv_ai_simulation/bin/pip install package_name

# Run with pip
./venv_ai_simulation/bin/pip -m your_module
```

### Option 2: Create Activation Script (Recommended)
Create a simple activation script for convenience:

```bash
# Create activation script
cat > activate_env.sh << 'EOF'
#!/bin/bash
cd /home/tanmay/Music/build
export PATH="./venv_ai_simulation/bin:$PATH"
echo "Virtual environment activated!"
echo "Python path: $(which python)"
python --version
EOF

# Make it executable
chmod +x activate_env.sh

# Use it
./activate_env.sh
```

## Key Packages Available

### Backend Framework
- **FastAPI 0.109.1**: Modern web framework for building APIs
- **Uvicorn 0.24.0**: ASGI server for FastAPI
- **WebSockets 12.0**: Real-time communication support
- **Pydantic 2.11.9**: Data validation and serialization

### AI/ML and Simulation
- **Mesa 3.3.0**: Agent-based modeling framework
- **Ray 2.45.0**: Distributed computing for AI workloads
- **NumPy 2.1.3**: Numerical computing
- **Pandas 2.2.3**: Data manipulation and analysis
- **Scikit-learn 1.7.2**: Machine learning algorithms

### Network and Visualization
- **NetworkX 3.5**: Network analysis and graph algorithms
- **Plotly 6.3.1**: Interactive data visualization
- **Streamlit 1.39.0**: Web application framework

### Testing and Development
- **pytest 8.4.2**: Testing framework
- **pytest-asyncio 0.21.1**: Async testing support
- **httpx 0.25.2**: HTTP client for testing

## Usage Examples

### Running FastAPI Backend
```bash
cd /home/tanmay/Music/build
./venv_ai_simulation/bin/python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Running Mesa Simulation
```bash
cd /home/tanmay/Music/build
./venv_ai_simulation/bin/python decentralized-ai-simulation/src/core/decentralized_ai_simulation.py
```

### Running Streamlit Interface
```bash
cd /home/tanmay/Music/build
./venv_ai_simulation/bin/python -m streamlit run decentralized-ai-simulation/src/ui/streamlit_app.py
```

### Running Tests
```bash
cd /home/tanmay/Music/build
./venv_ai_simulation/bin/python -m pytest decentralized-ai-simulation/tests/ -v
```

## Common Development Workflows

### 1. Development Session Setup
```bash
# Activate environment and verify packages
cd /home/tanmay/Music/build
./venv_ai_simulation/bin/python -c "import fastapi, mesa, ray; print('Environment ready!')"

# Start development servers as needed
# Backend API: ./venv_ai_simulation/bin/python -m uvicorn backend.main:app --reload
# Streamlit UI: ./venv_ai_simulation/bin/python -m streamlit run src/ui/streamlit_app.py
```

### 2. Installing New Dependencies
```bash
# Install packages and update requirements
./venv_ai_simulation/bin/pip install new_package_name
./venv_ai_simulation/bin/pip freeze > new_requirements.txt
```

### 3. Package Verification
```bash
# Quick check of critical packages
./venv_ai_simulation/bin/python -c "
import fastapi, mesa, ray, numpy, pandas, networkx, plotly, streamlit
print('All critical packages available!')
"
```

## Environment Management

### Check Installed Packages
```bash
./venv_ai_simulation/bin/pip list
```

### Export Requirements
```bash
./venv_ai_simulation/bin/pip freeze > requirements_complete.txt
```

### Reinstall from Requirements
```bash
./venv_ai_simulation/bin/pip install -r requirements_complete.txt
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're using the virtual environment's Python
   ```bash
   # Wrong: python script.py
   # Correct: ./venv_ai_simulation/bin/python script.py
   ```

2. **Package Not Found**: Verify the package is installed
   ```bash
   ./venv_ai_simulation/bin/pip list | grep package_name
   ```

3. **Permission Issues**: Make sure the virtual environment has execute permissions
   ```bash
   chmod +x venv_ai_simulation/bin/python
   ```

### Environment Validation Script
Create this script to validate your environment:
```bash
cat > validate_env.py << 'EOF'
#!/usr/bin/env python3
import sys
print(f"Python: {sys.version}")
print(f"Executable: {sys.executable}")

try:
    import fastapi, mesa, ray, numpy, pandas, networkx, plotly, streamlit
    print("✓ All critical packages imported successfully!")
    
    print(f"FastAPI: {fastapi.__version__}")
    print(f"Mesa: {mesa.__version__}")
    print(f"Ray: {ray.__version__}")
    print(f"NumPy: {numpy.__version__}")
    print(f"Pandas: {pandas.__version__}")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
EOF

./venv_ai_simulation/bin/python validate_env.py
```

## Next Steps

1. **Start Development**: Use the virtual environment for all Python development
2. **Run Tests**: Execute the test suite to verify everything works
3. **Build Components**: Begin developing the simulation and backend components
4. **Monitor Performance**: Use psutil and other monitoring tools as needed

## Support

For issues with the virtual environment:
1. Verify you're using the correct Python path
2. Check that all dependencies are installed
3. Review the troubleshooting section above
4. Consult the project documentation

---

**Environment Setup Completed**: November 2, 2025  
**Status**: ✅ Ready for Development