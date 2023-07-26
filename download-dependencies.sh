#!/bin/sh

echo "Creating directory"
mkdir -p ./dependencies && \
cd ./dependencies && \
echo "Downloading dependencies"
curl -sS https://preview.documentation.bedrock.aws.dev/Documentation/SDK/bedrock-python-sdk.zip > sdk.zip && \
echo "Unpacking dependencies"
# (SageMaker Studio system terminals don't have `unzip` utility installed)
if command -v unzip &> /dev/null
then
    unzip sdk.zip && rm sdk.zip && echo "Done"
else
    echo "'unzip' command not found: Trying to unzip via Python"
    python -m zipfile -e sdk.zip . && rm sdk.zip && echo "Done"
fi
