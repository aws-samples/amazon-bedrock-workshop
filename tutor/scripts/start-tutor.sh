#!/bin/bash
# Bedrock Workshop Tutor startup script
# Runs inside the SageMaker Studio JupyterLab container after repo clone.

set -e

TUTOR_DIR="$HOME/amazon-bedrock-workshop/tutor"
LOG_DIR="/tmp/tutor-logs"
mkdir -p "$LOG_DIR"

echo "=== Starting Bedrock Workshop Tutor ==="

# 1. Discover Studio proxy base URL from metadata + SageMaker API
METADATA="/opt/ml/metadata/resource-metadata.json"
REGION=$(python3 -c "import json; d=json.load(open('$METADATA')); print(d['ResourceArn'].split(':')[3])" 2>/dev/null || echo "us-west-2")
DOMAIN_ID=$(python3 -c "import json; d=json.load(open('$METADATA')); print(d['DomainId'])" 2>/dev/null || echo "")

# Get the space URL from describe_space — returns the exact JupyterLab URL
SPACE_BASE=$(python3 - <<'PYEOF' 2>/dev/null
import json, boto3
meta = json.load(open('/opt/ml/metadata/resource-metadata.json'))
sm = boto3.client('sagemaker', region_name=meta['ResourceArn'].split(':')[3])
space = sm.describe_space(DomainId=meta['DomainId'], SpaceName=meta['SpaceName'])
# Url is like https://8nerfhf9nzasewu.studio.us-west-2.sagemaker.aws/jupyterlab/default
print(space['Url'])
PYEOF
)

if [ -n "$SPACE_BASE" ]; then
    PROXY_BASE="${SPACE_BASE}/proxy/3000"
else
    echo "WARNING: Could not detect space URL, using domain ID fallback"
    PROXY_BASE="https://studio-${DOMAIN_ID}.studio.${REGION}.sagemaker.aws/jupyterlab/default/proxy/3000"
fi

echo "Proxy base: $PROXY_BASE"

# 2. Start the agent (uses instance role credentials automatically)
echo "Starting agent on port 8000..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "Agent already running"
else
    cd "$TUTOR_DIR/agent"
    pip install uv -q 2>/dev/null
    uv sync --quiet
    nohup uv run python main.py > "$LOG_DIR/agent.log" 2>&1 &
    echo $! > /tmp/tutor-agent.pid
    for i in $(seq 1 30); do
        curl -s http://localhost:8000/health > /dev/null 2>&1 && echo "Agent ready (${i}s)" && break
        sleep 1
    done
fi

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
echo $! > /tmp/tutor-ui.pid

echo ""
echo "=== Tutor ready ==="
echo "Open: ${PROXY_BASE}/"
