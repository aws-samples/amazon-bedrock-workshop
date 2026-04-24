#!/bin/bash
set -e

echo "🚀 Starting Bedrock Workshop Tutor..."

# Navigate to script directory
cd "$(dirname "$0")"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    echo "📥 Installing dependencies..."
    .venv/bin/pip install --quiet --upgrade pip
    .venv/bin/pip install --quiet -r requirements.txt
else
    echo "📦 Using existing virtual environment"
fi

# Verify installations
echo "🔍 Verifying dependencies..."
.venv/bin/python << 'PYEOF'
import sys
try:
    import streamlit, boto3, openai, yaml, numpy
    from code_editor import code_editor
    print("✓ All dependencies available")
except ImportError as e:
    print(f"✗ Missing dependency: {e}")
    sys.exit(1)
PYEOF

echo "🔧 Starting Streamlit..."
exec .venv/bin/streamlit run streamlit_app.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.gatherUsageStats=false
