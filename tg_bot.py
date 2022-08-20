from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
import redis
import logging
from dotenv import load_dotenv
import os
import json
import random

load_dotenv()
r = redis.Redis(
    host=os.getenv('REDIS_HOST'),
    port=os.getenv('REDIS_PORT'),
    username=os.getenv('REDIS_USERNAME'),
    password=os.getenv('REDIS_PASSWORD'),
    decode_responses=True
)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def start(bot, update):
    custom_keyboard = [['Новый вопрос', 'Сдаться'],
                       ['Мой счет']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)

    update.message.reply_text('Hello!', reply_markup=reply_markup)


def get_random_question(file):
    with open(file) as f:
        dictdump = json.loads(f.read())
        question, _ = list(dictdump.items())[random.randint(0, 100)]
        return question


def dull(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('it is Dull!')


def echo(bot, update):
    """Echo the user message."""
    tg_login = update['message']['chat']['username']
    if update.message.text == 'Новый вопрос':
        question = get_random_question('questions.json')
        r.set(tg_login, question)
        update.message.reply_text(question)
        print('Read from Redis: ', r.get(tg_login))
    else:
        update.message.reply_text(update.message.text)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():

    updater = Updater(os.getenv('TG_TOKEN'))
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("dull", dull))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
