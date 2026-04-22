#!/bin/bash
# Bedrock Workshop Tutor startup script
# Runs inside the SageMaker Studio JupyterLab container after repo clone.

set -e

TUTOR_DIR="$HOME/amazon-bedrock-workshop/tutor"
LOG_DIR="/tmp/tutor-logs"
mkdir -p "$LOG_DIR"

echo "=== Starting Bedrock Workshop Tutor ==="

# 1. Discover Studio domain and region from metadata
METADATA="/opt/ml/metadata/resource-metadata.json"
DOMAIN_ID=$(python3 -c "import json; d=json.load(open('$METADATA')); print(d['DomainId'])")
REGION=$(python3 -c "import json; d=json.load(open('$METADATA')); print(d['ResourceArn'].split(':')[3])")
PROXY_BASE="https://${DOMAIN_ID}.studio.${REGION}.sagemaker.aws/jupyterlab/default/proxy/3000"
echo "Proxy base: $PROXY_BASE"

# 2. Start the agent
echo "Starting agent on port 8000..."
cd "$TUTOR_DIR/agent"
pip install uv -q 2>/dev/null
uv sync --quiet
nohup uv run python main.py > "$LOG_DIR/agent.log" 2>&1 &

for i in $(seq 1 30); do
    curl -s http://localhost:8000/health > /dev/null 2>&1 && echo "Agent ready (${i}s)" && break
    sleep 1
done

# 3. Build and start the UI
echo "Building UI..."
cd "$TUTOR_DIR"
npm install --quiet 2>/dev/null

export NEXT_PUBLIC_COPILOTKIT_URL="${PROXY_BASE}/api/copilotkit"
export NEXT_ASSET_PREFIX="/jupyterlab/default/proxy/3000"
export NEXT_PUBLIC_AGENT_URL="http://localhost:8000"

npm run build > "$LOG_DIR/build.log" 2>&1
echo "Build complete"

AGENT_URL=http://localhost:8000 nohup npx next start --port 3000 > "$LOG_DIR/ui.log" 2>&1 &

echo ""
echo "=== Tutor ready ==="
echo "Open: ${PROXY_BASE}/"
