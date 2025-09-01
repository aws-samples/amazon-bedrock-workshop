import python_weather
import asyncio
import json


def lambda_handler(event, context):
    city = json.loads(event['body']).get('city') if isinstance(
        event.get('body'), str) else event.get('city')

    async def get_weather():
        async with python_weather.Client() as client:
            weather = await client.get(city)
            return {"city": city, "temperature": weather.temperature, "description": weather.description}

    return {'statusCode': 200, 'body': json.dumps(asyncio.run(get_weather()))}
