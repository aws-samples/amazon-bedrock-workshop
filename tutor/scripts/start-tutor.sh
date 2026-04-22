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

# Get the studio subdomain from the presigned URL (host = <subdomain>.studio.<region>.sagemaker.aws)
STUDIO_HOST=$(python3 - <<'PYEOF' 2>/dev/null
import json, boto3, re
meta = json.load(open('/opt/ml/metadata/resource-metadata.json'))
sm = boto3.client('sagemaker', region_name=meta['ResourceArn'].split(':')[3])
url = sm.create_presigned_domain_url(
    DomainId=meta['DomainId'],
    UserProfileName=meta['UserProfileName'],
    ExpiresInSeconds=60
)['AuthorizedUrl']
host = re.search(r'https://([^/]+)', url).group(1)
print(host)
PYEOF
)

if [ -n "$STUDIO_HOST" ]; then
    PROXY_BASE="https://${STUDIO_HOST}/jupyterlab/default/proxy/3000"
else
    echo "WARNING: Could not detect Studio host, using domain ID fallback"
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
