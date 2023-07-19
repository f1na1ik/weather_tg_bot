import datetime
from datetime import datetime, date, timedelta

import requests
from config import OPENWEATHER_TOKEN
from pytemperature import k2c

class CurrentWeatherData:
    def __init__(self, description, temp, temps_feels_like, humidity, wind_speed, clouds):
        self.description = description
        self.temp = temp
        self.temps_feels_like = temps_feels_like
        self.humidity = humidity
        self.wind_speed = wind_speed
        self.clouds = clouds

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
            print(f'Ошибка таймаута, при попытке {attempt+1} / {city_name}')
            attempt += 1
        except Exception as e:
            print(f'Ошибка {e} / {city_name}')
            break
    else:
        print('Не удалось получить данные')


def get_current_weather(lat_city, lon_city):
    url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat_city}&lon={lon_city}&appid={OPENWEATHER_TOKEN}&lang=ru'
    attempts = 10

    for i in range(attempts):
        try:
            print(url)
            data = requests.get(url, timeout=0.2).json()
            #print(data)
            current_weather_description = data["weather"][0]["description"]
            current_temp = k2c(data['main']['temp'])
            current_temp_feels_like = k2c(data['main']['feels_like'])
            current_humidity = data["main"]["humidity"]
            current_wind_speed = data["wind"]["speed"]
            current_clouds_percent = data["clouds"]["all"]
            return CurrentWeatherData(current_weather_description, current_temp, current_temp_feels_like, current_humidity, current_wind_speed, current_clouds_percent)
            break
        except requests.exceptions.Timeout:
            print(f'Ошибка таймаута при {i+1} попытке из {attempts}')
        except Exception as e:
            print(f'Ошибка: {e}')
    else:
        print(f'Не удалось получить данные после {attempts} попыток')


forecast_dates = [date.today() + timedelta(days=i) for i in range(5)] #переменная для выбора погоды в боте
def get_5day_forecast(lat_city, lon_city, forecast_date):
    url = f'https://api.openweathermap.org/data/2.5/forecast?lat={lat_city}&lon={lon_city}&appid={OPENWEATHER_TOKEN}&units=metric&lang=ru'
    forecast_by_day = {}
    attempts = 10
    print(url)
    for i in range(attempts):
        try:
            data = requests.get(url, timeout=0.2).json()
            population = data['city']['population']
            sunrise = datetime.fromtimestamp(data['city']['sunrise'])
            sunset = datetime.fromtimestamp(data['city']['sunset'])
            for forecast in data['list']:
                date = datetime.fromtimestamp(forecast['dt']).date()
                if date not in forecast_by_day:
                    forecast_by_day[date] = []
                forecast_by_day[date].append(forecast)
            for date, forecasts in forecast_by_day.items():
                if date == forecast_date:
                    print(f'Дата: {date}')
                    #print(forecasts)
                    for forecast in forecasts:
                        date_forecast = forecast["dt"]
                        weather_description = forecast["weather"][0]["description"]
                        temp = forecast['main']['temp']
                        temp_feels_like = forecast['main']['feels_like']
                        humidity = forecast["main"]["humidity"]
                        wind_speed = forecast["wind"]["speed"]
                        clouds_percent = forecast["clouds"]["all"]
                        print(f'В {datetime.fromtimestamp(date_forecast).strftime("%H:%M")} Температура будет: {temp} °C, но ощущаться будет как {temp_feels_like} °C')
            return population, sunrise, sunset
            break

        except requests.exceptions.Timeout:
            print(f'Ошибка таймаута при {i + 1} попытке из {attempts}')
        except Exception as e:
            print(f'Ошибка: {e}')
    else:
        print(f'Не удалось получить данные после {attempts} попыток')




#lat, lon = get_lat_lon_city('Северодвинск')
#get_current_weather(lat, lon)
#get_5day_forecast(lat, lon, date.today() + timedelta(1))
#print(date.today() + timedelta(1))