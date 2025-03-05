# Third party imports
import os
import requests
from dotenv import load_dotenv

# Load environmental variables
load_dotenv()


class WeatherApi:
    def __init__(self, api_url="http://api.weatherapi.com/v1/current.json", api_key=None, fields=None, **api_params):
        self.api_url = api_url
        self.api_key = api_key or os.getenv("API_KEY")
        self.api_params = api_params or {}
        self.api_params.setdefault("key", self.api_key)
        self.api_params.setdefault("q", "krk")

        if fields:
            self.fields = {
                "location": fields.get("location"),
                "current": fields.get("current"),
                "name": fields.get("name"),
                "last_updated": fields.get("last_updated"),
                "current_wind_speed": fields.get("current_wind_speed"),
                "current_wind_direction": fields.get("current_wind_direction"),
                "current_temperature": fields.get("current_temperature")
            }
        self.name = None
        self.last_updated = None
        self.current_wind_speed = None
        self.current_wind_direction = None
        self.current_temperature = None

    def get_weather_data(self):
        try:
            response = requests.get(url=self.api_url, params=self.api_params)
            response.raise_for_status()

            data = response.json()

            # Check if API returned an error
            if "error" in data:
                error_message = data['error'].get('message', 'Unknown error')
                print(f"API Error: {error_message}.")
                raise ValueError(f"API Error: {error_message}.")

            # Extract data safely
            location = data.get(self.fields.get("location"), {})
            current = data.get(self.fields.get("current"), {})

            # Ensure valid location and current data
            if not location or not current:
                raise ValueError("Weather data is incomplete or missing.")

            self.name = location.get(self.fields.get("name"), "Unknown")
            self.last_updated = current.get(self.fields.get("last_updated"), "Unknown")
            self.current_wind_speed = current.get(self.fields.get("current_wind_speed"), "Unknown")
            self.current_wind_direction = current.get(self.fields.get("current_wind_direction"), "Unknown")
            self.current_temperature = current.get(self.fields.get("current_temperature"), "Unknown")

        except requests.exceptions.RequestException as err:
            print(f"Error fetching weather data: {err}.")

        except ValueError as err:
            print(f"API Error: {err}.")

    def print_weather_data(self):
        # Print weather details
        print(f"Location name: {self.name}")
        print(f"Last update: {self.last_updated}.")
        print(f"Current wind direction and speed: {self.current_wind_direction}⁰ / {self.current_wind_speed} kph.")
        print(f"Current temperature: {self.current_temperature}⁰ C.")


weather_api = WeatherApi(
    fields={
        "location": "location",
        "current": "current",
        "name": "name",
        "last_updated": "last_updated",
        "current_wind_speed": "wind_kph",
        "current_wind_direction": "wind_degree",
        "current_temperature": "temp_c"
    },
    q="waw")

weather_api.get_weather_data()
weather_api.print_weather_data()

new_weather_api = WeatherApi(
    api_url="http://api.weatherstack.com/current",
    fields={
        "location": "location",
        "current": "current",
        "name": "name",
        "last_updated": "observation_time",
        "current_wind_speed": "wind_speed",
        "current_wind_direction": "wind_degree",
        "current_temperature": "temperature"
    },
    access_key=os.getenv("NEW_API_KEY"), query="ktw"
)
new_weather_api.get_weather_data()
new_weather_api.print_weather_data()
