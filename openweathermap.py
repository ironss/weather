# Weather service file for OpenWeatherMap


import json
import datetime
import math

import weather


debug = False

def _parse_weather(report_text):
    report_raw = json.loads(report_text)
    if debug:
        print(report_raw)

    report = weather.Weather_report(
        datetime.datetime.fromtimestamp(report_raw['dt'], tz=datetime.timezone.utc),
        report_raw['weather'][0]['main'],
        report_raw['weather'][0]['id'],
        report_raw['weather'][0]['icon'],
        report_raw['main']['temp'],
        report_raw['main']['pressure'],
        report_raw['wind']['speed'],
        report_raw['wind']['gust'] if 'gust' in report_raw['wind'] else None,
        report_raw['wind']['deg'],
        math.cos(math.radians(90-report_raw['wind']['deg'])),
        math.sin(math.radians(90-report_raw['wind']['deg'])),
        None,
        report_raw['rain']['1h'] if 'rain' in report_raw else 0,  # rain 1h
        report_raw['main']['humidity'],
        report_raw['clouds']['all'],
        report_raw['visibility'],
    )
    return report

service_weather = {
    'name': 'OpenWeatherMap',
    'url_base': 'https://api.openweathermap.org/data/2.5/weather',
    'url_params': {
        'appid': '{api_key}',
        'lat': '{lat}',
        'lon': '{lon}',
        'units': 'metric',
    },
    'url_headers': {
    },
    'handler': _parse_weather,
}


def _parse_forecast(forecast_text):
    forecast_raw = json.loads(forecast_text)
    if debug:
        print(forecast_raw)

    reports = []
    for fc in forecast_raw['list']:
        report = weather.Weather_report(
            datetime.datetime.fromtimestamp(fc['dt'], tz=datetime.timezone.utc),
            fc['weather'][0]['main'],
            fc['weather'][0]['id'],
            fc['weather'][0]['icon'],
            fc['main']['temp'],
            fc['main']['pressure'],
            fc['wind']['speed'],
            fc['wind']['gust'] if 'gust' in fc['wind'] else None,
            fc['wind']['deg'],
            math.cos(math.radians(90-fc['wind']['deg'])),
            math.sin(math.radians(90-fc['wind']['deg'])),
            None,  # rain
            fc['rain']['3h'] / 3 if 'rain' in fc else 0,  # rain 1h
            fc['main']['humidity'],
            fc['clouds']['all'],
            fc['visibility'],
        )
        reports.append(report)

    return reports

service_forecast = {
    'name': 'OpenWeatherMap',
    'url_base': 'https://api.openweathermap.org/data/2.5/forecast',
    'url_params': {
        'appid': '{api_key}',
        'lat': '{lat}',
        'lon': '{lon}',
        'units': 'metric',
    },
    'url_headers': {
    },
    'handler': _parse_forecast,
}


if __name__ == '__main__':
    import json
    import weather
    import os

    apikey = None

    if apikey is None:
        apikey = os.getenv('OWM_APIKEY')

    if apikey is None:
        secrets_fn = 'secrets.json'
        try:
            with open(secrets_fn) as f:
                secrets = json.load(f)
        except FileNotFoundError:
            secrets = None

        try:
            apikey = secrets['openweathermap']
        except (TypeError, KeyError):
            apikey = None

    if apikey is None:
        raise ValueError('apikey not found')

    owm_secrets = {
        'api_key': apikey,
    }

    locations = [
        ( 'Christchurch, NZ'       , -43.4821,  172.5500,   37),
        ( 'Lyttelton, NZ'          , -43.6000,  172.7200,    0),
        #( 'Nelson, NZ'             , -41.2980,  173.2210,    5),
        #( 'Scott Base, NZ'         , -77.8491,  166.7682,   10),
        #( 'SANAE IV, ZA'           , -71.6724,   -2.8249,  850),
        #( 'Wichita, KA, US'        ,  37.6889,  -97.3361,  400),
        #( 'Amundsen-Scott Base, US', -90.0000,    0.0000, 2835),
    ]

    debug = True
    for loc in locations:
        location = { k: loc[i] for i, k in enumerate(['name', 'lat', 'lon', 'alt']) }
        print(location)

        report = weather.load(service_weather, location, owm_secrets)
        print(report)
        print()

        forecast = weather.load(service_forecast, location, owm_secrets)
        print(forecast)
        print()
