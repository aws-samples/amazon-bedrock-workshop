import os
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
from strands import Agent, tool
from bedrock_agentcore.runtime import BedrockAgentCoreApp # <-- Import the Runtime App
from strands.models import BedrockModel
from strands_tools import current_time, retrieve
import boto3
import uuid

# Load passed environment variables
kb_id = os.environ["KNOWLEDGE_BASE_ID"]
kb_name = os.environ["KNOWLEDGE_BASE_NAME"]
db_table_name = os.environ["DB_TABLE_NAME"]
model_id = os.environ["BEDROCK_MODEL_ID"]
system_prompt = os.environ["BEDROCK_MODEL_SYSTEM_PROMPT"]

# Retrieve DynamoDB table resource
dynamodb = boto3.resource('dynamodb')
db_table = dynamodb.Table(db_table_name)

# Initialize the Bedrock AgentCore app
app = BedrockAgentCoreApp()

@tool
def get_booking_details(booking_id: str, restaurant_name: str) -> dict:
    """Get the relevant details for booking_id in restaurant_name
    Args:
        booking_id: the id of the reservation
        restaurant_name: name of the restaurant handling the reservation

    Returns:
        booking_details: the details of the booking in JSON format
    """

    try:
        response = db_table.get_item(
            Key={"booking_id": booking_id, "restaurant_name": restaurant_name}
        )
        if "Item" in response:
            return response["Item"]
        else:
            return f"No booking found with ID {booking_id}"
    except Exception as e:
        return str(e)
    
@tool
def delete_booking(booking_id: str, restaurant_name:str) -> str:
    """delete an existing booking_id at restaurant_name
    Args:
        booking_id: the id of the reservation
        restaurant_name: name of the restaurant handling the reservation

    Returns:
        confirmation_message: confirmation message
    """
    try:
        response = db_table.delete_item(Key={'booking_id': booking_id, 'restaurant_name': restaurant_name})
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return f'Booking with ID {booking_id} deleted successfully'
        else:
            return f'Failed to delete booking with ID {booking_id}'
    except Exception as e:
        return str(e)

@tool
def create_booking(date: str, hour: str, restaurant_name: str, guest_name: str, num_guests: str) -> str:
    """Create a new booking at restaurant_name
    Args:
        date: The date of the booking in the format YYYY-MM-DD. 
        hour:the hour of the booking in the format HH:MM"
        restaurant_name:The name of the restaurant handling the reservation"
        guest_name: The name of the customer to have in the reservation"
        num_guests: The number of guests for the booking"

    Returns:
        confirmation_message: confirmation message
    """
    
    print(f"Creating reservation for {num_guests} people at {restaurant_name}, {date} at {hour} in the name of {guest_name}")
    try:
        booking_id = str(uuid.uuid4())[:8]
        db_table.put_item(
            Item={
                'booking_id': booking_id,
                'restaurant_name': restaurant_name,
                'date': date,
                'name': guest_name,
                'hour': hour,
                'num_guests': num_guests
            }
        )
        return f"Reservation created with booking id: {booking_id}"
    except Exception as e:
        print(e)
        return "Failed to create booking."



model = BedrockModel(
    model_id=model_id,
)
agent = Agent(
    model=model,
    tools=[current_time, retrieve, get_booking_details, create_booking, delete_booking],
    system_prompt=system_prompt
)

@app.entrypoint # <-- Decorate the invocation function
def strands_agent_bedrock(payload):
    """
    Invoke the agent with a payload
    """
    user_input = payload.get("prompt")
    print("User input:", user_input)
    response = agent(user_input)
    return response.message['content'][0]['text']

if __name__ == "__main__":
    app.run() # <-- Let AgentCoreRuntime control the running of the agent with `app.run()`
