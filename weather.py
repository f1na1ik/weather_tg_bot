import requests
import time
from config import OPENWEATHER_TOKEN
from pytemperature import k2c

def get_lat_lon_city(city_name, max_attempts = 10):
    url = f'http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit={1}&appid={OPENWEATHER_TOKEN}'
    attempt = 0
    while attempt < max_attempts:
        try:
            # start_time = time.time()
            data = requests.get(url, timeout=0.1).json()
            # end_time = time.time()
            # request_time = end_time - start_time

            #print(f'Запрос происходил {request_time}')
            # print(url)
            # print(data)

            lat = data[0]['lat']
            lon = data[0]['lon']
            return lat, lon
        except requests.exceptions.Timeout:
            print('Ошибка таймаута')
            attempt += 1
        except Exception as e:
            print(f'Ошибка {e}')
            break
    else:
        print('Не удалось получить данные')


def get_weather_lat_lon(lat_city, lon_city):
    url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_TOKEN}&lang=ru'
    print(url)
    data = requests.get(url, timeout=0.2).json()
    print(data)

    print(f'В северодвинске сейчас {data["weather"][0]["description"]}')

    temp_kelvin = data['main']['temp']
    temp_feels_like_kelvin = data['main']['feels_like']
    print(f'В северодвинске сейчас {k2c(temp_kelvin):.0f} °C, но ощущается как {k2c(temp_feels_like_kelvin):.0f} °C')

    print(f'Влажность {data["main"]["humidity"]} %')
    print(f'Скорость ветра {data["wind"]["speed"]} м/с')
    print(f'Облачность {data["clouds"]["all"]}%')







lat, lon = get_lat_lon_city('Холмогоры')
get_weather_lat_lon(lat, lon)