# agent knowledge base
echo "deploying knowledge base ..."
python prereqs/knowledge_base.py --mode create

# agent dynamodb
echo "deploying DynamoDB ..."
python prereqs/dynamodb.py --mode create


