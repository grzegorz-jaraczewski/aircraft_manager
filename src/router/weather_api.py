# Third party imports
import requests


url = "http://api.weatherapi.com/v1/current.json"

params = {
    "key": "06283cda75c2439e915220408250203",
    "q": "KRK"
}

response = requests.get(url=url, params=params)
data = response.json()

wind_speed = data["current"]["wind_kph"]
wind_direction = data["current"]["wind_degree"]
temperature = data["current"]["temp_c"]

print(f"Current wind direction/speed: {wind_direction}⁰/{wind_speed}kph.")
print(f"Current temperature: {temperature}⁰C.")
