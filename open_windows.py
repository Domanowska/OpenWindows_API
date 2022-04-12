import os

import requests as requests


class OpenWeatherApiKeyDoesNotExistError(Exception):
    pass


if __name__ == "__main__":
    # Get API Key from env vars
    API_KEY = os.getenv('OPEN_WEATHER_API_KEY')

    # We need an API Key to access Open Weather Map
    if not API_KEY:
        raise OpenWeatherApiKeyDoesNotExistError(
            "You need to set OPEN_WEATHER_API_KEY in environmental variables!"
        )

    # Get geographical coordinates: https://openweathermap.org/api/geocoding-api
    CITY_NAME = os.getenv('CITY_NAME', 'London')
    geo_response = requests.get(
        'https://api.openweathermap.org/geo/1.0/direct',
        params={'q': CITY_NAME, 'appid': API_KEY},
    )
    lat = geo_response.json()[0]['lat']
    lon = geo_response.json()[0]['lon']

    # Get Weather from Open Weather One-Call Api:
    # https://openweathermap.org/api/one-call-api
    UNITS = os.getenv('UNITS')
    # UNITS can only be of value standard, metric, or imperial
    VALID_UNITS = {'standard', 'metric', 'imperial'}
    if UNITS not in VALID_UNITS:
        print(
            f"UNITS {UNITS} not valid, Options are; 'standard', 'metric', 'imperial'. Setting to default = 'standard'",
        )
        UNITS = 'standard'
    unit = 'C' if UNITS == 'metric' else 'F' if UNITS == 'imperial' else 'K'

    one_call_response = requests.get(
        'https://api.openweathermap.org/data/2.5/onecall',
        params={'lat': lat, 'lon': lon, 'units': UNITS, 'appid': API_KEY},
    )
    # Get dew point from response
    dew_point = one_call_response.json()['current']['dew_point']
    # If dew point is below 62°F (289.85°K, 16.7°C) we can open windows
    # Ideally: 55°F (285.65°K, 12.5°C)
    if (
        (UNITS == 'standard' and dew_point < 289.85)
        or (UNITS == 'metric' and dew_point < 16.7)
        or (UNITS == 'imperial' and dew_point < 62)
    ):
        if (
            (UNITS == 'standard' and dew_point < 285.65)
            or (UNITS == 'metric' and dew_point < 12.5)
            or (UNITS == 'imperial' and dew_point < 55)
        ):
            print(f"Ideal dew point {dew_point}°{unit}! Open the windows!")
        else:
            print(
                f"You can open the windows, but it's not ideal! Dew point: {dew_point}°{unit}"
            )
    else:
        print(f"You can't open the windows, dew_point {dew_point}°{unit} is too high!")

    # TODO: Set up SMS in AWS, how frequent should this script run?
