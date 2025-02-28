import pandas as pd
import boto3
import pickle
import random
from datetime import datetime, timedelta
from faker import Faker
import sqlite3
import math



from collections import Counter
from langchain_core.tools import tool
from langchain_core.runnables.config import RunnableConfig
from langchain_aws import ChatBedrockConverse
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_aws.embeddings.bedrock import BedrockEmbeddings
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain.tools.retriever import create_retriever_tool
from langchain_community.vectorstores import FAISS
from langchain.retrievers import ParentDocumentRetriever


from ragas.messages import HumanMessage as RGHumanMessage
from ragas.messages import AIMessage as RGAIMessage
from ragas.messages import ToolMessage as RGToolMessage
from ragas.messages import ToolCall as RGToolCall

from io import BytesIO

def convert_message_langchain_to_ragas(lc_message):
    message_dict = lc_message.model_dump()
    if message_dict['type'] == 'human':
        rg_message = RGHumanMessage(content=message_dict['content'])
    if message_dict['type'] == 'ai':
        if type(message_dict['content']) == list:
            text = list(filter((lambda x: x['type'] == 'text'), message_dict['content']))
            tool = list(filter((lambda x: x['type'] == 'tool_use'), message_dict['content']))
            if len(text) > 0 and len(tool) > 0:

                if len(list(tool[0]['input'].keys())) > 0:
                    dyn_args = {'query': tool[0]['input'][list(tool[0]['input'].keys())[0]]}
                else: 
                    dyn_args = {}
                
                rg_message = RGAIMessage(content=text[0]['text'], tool_calls=[RGToolCall(name=tool[0]['name'], args= dyn_args)])
            elif len(text) > 0:
                rg_message = RGAIMessage(content=text[0]['text'])
            elif len(tool) > 0:
                rg_message = RGAIMessage(content='', tool_calls=[RGToolCall(name=tool[0]['name'], args={#'id': tool[0]['id'], 
                                                                                                        'query': tool[0]['input'][list(tool[0]['input'].keys())[0]]})])
        else:
            rg_message = RGAIMessage(content= message_dict['content'], tool_calls=message_dict['tool_calls'], metadata=message_dict['usage_metadata'])
    if message_dict['type'] == 'tool':
        rg_message = RGToolMessage(content=message_dict['content'], metadata={"tool_name": message_dict['name'], "tool_call_id": message_dict['tool_call_id']})
    return rg_message


def create_agent(enable_memory = False):
    # ---- ⚠️ Update region for your AWS setup ⚠️ ----
    bedrock_client = boto3.client("bedrock-runtime", region_name="us-west-2")
    
    
    
    llm = ChatBedrockConverse(
        model="anthropic.claude-3-haiku-20240307-v1:0",
        temperature=0,
        max_tokens=None,
        client=bedrock_client,
        # other params...
    )
    
    def read_travel_data(file_path: str = "data/synthetic_travel_data.csv") -> pd.DataFrame:
        """Read travel data from CSV file"""
        try:
            df = pd.read_csv(file_path)
            return df
        except FileNotFoundError:
            return pd.DataFrame(
                columns=["Id", "Name","Current_Location","Age","Past_Travel_Destinations", "Number_of_Trips", "Flight_Number", "Departure_City","Arrival_City","Flight_Date",]
            )
    
    
    @tool
    def compare_and_recommend_destination(config: RunnableConfig) -> str:
        """This tool is used to check which destinations user has already traveled.
        If user has already been to a city then do not recommend that city.
    
        Returns:
            str: Destination to be recommended.
    
        """
    
        df = read_travel_data()
        user_id = config.get("configurable", {}).get("user_id")
    
        if user_id not in df["Id"].values:
            return "User not found in the travel database."
    
        user_data = df[df["Id"] == user_id].iloc[0]
        current_location = user_data["Current_Location"]
        age = user_data["Age"]
        past_destinations = user_data["Past_Travel_Destinations"].split(", ")
    
        # Get all past destinations of users with similar age (±5 years) and same current location
        similar_users = df[(df["Current_Location"] == current_location) & (df["Age"].between(age - 5, age + 5))]
        all_destinations = [dest for user_dests in similar_users["Past_Travel_Destinations"].str.split(", ") for dest in user_dests ]
    
        # Count occurrences of each destination
        destination_counts = Counter(all_destinations)
    
        # Remove user's current location and past destinations from recommendations
        for dest in [current_location] + past_destinations:
            if dest in destination_counts:
                del destination_counts[dest]
    
        if not destination_counts:
            return f"No new recommendations found for users in {current_location} with similar age."
    
        # Get the most common destination
        recommended_destination = destination_counts.most_common(1)[0][0]
    
        return f"Based on your current location ({current_location}), age ({age}), and past travel data, we recommend visiting {recommended_destination}."
    
    
    embeddings_model = BedrockEmbeddings(
        client=bedrock_client, model_id="amazon.titan-embed-text-v1"
    )
    
    child_splitter = RecursiveCharacterTextSplitter(
        separators=["\n", "\n\n"], chunk_size=2000, chunk_overlap=250
    )
    
    in_memory_store_file = "data/section_doc_store.pkl"
    vector_store_file = "data/section_vector_store.pkl"
    
    store = pickle.load(open(in_memory_store_file, "rb"))
    vector_db_buff = BytesIO(pickle.load(open(vector_store_file, "rb")))
    vector_db = FAISS.deserialize_from_bytes(
        serialized=vector_db_buff.read(),
        embeddings=embeddings_model,
        allow_dangerous_deserialization=True,
    )

    retriever = ParentDocumentRetriever(
        vectorstore=vector_db,
        docstore=store,
        child_splitter=child_splitter,
    )    
    
    retriever_tool = create_retriever_tool(
        retriever,
        "travel_guide",
        """Holds information from travel guide books containing city details to find information matching the user's interests in various cities. Only search based on the keyword mentioned in user input.

        Args:
            query (str): place to query travel guide.
        Returns:
            str: Information about destination from travel guide.
        
        """,
    )
    
    tools = [compare_and_recommend_destination, retriever_tool]

    if enable_memory:

        memory = MemorySaver()
        agent = create_react_agent(llm, tools, checkpointer = memory)

    else:
        agent = create_react_agent(llm, tools)
    
    return agent



# Initialize Faker
fake = Faker()

# Get today's date
today = datetime.now().date()

# City data with coordinates (latitude, longitude)
city_data = {
    "New York": (40.7128, -74.0060),
    "Los Angeles": (34.0522, -118.2437),
    "Chicago": (41.8781, -87.6298),
    "Las Vegas": (36.1699, -115.1398),
    "San Francisco": (37.7749, -122.4194),
    "Orlando": (28.5383, -81.3792),
    "Miami": (25.7617, -80.1918),
    "Washington": (38.9072, -77.0369),
    "New Orleans": (29.9511, -90.0715),
    "Boston": (42.3601, -71.0589),
    "Seattle": (47.6062, -122.3321),
    "San Diego": (32.7157, -117.1611),
    "Honolulu": (21.3069, -157.8583),
    "Nashville": (36.1627, -86.7816),
    "Denver": (39.7392, -104.9903),
    "Austin": (30.2672, -97.7431),
    "Philadelphia": (39.9526, -75.1652),
    "Atlanta": (33.7490, -84.3880),
    "San Antonio": (29.4241, -98.4936),
    "Portland": (45.5155, -122.6789),
    "Paris": (48.8566, 2.3522),
    "London": (51.5074, -0.1278),
    "Rome": (41.9028, 12.4964),
    "Barcelona": (41.3851, 2.1734),
    "Amsterdam": (52.3676, 4.9041),
    "Berlin": (52.5200, 13.4050),
    "Vienna": (48.2082, 16.3738),
    "Prague": (50.0755, 14.4378),
    "Venice": (45.4408, 12.3155),
    "Florence": (43.7696, 11.2558),
    "Istanbul": (41.0082, 28.9784),
    "Madrid": (40.4168, -3.7038),
    "Lisbon": (38.7223, -9.1393),
    "Dublin": (53.3498, -6.2603),
    "Budapest": (47.4979, 19.0402),
    "Athens": (37.9838, 23.7275),
    "Edinburgh": (55.9533, -3.1883),
    "Copenhagen": (55.6761, 12.5683),
    "Stockholm": (59.3293, 18.0686),
    "Brussels": (50.8503, 4.3517),
    "Zurich": (47.3769, 8.5417),
    "Milan": (45.4642, 9.1900),
    "Munich": (48.1351, 11.5820),
    "Seville": (37.3891, -5.9845),
}

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's radius in kilometers

    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))
    distance = R * c

    return distance

def calculate_flight_duration(distance):
    # Assume average speed of 800 km/h and add 30 minutes for takeoff and landing
    duration_hours = distance / 800
    duration_minutes = int(duration_hours * 60) + 30
    return timedelta(minutes=duration_minutes)

def calculate_flight_price(distance):
    # Base price of $50 plus $0.1 per km
    base_price = 50
    price_per_km = 0.1
    return round(base_price + (distance * price_per_km), 2)

def generate_user(user_id):
    name = fake.name()
    age = random.randint(18, 80)
    home_location = random.choice(list(city_data.keys()))

    return (user_id, name, age, home_location)

def generate_flight_booking(booking_id, user_id, user_name):
    origin = random.choice(list(city_data.keys()))
    destination = random.choice([city for city in city_data.keys() if city != origin])

    origin_coords = city_data[origin]
    dest_coords = city_data[destination]

    distance = calculate_distance(
        origin_coords[0], origin_coords[1], dest_coords[0], dest_coords[1]
    )
    flight_duration = calculate_flight_duration(distance)
    price = calculate_flight_price(distance)

    # Generate a random booking date within the next 15 days
    booking_date = today + timedelta(days=random.randint(0, 14))

    # Generate departure date between 1 and 30 days after the booking date
    departure_date = booking_date + timedelta(days=random.randint(1, 30))

    # Generate departure time
    departure_time = f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}"

    # Calculate arrival date and time
    departure_datetime = datetime.combine(
        departure_date, datetime.strptime(departure_time, "%H:%M").time()
    )
    arrival_datetime = departure_datetime + flight_duration

    return (
        booking_id,
        user_id,
        user_name,
        origin,
        destination,
        price,
        int(flight_duration.total_seconds() // 60),  # Convert to minutes
        departure_date.strftime("%Y-%m-%d"),
        departure_time,
        arrival_datetime.strftime("%Y-%m-%d"),
        arrival_datetime.strftime("%H:%M"),
        round(distance, 2),
        booking_date.strftime("%Y-%m-%d"),
    )

def generate_hotel_booking(booking_id, user_id, user_name):
    city = random.choice(list(city_data.keys()))
    hotel_name = fake.company() + " Hotel"
    check_in_date = fake.date_between(start_date="+1d", end_date="+60d")
    nights = random.randint(1, 14)
    check_out_date = check_in_date + timedelta(days=nights)
    price_per_night = round(random.uniform(50, 500), 2)
    total_price = round(price_per_night * nights, 2)
    num_guests = random.randint(1, 4)
    room_type = random.choice(["Single", "Double", "Suite", "Deluxe"])

    return (
        booking_id,
        user_id,
        user_name,
        city,
        hotel_name,
        check_in_date.strftime("%Y-%m-%d"),
        check_out_date.strftime("%Y-%m-%d"),
        nights,
        price_per_night,
        total_price,
        num_guests,
        room_type,
    )

def create_database():
    conn = sqlite3.connect("data/travel_bookings.db")
    cursor = conn.cursor()

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        name TEXT,
        age INTEGER,
        home_location TEXT
    )
    """
    )

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS flight_bookings (
        booking_id INTEGER PRIMARY KEY,
        user_id INTEGER,
        user_name TEXT,
        origin TEXT,
        destination TEXT,
        price REAL,
        flight_duration INTEGER,
        departure_date TEXT,
        departure_time TEXT,
        arrival_date TEXT,
        arrival_time TEXT,
        distance REAL,
        booking_date TEXT,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    """
    )

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS hotel_bookings (
        booking_id INTEGER PRIMARY KEY,
        user_id INTEGER,
        user_name TEXT,
        city TEXT,
        hotel_name TEXT,
        check_in_date TEXT,
        check_out_date TEXT,
        nights INTEGER,
        price_per_night REAL,
        total_price REAL,
        num_guests INTEGER,
        room_type TEXT,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    """
    )

    conn.commit()
    return conn, cursor

def insert_sample_data(
    conn, cursor, num_users, num_flight_bookings, num_hotel_bookings
):
    # Generate and insert user data
    users = [generate_user(i + 1) for i in range(num_users)]
    cursor.executemany(
        """
    INSERT INTO users (user_id, name, age, home_location)
    VALUES (?, ?, ?, ?)
    """,
        users,
    )

    # Generate and insert flight bookings
    for i in range(num_flight_bookings):
        user = random.choice(users)
        flight_booking = generate_flight_booking(i + 1, user[0], user[1])
        cursor.execute(
            """
        INSERT INTO flight_bookings (booking_id, user_id, user_name, origin, destination, price, flight_duration, departure_date, departure_time, arrival_date, arrival_time, distance, booking_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            flight_booking,
        )

    # Generate and insert hotel bookings
    for i in range(num_hotel_bookings):
        user = random.choice(users)
        hotel_booking = generate_hotel_booking(i + 1, user[0], user[1])
        cursor.execute(
            """
        INSERT INTO hotel_bookings (booking_id, user_id, user_name, city, hotel_name, check_in_date, check_out_date, nights, price_per_night, total_price, num_guests, room_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            hotel_booking,
        )

    conn.commit()

if __name__ == "__main__":
    conn, cursor = create_database()
    insert_sample_data(
        conn, cursor, num_users=500, num_flight_bookings=1000, num_hotel_bookings=1000
    )
    conn.close()
    print("Sample data has been generated and inserted into the SQLite database.")