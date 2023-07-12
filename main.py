from bot import get_bot
from config import YOU_TELEGRAM_TOKEN


if __name__ == '__main__':
    bot = get_bot(YOU_TELEGRAM_TOKEN)
    bot.run_polling()

