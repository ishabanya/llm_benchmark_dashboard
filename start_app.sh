#!/bin/bash

# LLM Benchmark Framework - Deployment Script
echo "🚀 Starting LLM Benchmark Framework..."

# Set the correct directory
cd "$(dirname "$0")"

# Set Python path to include src directory
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"

# Check if required Python version is available
if command -v python3.10 &> /dev/null; then
    PYTHON_CMD="python3.10"
else
    echo "⚠️  Python 3.10 not found, trying python3..."
    PYTHON_CMD="python3"
fi

# Start Streamlit app
echo "📊 Starting Streamlit dashboard on http://localhost:8501"
echo "🔧 Using Python: $PYTHON_CMD"
echo "📁 Project directory: $(pwd)"
echo "🐍 Python path: $PYTHONPATH"
echo ""
echo "💡 To stop the app, press Ctrl+C"
echo ""

$PYTHON_CMD -m streamlit run web_ui/app.py --server.port 8501 