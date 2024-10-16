import json
import uuid
import boto3
import urllib.request
from urllib.parse import quote


def lambda_handler(event, _):
    """
    This function gets the weather information for a given city
    """

    # Extract info from the event
    actionGroup = event.get('actionGroup', '')
    function = event.get('function', '')
    city = event['parameters'][0]['value']
    encoded_city = quote(city)

    # Get the location data based on the city
    url = f'https://geocoding-api.open-meteo.com/v1/search?name={encoded_city}&count=1&language=en&format=json'
    with urllib.request.urlopen(url) as response:
        location_data = json.loads(response.read().decode())
        if not location_data['results']:
            return {"error": "City not found"}
        
        lat = location_data['results'][0]['latitude']
        lon = location_data['results'][0]['longitude']

    # Get the weather data based on the location
    weather_url = f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m&daily=weather_code,temperature_2m_max,temperature_2m_min&timezone=auto'
    with urllib.request.urlopen(weather_url) as response:
        weather_data = json.loads(response.read().decode())

    current = weather_data['current']
    daily = weather_data['daily']

    # Prepare the response
    weather_codes = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Depositing rime fog",
        51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        71: "Slight snow fall", 73: "Moderate snow fall", 75: "Heavy snow fall",
        77: "Snow grains", 80: "Slight rain showers", 81: "Moderate rain showers",
        82: "Violent rain showers", 85: "Slight snow showers", 86: "Heavy snow showers",
        95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
    }
    response_core =  {   
        'temperature': current['temperature_2m'],
        'condition': weather_codes.get(current['weather_code'], "Unknown"),
        'humidity': current['relative_humidity_2m'],
        'wind_speed': current['wind_speed_10m'],
        'forecast_max': daily['temperature_2m_max'][0],
        'forecast_min': daily['temperature_2m_min'][0],
        'forecast_condition': weather_codes.get(daily['weather_code'][0], "Unknown")
    }

    responseBody = {'TEXT': {'body': json.dumps(response_core)}}
    action_response = {
        'actionGroup': actionGroup,
        'function': function,
        'functionResponse': {
            'responseBody': responseBody
        }
    }
    function_response = {'response': action_response, 'messageVersion': event['messageVersion']}

    return function_response

    
