#!/bin/bash
# Bedrock Workshop Tutor startup script
# Runs inside the SageMaker Studio JupyterLab container after repo clone.

set -e

TUTOR_DIR="$HOME/amazon-bedrock-workshop/tutor"
LOG_DIR="/tmp/tutor-logs"
mkdir -p "$LOG_DIR"

echo "=== Starting Bedrock Workshop Tutor ==="

# 1. Discover Studio proxy base URL from describe_space
METADATA="/opt/ml/metadata/resource-metadata.json"
REGION=$(python3 -c "import json; d=json.load(open('$METADATA')); print(d['ResourceArn'].split(':')[3])" 2>/dev/null || echo "us-west-2")
DOMAIN_ID=$(python3 -c "import json; d=json.load(open('$METADATA')); print(d['DomainId'])" 2>/dev/null || echo "")

SPACE_BASE=$(python3 - <<'PYEOF' 2>/dev/null
import json, boto3
meta = json.load(open('/opt/ml/metadata/resource-metadata.json'))
sm = boto3.client('sagemaker', region_name=meta['ResourceArn'].split(':')[3])
space = sm.describe_space(DomainId=meta['DomainId'], SpaceName=meta['SpaceName'])
print(space['Url'])
PYEOF
)

if [ -n "$SPACE_BASE" ]; then
    PROXY_BASE="${SPACE_BASE}/proxy/3000"
else
    PROXY_BASE="https://studio-${DOMAIN_ID}.studio.${REGION}.sagemaker.aws/jupyterlab/default/proxy/3000"
fi

echo "Proxy base: $PROXY_BASE"
# Extract the path prefix from the space base URL (everything after the hostname)
# e.g. https://8nerfhf9.studio.us-west-2.sagemaker.aws/jupyterlab/default -> /jupyterlab/default
SPACE_PATH=$(echo "$SPACE_BASE" | sed 's|https://[^/]*||')
PREFIX="${SPACE_PATH}/proxy/3000"

# 2. Start the agent
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

# 3. Build Next.js (plain, no basePath)
echo "Building UI..."
cd "$TUTOR_DIR"
npm install --quiet 2>/dev/null

# Write to .env.local so Next.js bakes NEXT_PUBLIC_* vars into the build
cat > .env.local << EOF
NEXT_PUBLIC_COPILOTKIT_URL=${PROXY_BASE}/api/copilotkit
NEXT_PUBLIC_AGENT_URL=http://localhost:8000
EOF

AGENT_URL=http://localhost:8000 npm run build > "$LOG_DIR/build.log" 2>&1
echo "Build complete"

# Start Next.js on port 3001
AGENT_URL=http://localhost:8000 nohup npx next start --port 3001 > "$LOG_DIR/ui.log" 2>&1 &
echo $! > /tmp/tutor-ui.pid
sleep 3

# 4. Start a tiny proxy on port 3000 that rewrites /_next/ -> PREFIX/_next/ in HTML
python3 - <<PYEOF &
import http.server, http.client, gzip, zlib

PREFIX = "$PREFIX"

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):  self._proxy("GET")
    def do_POST(self): self._proxy("POST")
    def do_PUT(self):  self._proxy("PUT")

    def _proxy(self, method):
        path = self.path
        if path.startswith(PREFIX):
            path = path[len(PREFIX):] or "/"

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length > 0 else None

        headers = {k: v for k, v in self.headers.items()
                   if k.lower() not in ("host", "content-length", "transfer-encoding")}
        if body:
            headers["Content-Length"] = str(len(body))

        try:
            conn = http.client.HTTPConnection("localhost", 3001, timeout=120)
            conn.request(method, path, body=body, headers=headers)
            r = conn.getresponse()
            raw = r.read()
            ct = r.getheader("Content-Type", "")
            enc = r.getheader("Content-Encoding", "")

            if "text/html" in ct:
                if enc == "gzip":
                    raw = gzip.decompress(raw)
                elif enc == "deflate":
                    raw = zlib.decompress(raw)
                raw = raw.replace(b'"/_next/', f'"{PREFIX}/_next/'.encode())
                raw = raw.replace(b"'/_next/", f"'{PREFIX}/_next/".encode())
                enc = ""

            self.send_response(r.status)
            for k, v in r.getheaders():
                if k.lower() not in ("transfer-encoding", "content-length", "content-encoding"):
                    self.send_header(k, v)
            if enc:
                self.send_header("Content-Encoding", enc)
            self.send_header("Content-Length", len(raw))
            self.end_headers()
            self.wfile.write(raw)
            conn.close()
        except Exception as e:
            self.send_error(502, str(e))

    def log_message(self, *a): pass

http.server.HTTPServer(("0.0.0.0", 3000), Handler).serve_forever()
PYEOF
echo $! > /tmp/tutor-proxy.pid
sleep 1

echo ""
echo "=== Tutor ready ==="
echo "Open: ${PROXY_BASE}/"
