# Third party imports
import os
import requests
from dotenv import load_dotenv

# Load environmental variables
load_dotenv()

# Constants
api_url = "http://api.weatherapi.com/v1/current.json"
api_key = os.getenv("API_KEY")

# Validate API key
if not api_key:
    raise ValueError("The 'api_key' is missing. Please, set it in the environment variables.")

# Query parameters
params = {
    "key": api_key,
    "q": "krk"
}

try:
    response = requests.get(url=api_url, params=params)
    response.raise_for_status()

    data = response.json()

    # Check if API returned an error
    if "error" in data:
        error_message = data['error'].get('message', 'Unknown error')
        print(f"API Error: {error_message}.")
        raise ValueError(f"API Error: {error_message}.")

    # Extract data safely
    location = data.get("location", {})
    current = data.get("current", {})

    # Ensure valid location and current data
    if not location or not current:
        raise ValueError("Weather data is incomplete or missing.")

    name = location.get("name", "Unknown")
    last_updated = current.get("last_updated", "Unknown")
    current_wind_speed = current.get("wind_kph", "Unknown")
    current_wind_direction = current.get("wind_degree", "Unknown")
    current_temperature = current.get("temp_c", "Unknown")

    # Print weather details
    print(f"Location name: {name}")
    print(f"Last update: {last_updated}.")
    print(f"Current wind direction and speed: {current_wind_direction}⁰ / {current_wind_speed} kph.")
    print(f"Current temperature: {current_temperature}⁰ C.")

except requests.exceptions.RequestException as err:
    print(f"Error fetching weather data: {err}.")

except ValueError as err:
    print(f"API Error: {err}.")
