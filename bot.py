from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import logging
from config import YOU_TELEGRAM_TOKEN

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=YOU_TELEGRAM_TOKEN)
dp = Dispatcher(bot)

# def create_start_inline_keyboard():
#     inline_keyboard = types.InlineKeyboardMarkup()
#     array_of_buttons = [types.InlineKeyboardButton(f'Button{i}', callback_data=f'button{i}') for i in range(5)]
#     inline_keyboard.add(*array_of_buttons)
#     return inline_keyboard

def create_start_inline_keyboard():
    inline_keyboard = types.InlineKeyboardMarkup()
    button_another_city = types.InlineKeyboardButton('Ввести любой другой город')
    


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Привет!\nЯ бот, который говорит прогноз погоды\nPowered by aiogram.", reply_markup=create_start_inline_keyboard())

@dp.message_handler()
async def echo(message: types.Message):
    # old style:
    # await bot.send_message(message.chat.id, message.text)
    await bot.send_message(message.chat.id, message.text)
    await message.answer(message.text)

