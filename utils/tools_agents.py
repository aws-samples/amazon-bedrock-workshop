import requests

# To add a tool to be used by Claude in main_demo.py,
# create your tool in python as shown below and then create
# a new string variable describing the tool spec. Copy the XML formatting
# that is shown in the below example.
#
# Once you have created your tool and your spec, add the spec variable to the 
# list_of_tools_specs list.


def get_weather(latitude: str, longitude: str):
  url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
  response = requests.get(url)
  return response.json()

get_weather_description = """
<tool_description>
<tool_name>get_weather</tool_name>
<parameters>
<name>latitude</name>
<name>longitude</name>
</parameters>
</tool_description>
"""

def get_lat_long(place):
    
    url = "https://nominatim.openstreetmap.org/search"

    params = {'q': place, 'format': 'json', 'limit': 1}
    response = requests.get(url, params=params).json()

    if response:
        lat = response[0]["lat"]
        lon = response[0]["lon"]
        return {"latitude": lat, "longitude": lon}
    else:
        return None
    
get_lat_long_description = """
<tool_description>
<tool_name>get_lat_long</tool_name>
<parameters>
<name>place</name>  
</parameters>
</tool_description>
"""


list_of_tools_specs = [get_weather_description, get_lat_long_description]




def get_weather_xml(latitude: str, longitude: str):
  url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
  response = requests.get(url)
  return response.json()

get_weather_description = """
<tool_description>
<tool_name>get_weather</tool_name>
<description>
Returns weather data for a given latitude and longitude. </description>
<parameters>
<parameter>
<name>latitude</name>
<type>string</type>
<description>The latitude coordinate as a string</description>
</parameter> <parameter>
<name>longitude</name>
<type>string</type>
<description>The longitude coordinate as a string</description>
</parameter>
</parameters>
</tool_description>
"""

def get_lat_long_xml(place):
    
    url = "https://nominatim.openstreetmap.org/search"

    params = {'q': place, 'format': 'json', 'limit': 1}
    response = requests.get(url, params=params).json()

    if response:
        lat = response[0]["lat"]
        lon = response[0]["lon"]
        return {"latitude": lat, "longitude": lon}
    else:
        return None
    
get_lat_long_description = """<tool_description>
<tool_name>get_lat_long</tool_name>
<description>
Returns the latitude and longitude for a given place name.
</description>
<parameters>
<parameter>
<name>place</name>  
<type>string</type>
<description>
The place name to geocode and get coordinates for.
</description>
</parameter>
</parameters>
</tool_description>"""
