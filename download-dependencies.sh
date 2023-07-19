#!/bin/sh

echo "Creating directory"
mkdir -p ./dependencies && \
cd ./dependencies && \
echo "Downloading dependencies"
curl -sS https://preview.documentation.bedrock.aws.dev/Documentation/SDK/bedrock-python-sdk.zip > sdk.zip && \
echo "Unpacking dependencies"
unzip sdk.zip && \
rm sdk.zip