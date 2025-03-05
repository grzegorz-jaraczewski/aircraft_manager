# Third party imports
import os
import requests
from dotenv import load_dotenv
from dataclasses import dataclass

# Load environmental variables
load_dotenv()


@dataclass
class FieldsMapper:
    location: str = None
    current: str = None
    name: str = None
    last_updated: str = None
    current_wind_speed: str = None
    current_wind_direction: str = None
    current_temperature: str = None


@dataclass
class WeatherData:
    name: str = None
    last_updated: str = None
    current_wind_speed: str = None
    current_wind_direction: str = None
    current_temperature: str = None


class WeatherApi:
    def __init__(self,
                 api_url: str = None,
                 api_key: str = None,
                 fields: FieldsMapper = None,
                 **api_params):
        self.api_url = api_url
        self.api_key = api_key or os.getenv("API_KEY")
        self.api_params = api_params or {}
        self.fields = fields
        self.location = None
        self.current = None

    def get_weather_data(self) -> WeatherData | None:
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
            self.location = data.get(self.fields.location, {})
            self.current = data.get(self.fields.current, {})

            # Ensure valid location and current data
            if not self.location or not self.current:
                raise ValueError("Weather data is incomplete or missing.")

        except requests.exceptions.RequestException as err:
            print(f"Error fetching weather data: {err}.")

        except ValueError as err:
            print(f"API Error: {err}.")

        return WeatherData(
            name=self.location.get(self.fields.name, "Unknown"),
            last_updated=self.current.get(self.fields.last_updated, "Unknown"),
            current_wind_speed=self.current.get(self.fields.current_wind_speed, "Unknown"),
            current_wind_direction=self.current.get(self.fields.current_wind_direction, "Unknown"),
            current_temperature=self.current.get(self.fields.current_temperature, "Unknown")
        )

    @staticmethod
    def show_weather_data(wx_data: WeatherData):
        # Print weather details
        print(f"Location name: {wx_data.name}.")
        print(f"Last update: {wx_data.last_updated}.")
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
        ), access_key=os.getenv("NEW_API_KEY"), query="ktw")

    new_weather_data = new_weather_api.get_weather_data()
    new_weather_api.show_weather_data(wx_data=new_weather_data)
