# Third party imports
import logging
import os
import requests
from dotenv import load_dotenv
from dataclasses import dataclass
from dateutil import parser

# Load environmental variables
load_dotenv()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def date_formatter(date_input: str) -> str:
    """
    Parses and formats a given date string into the format YYYY-MM-DD HH:MM.

    Args:
        date_input: A string representing a date/time.

    Returns:
        Formatted date string in YYYY-MM-DD HH:MM format.

    Raises:
        ValueError: If the input date format is invalid.
    """
    try:
        date_formatted = parser.parse(date_input)
        return date_formatted.strftime("%Y-%m-%d %H:%M")
    except TypeError:
        raise TypeError("Invalid date/time input. Please provide recognizable data.")


@dataclass
class FieldsMapper:
    """
    Data class for mapping field names used in the API response.

    Attributes:
        location: Key for location data.
        current: Key for current weather data.
        name: Key for location name.
        last_updated: Key for last updated time.
        current_wind_speed: Key for wind speed.
        current_wind_direction: Key for wind direction.
        current_temperature: Key for temperature.
    """
    location: str = None
    current: str = None
    name: str = None
    last_updated: str = None
    current_wind_speed: str = None
    current_wind_direction: str = None
    current_temperature: str = None


@dataclass
class WeatherData:
    """
    Data class representing the structured weather data.

    Attributes:
        name: Location name.
        last_updated: Last updated timestamp.
        current_wind_speed: Current wind speed.
        current_wind_direction: Current wind direction.
        current_temperature: Current temperature.
    """
    name: str = None
    last_updated: str = None
    current_wind_speed: str = None
    current_wind_direction: str = None
    current_temperature: str = None


class WeatherApi:
    """
    A class to interact with a weather API and fetch weather data.

    Attributes:
        api_url: Base URL of the weather API.
        api_key: API key for authentication.
        fields: An instance of FieldsMapper for mapping API response fields.
        api_params: Additional parameters to pass to the API request.
    """
    def __init__(self,
                 api_url: str = None,
                 api_key: str = None,
                 fields: FieldsMapper = None,
                 **api_params: str):
        self.api_url = api_url
        self.api_key = api_key or os.getenv("API_KEY")
        self.api_params = api_params or {}
        self.fields = fields
        self.location = {}
        self.current = {}

    def get_weather_data(self) -> WeatherData:
        """
        Fetches weather data from the API and structures it into a WeatherData object.

        Returns:
            A WeatherData object containing structured weather information.

        Raises:
             ValueError: If the API response contains an error or missing data.
        """
        try:
            response = requests.get(url=self.api_url, params=self.api_params)
            response.raise_for_status()

            data = response.json()

            # Check if API returned an error
            if "error" in data:
                error_message = data['error'].get('message', 'Unknown error')
                logger.error(f"API Error: {error_message}")
                raise ValueError(f"API Error: {error_message}.")

            # Extract data safely
            self.location = data.get(self.fields.location, {})
            self.current = data.get(self.fields.current, {})

            # Ensure valid location and current data
            if not self.location or not self.current:
                logger.error("Weather data is incomplete or missing.")
                raise ValueError("Weather data is incomplete or missing.")

        except requests.exceptions.RequestException as err:
            logger.error(f"Error fetching weather data: {err}.")

        except ValueError as err:
            logger.error(f"API Error: {err}.")

        return WeatherData(
            name=self.location.get(self.fields.name, "Unknown"),
            last_updated=self.current.get(self.fields.last_updated, "Unknown"),
            current_wind_speed=self.current.get(self.fields.current_wind_speed, "Unknown"),
            current_wind_direction=self.current.get(self.fields.current_wind_direction, "Unknown"),
            current_temperature=self.current.get(self.fields.current_temperature, "Unknown")
        )

    @staticmethod
    def show_weather_data(wx_data: WeatherData):
        """
        Displays weather data in a readable format.

        Args:
            wx_data: A WeatherData object containing weather details.
        """
        # Print weather details
        print(f"Location name: {wx_data.name}.")
        print(f"Last update: {date_formatter(wx_data.last_updated)}.")
        print(f"Current wind direction and speed: {wx_data.current_wind_direction}⁰ /"
              f" {wx_data.current_wind_speed} kph.")
        print(f"Current temperature: {wx_data.current_temperature}⁰ C.")
        print("-----End of message-----")
        print()


if __name__ == "__main__":
    # First API service
    weather_api = WeatherApi(
        api_url="http://api.weatherapi.com/v1/current.json",
        fields=FieldsMapper(
            location="location",
            current="current",
            name="name",
            last_updated="last_updated",
            current_wind_speed="wind_kph",
            current_wind_direction="wind_degree",
            current_temperature="temp_c"
        ), key=os.getenv("API_KEY"), q="waw")

    weather_data = weather_api.get_weather_data()
    weather_api.show_weather_data(wx_data=weather_data)

    # Second API service
    new_weather_api = WeatherApi(
        api_url="http://api.weatherstack.com/current",
        fields=FieldsMapper(
            location="location",
            current="current",
            name="name",
            last_updated="observation_time",
            current_wind_speed="wind_speed",
            current_wind_direction="wind_degree",
            current_temperature="temperature"
        ), access_key=os.getenv("NEW_API_KEY"), query="krk")

    new_weather_data = new_weather_api.get_weather_data()
    new_weather_api.show_weather_data(wx_data=new_weather_data)
