from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
import logging
from config import YOU_TELEGRAM_TOKEN
import database
from weather import get_lat_lon_city, get_5day_forecast, get_current_weather, forecast_dates
from datetime import datetime, date, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=YOU_TELEGRAM_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# Create a connection to the database
conn = database.create_connection()

# Create the table if it doesn't exist
database.create_table(conn)


class Form(StatesGroup):
    city_add = State()  # Will be used to save user's city
    city_delete = State()  # Will be used to delete user's city


def create_back_button():
    inline_keyboard = types.InlineKeyboardMarkup()
    back_button = types.InlineKeyboardButton('⏪ Go back', callback_data='go_back_button')
    inline_keyboard.add(back_button)
    return inline_keyboard


def create_start_inline_keyboard(user_id):
    inline_keyboard = types.InlineKeyboardMarkup()
    button_another_city = types.InlineKeyboardButton('🔎 Добавить город в список', callback_data='add_another_city')
    button_delete_city = types.InlineKeyboardButton('❌ Удалить город', callback_data='delete_city')
    user_cities = database.get_user_cities(conn, user_id)
    buttons = []
    for city in user_cities:
        button_city = types.InlineKeyboardButton(city, callback_data=f'city_{city}')
        buttons.append(button_city)
        if len(buttons) == 3:
            inline_keyboard.row(*buttons)
            buttons = []
    if buttons:
        inline_keyboard.row(*buttons)
    inline_keyboard.add(button_another_city)
    inline_keyboard.add(button_delete_city)
    return inline_keyboard


def create_delete_inline_keyboard(user_id):
    inline_keyboard = types.InlineKeyboardMarkup()
    user_cities = database.get_user_cities(conn, user_id)
    buttons = []
    for city in user_cities:
        button_city = types.InlineKeyboardButton(city, callback_data=f'city_{city}')
        buttons.append(button_city)
        if len(buttons) == 3:
            inline_keyboard.row(*buttons)
            buttons = []
    if buttons:
        inline_keyboard.row(*buttons)
    back_button = types.InlineKeyboardButton('⏪ Go back', callback_data='go_back_button')
    inline_keyboard.add(back_button)
    return inline_keyboard


def create_days_info_buttons():
    inline_keyboard = types.InlineKeyboardMarkup()
    button_current_weather = types.InlineKeyboardButton('Текущая погода (прямо сейчас)', callback_data='current_weather_button')
    button_current_day_weather = types.InlineKeyboardButton('Погода не текущий день', callback_data='current_weather_day_button')
    inline_keyboard.add(button_current_weather)
    inline_keyboard.add((button_current_day_weather))
    buttons = [] #список для хранения кнопок
    for i in range(1,5):
        day = datetime.now() + timedelta(days=i)
        button_day = types.InlineKeyboardButton(f'На {day.strftime("%d.%m")}', callback_data=f'weather_{day.strftime("%Y-%m-%d")}')
        buttons.append(button_day)
        if len(buttons) == 2:
            inline_keyboard.row(*buttons)
            buttons = []
    if buttons:
        inline_keyboard.row(*buttons)
    back_button = types.InlineKeyboardButton('⏪ Go back', callback_data='go_back_button')
    inline_keyboard.add(back_button)
    return inline_keyboard


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    database.insert_user(conn, message.from_user.id, message.from_user.username)
    await message.reply("Привет!\nЯ бот, который сообщает прогноз погоды, либо дает инфорамцию по выбранному городу",
                        reply_markup=create_start_inline_keyboard(message.from_user.id))


@dp.callback_query_handler(lambda call: call.data.startswith('city_'))  # Создание меню при выборе города, какую дату смотреть, инфа и т.п
async def callback_check_info_city(callback_query: types.CallbackQuery, state: FSMContext):
    print(callback_query.data)
    city_name = callback_query.data[5:]
    lat, lon = get_lat_lon_city(city_name)
    population, sunrise, sunset = get_5day_forecast(lat_city=lat, lon_city=lon, forecast_date=date.today())
    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text=f'***Популяция в городе {city_name}:***   {format(population, ",").replace(",", " ")} чел. \n'
                                f'***Восход солнца:***     {sunrise.strftime("%H:%M")}\n'
                                f'***Закат солнца:***      {sunset.strftime("%H:%M")}\n'
                                f'Какой прогноз погоды вас интересует? ',
                                reply_markup=create_days_info_buttons(),
                                parse_mode='Markdown')
    await state.update_data(current_city=city_name, current_lat=lat, current_lon=lon)  # записываем какой город выбрали


@dp.callback_query_handler(lambda call: call.data == 'current_weather_button' or call.data.startswith('weather_'))  # обработка кнопки текущей погоды у определенного города
async def callback_current_city_info(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    city_name = data.get('current_city')
    lat = data.get('current_lat')
    lon = data.get('current_lon')
    if callback_query.data == 'current_weather_button':
        current_weather = get_current_weather(lat, lon)
        await bot.send_message(chat_id=callback_query.message.chat.id,
                               text=f'***В {city_name} сейчас*** {current_weather.temp:.1f} °C, ***но '
                                    f'ощущается как ***{current_weather.temps_feels_like:.1f}°C '
                                    f'***Скорость ветра*** {current_weather.wind_speed} м/c, ***влажность*** {current_weather.humidity}%, '
                                    f'***облачность*** {current_weather.clouds} %\n'
                                    f'Можете посмотреть еще погоду, либо вернуться в меню',
                               reply_markup=create_days_info_buttons(),
                               parse_mode='Markdown')
    if callback_query.data.startswith('weather_'):
        data_day = callback_query.data[8:]
        print(data_day)
        #get_5day_forecast(lat)
        print(get_5day_forecast(lat, lon, data_day))

@dp.callback_query_handler(lambda call: call.data == 'go_back_button',)  # обработка кнопки назад
async def callback_back_button(callback_query: types.CallbackQuery, state: FSMContext):

    await bot.send_message(chat_id=callback_query.message.chat.id,
                           text='Вы вернулись в меню.\nВыберите город',
                           reply_markup=create_start_inline_keyboard(callback_query.from_user.id))
    await state.finish()

@dp.callback_query_handler(lambda call: call.data == 'go_back_button', state=[Form.city_delete, Form.city_add])  # обработка кнопки назад
async def callback_back_button(callback_query: types.CallbackQuery, state: FSMContext):
    print(callback_query.data)
    current_state = await state.get_state()
    if current_state == Form.city_delete.state:
        await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    text='Понял, удалять город не будем.\nДержи менюшку:',
                                    reply_markup=create_start_inline_keyboard(callback_query.from_user.id))
    elif current_state == Form.city_add.state:
        await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    text='Понял, добавлять город не будем.\nДержи менюшку:',
                                    reply_markup=create_start_inline_keyboard(callback_query.from_user.id))
    await state.finish()


@dp.callback_query_handler(lambda call: call.data == 'add_another_city')  # Введение города при добавлении
async def callback_add_city(callback_query: types.CallbackQuery):
    print(callback_query.data)
    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text='Введите название города, который хотите добавить:',
                                reply_markup=create_back_button())
    await Form.city_add.set()


@dp.callback_query_handler(lambda call: call.data == 'delete_city')  # Выбор удаления города
async def callback_delete_city(callback_query: types.CallbackQuery):
    print(callback_query.data)
    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text='Нажмите на город из этого списка чтобы удалить его:',
                                reply_markup=create_delete_inline_keyboard(callback_query.from_user.id))
    await Form.city_delete.set()


@dp.callback_query_handler(lambda call: call.data.startswith('city_'),
                           state=Form.city_delete)  # удаление города по клику
async def delete_city(callback_query: types.CallbackQuery, state: FSMContext):
    city_name = callback_query.data[5:]  # вырезаем только название города
    user_id = callback_query.from_user.id
    city_id = database.get_city_id(conn, city_name)
    database.delete_selected_city_from_user(conn, user_id, city_id)  # удаление города у юзера в бд
    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text=f'Вы успешно удалили город {city_name}\nМожете пользоваться ботом дальше.',
                                reply_markup=create_start_inline_keyboard(callback_query.from_user.id))
    await state.finish()


@dp.message_handler(state=Form.city_add)  # добавление города в список
async def add_city(message: types.Message, state: FSMContext):
    city_name = message.text
    user_id = message.from_user.id
    if get_lat_lon_city(
            message.text) == None:  # Если запрос города что-то вернул (если существует), тогда записываем в БД.
        await bot.send_message(message.chat.id, 'Такого города не существует')
    else:
        if not database.check_city_exists(conn, city_name):  # Если в БД нет такого города
            database.insert_city(conn, city_name)  # то добавляем
            city_id = database.get_city_id(conn, message.text)  # Добавили, теперь парсим его ID
            database.insert_selected_city_by_user(conn, user_id, city_id)  # Присваиваем город юзеру
        else:
            city_id = database.get_city_id(conn, message.text)  # Если такой город есть, то парсим его ID
            database.insert_selected_city_by_user(conn, user_id, city_id)  # Присваиваем город юзеру
    await bot.send_message(message.chat.id,
                           f'Вы добавили новый город: {message.text}\nВыберите, где хотите посмотреть погоду.',
                           reply_markup=create_start_inline_keyboard(user_id))
    await state.finish()


@dp.message_handler()
async def echo(message: types.Message):
    # old style:
    # await bot.send_message(message.chat.id, message.text)
    await bot.send_message(message.chat.id, message.text)
    await message.answer(message.text)
