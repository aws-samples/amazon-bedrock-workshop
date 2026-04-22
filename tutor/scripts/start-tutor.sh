#!/bin/bash
# Bedrock Workshop Tutor startup script
# Runs inside the SageMaker Studio JupyterLab container after repo clone.

set -e

TUTOR_DIR="$HOME/amazon-bedrock-workshop/tutor"
LOG_DIR="/tmp/tutor-logs"
mkdir -p "$LOG_DIR"

echo "=== Starting Bedrock Workshop Tutor ==="

# 1. Discover Studio proxy base URL
# The space subdomain is in the browser URL but not available inside the container.
# We derive it from the Jupyter server token URL or accept it as an argument.
METADATA="/opt/ml/metadata/resource-metadata.json"
REGION=$(python3 -c "import json; d=json.load(open('$METADATA')); print(d['ResourceArn'].split(':')[3])" 2>/dev/null || echo "us-west-2")

if [ -n "$1" ]; then
    # Subdomain passed as argument: bash start-tutor.sh <subdomain>
    SPACE_SUBDOMAIN="$1"
else
    # Try to extract from the Jupyter token URL (contains the full proxy path)
    SPACE_SUBDOMAIN=$(jupyter server list 2>/dev/null | grep -oP '[a-z0-9]+(?=\.studio)' | head -1 || echo "")
fi

if [ -z "$SPACE_SUBDOMAIN" ]; then
    # Fallback: use domain ID (wrong subdomain but prints instructions)
    DOMAIN_ID=$(python3 -c "import json; d=json.load(open('$METADATA')); print(d['DomainId'])" 2>/dev/null || echo "unknown")
    PROXY_BASE="https://${DOMAIN_ID}.studio.${REGION}.sagemaker.aws/jupyterlab/default/proxy/3000"
    echo ""
    echo "NOTE: Could not auto-detect your Studio subdomain."
    echo "Run with your subdomain from the browser URL:"
    echo "  bash start-tutor.sh <subdomain>"
    echo "e.g. if your URL is https://abc123.studio.us-west-2.sagemaker.aws/..."
    echo "  bash start-tutor.sh abc123"
    echo ""
else
    PROXY_BASE="https://${SPACE_SUBDOMAIN}.studio.${REGION}.sagemaker.aws/jupyterlab/default/proxy/3000"
fi

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
