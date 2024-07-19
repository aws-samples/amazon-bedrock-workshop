import os
import json
import uuid
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['table_name'])

def get_named_parameter(event, name):
    """
    Get a parameter from the lambda event
    """
    return next(item for item in event['parameters'] if item['name'] == name)['value']


def get_booking_details(booking_id):
    """
    Retrieve details of a restaurant booking
    
    Args:
        booking_id (string): The ID of the booking to retrieve
    """
    try:
        response = table.get_item(Key={'booking_id': booking_id})
        if 'Item' in response:
            return response['Item']
        else:
            return {'message': f'No booking found with ID {booking_id}'}
    except Exception as e:
        return {'error': str(e)}


def create_booking(date, name, hour, num_guests):
    """
    Create a new restaurant booking
    
    Args:
        date (string): The date of the booking
        name (string): Name to idenfity your reservation
        hour (string): The hour of the booking
        num_guests (integer): The number of guests for the booking
    """
    try:
        booking_id = str(uuid.uuid4())[:8]
        table.put_item(
            Item={
                'booking_id': booking_id,
                'date': date,
                'name': name,
                'hour': hour,
                'num_guests': num_guests
            }
        )
        return {'booking_id': booking_id}
    except Exception as e:
        return {'error': str(e)}


def delete_booking(booking_id):
    """
    Delete an existing restaurant booking
    
    Args:
        booking_id (str): The ID of the booking to delete
    """
    try:
        response = table.delete_item(Key={'booking_id': booking_id})
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return {'message': f'Booking with ID {booking_id} deleted successfully'}
        else:
            return {'message': f'Failed to delete booking with ID {booking_id}'}
    except Exception as e:
        return {'error': str(e)}
    

def lambda_handler(event, context):
    # get the action group used during the invocation of the lambda function
    actionGroup = event.get('actionGroup', '')
    
    # name of the function that should be invoked
    function = event.get('function', '')
    
    # parameters to invoke function with
    parameters = event.get('parameters', [])

    if function == 'get_booking_details':
        booking_id = get_named_parameter(event, "booking_id")
        if booking_id:
            response = str(get_booking_details(booking_id))
            responseBody = {'TEXT': {'body': json.dumps(response)}}
        else:
            responseBody = {'TEXT': {'body': 'Missing booking_id parameter'}}

    elif function == 'create_booking':
        date = get_named_parameter(event, "date")
        name = get_named_parameter(event, "name")
        hour = get_named_parameter(event, "hour")
        num_guests = get_named_parameter(event, "num_guests")

        if date and hour and num_guests:
            response = str(create_booking(date, name, hour, num_guests))
            responseBody = {'TEXT': {'body': json.dumps(response)}}
        else:
            responseBody = {'TEXT': {'body': 'Missing required parameters'}}

    elif function == 'delete_booking':
        booking_id = get_named_parameter(event, "booking_id")
        if booking_id:
            response = str(delete_booking(booking_id))
            responseBody = {'TEXT': {'body': json.dumps(response)}}
        else:
            responseBody = {'TEXT': {'body': 'Missing booking_id parameter'}}

    else:
        responseBody = {'TEXT': {'body': 'Invalid function'}}

    action_response = {
        'actionGroup': actionGroup,
        'function': function,
        'functionResponse': {
            'responseBody': responseBody
        }
    }

    function_response = {'response': action_response, 'messageVersion': event['messageVersion']}
    print("Response: {}".format(function_response))

    return function_response
