#!/bin/bash
set -e

echo "🚀 Starting Amazon Bedrock Interactive Tutor"

cd "$(dirname "$0")"

# Create venv if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "📥 Installing dependencies..."
    venv/bin/pip install --quiet --upgrade pip
    venv/bin/pip install --quiet -r requirements.txt
else
    echo "📦 Using existing virtual environment"
fi

# Get proxy URL
echo ""
echo "========================================="
if [ -f "/opt/ml/metadata/resource-metadata.json" ]; then
    DOMAIN_ID=$(python3 -c "import json; print(json.load(open('/opt/ml/metadata/resource-metadata.json'))['DomainId'])")
    SPACE_NAME=$(python3 -c "import json; print(json.load(open('/opt/ml/metadata/resource-metadata.json'))['SpaceName'])")
    REGION=$(python3 -c "import json; arn=json.load(open('/opt/ml/metadata/resource-metadata.json'))['ResourceArn']; print(arn.split(':')[3])")
    SPACE_URL=$(aws sagemaker describe-space --domain-id "$DOMAIN_ID" --space-name "$SPACE_NAME" --region "$REGION" --query 'Url' --output text 2>/dev/null)

    if [ -n "$SPACE_URL" ]; then
        echo "✓ Detected SageMaker Space"
        echo ""
        echo "📡 Access your tutor at:"
        echo "${SPACE_URL}/proxy/8002/"
        echo "========================================="
    fi
fi
echo ""

echo "🔧 Starting FastAPI server on port 8002..."
cd backend

# Install websockets if not already installed
../venv/bin/pip show websockets > /dev/null 2>&1 || {
    echo "📦 Installing websockets..."
    ../venv/bin/pip install --quiet websockets
}

exec ../venv/bin/uvicorn main:app \
    --host 0.0.0.0 \
    --port 8002 \
    --log-level info
