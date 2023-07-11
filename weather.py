import datetime
from datetime import datetime

import requests
from config import OPENWEATHER_TOKEN
from pytemperature import k2c

def get_lat_lon_city(city_name, max_attempts = 10):
    url = f'http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit={1}&appid={OPENWEATHER_TOKEN}'
    attempt = 0
    while attempt < max_attempts:
        try:
            data = requests.get(url, timeout=0.1).json()
            lat = data[0]['lat']
            lon = data[0]['lon']
            return lat, lon
        except requests.exceptions.Timeout:
            print(f'Ошибка таймаута, при попытке {attempt+1}')
            attempt += 1
        except Exception as e:
            print(f'Ошибка {e}')
            break
    else:
        print('Не удалось получить данные')


def get_current_weather(lat_city, lon_city):
    url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_TOKEN}&lang=ru'
    attempts = 10

    for i in range(attempts):
        try:
            print(url)
            data = requests.get(url, timeout=0.2).json()
            print(data)
            current_weather_description = data["weather"][0]["description"]
            current_temp = k2c(data['main']['temp'])
            current_temp_feels_like = k2c(data['main']['feels_like'])
            current_humidity = data["main"]["humidity"]
            current_wind_speed = data["wind"]["speed"]
            current_clouds_percent = data["clouds"]["all"]
            # print(f'В северодвинске сейчас {current_weather_description}')
            # print(f'В северодвинске сейчас {current_temp:.1f} °C, но ощущается как {current_temp_feels_like:.1f} °C')
            # print(f'Влажность {current_humidity} %')
            # print(f'Скорость ветра {current_wind_speed} м/с')
            # print(f'Облачность {current_clouds_percent} %')
            break
        except requests.exceptions.Timeout:
            print(f'Ошибка таймаута при {i+1} попытке из {attempts}')
        except Exception as e:
            print(f'Ошибка: {e}')
    else:
        print(f'Не удалось получить данные после {attempts} попыток')


def get_5day_forecast(lat_city, lon_city):
    url = f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={OPENWEATHER_TOKEN}&units=metric&lang=ru'
    forecast_by_day = {}
    attempts = 3
    print(url)
    for i in range(attempts):
        try:
            data = requests.get(url, timeout=0.2).json()
            population = data['city']['population']
            sunrise = datetime.fromtimestamp(data['city']['sunrise'])
            print(f'Восход солнца {sunrise}')
            sunset = datetime.fromtimestamp(data['city']['sunset'])
            print(f'Закат солнца {sunset}')
            print(f'Популяция города/села {population} чел.')
            # for i in data['list']:
            #     print(datetime.fromtimestamp(i['dt']), '__', (i['main']['temp']), '__', i['weather'][0]['description'])
            # break
            for forecast in data['list']:
                date = datetime.fromtimestamp(forecast['dt']).date()
                if date not in forecast_by_day:
                    forecast_by_day[date] = []
                forecast_by_day[date].append(forecast)
            #print(forecast_by_day.items())
            for date, forecasts in forecast_by_day.items():
                print(f'Дата: {date}')
                #print(forecasts)
                for forecast in forecasts:
                    print(f'В {datetime.fromtimestamp(forecast["dt"]).strftime("%H:%M")} часов Температура будет: {forecast["main"]["temp"]}, но ощущаться будет как {forecast["main"]["feels_like"]}')
            break

        except requests.exceptions.Timeout:
            print(f'Ошибка таймаута при {i + 1} попытке из {attempts}')
        except Exception as e:
            print(f'Ошибка: {e}')
    else:
        print(f'Не удалось получить данные после {attempts} попыток')




lat, lon = get_lat_lon_city('Северодвинск')
#get_current_weather(lat, lon)
get_5day_forecast(lat, lon)