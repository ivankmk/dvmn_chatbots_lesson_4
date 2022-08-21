from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
import redis
import logging
from dotenv import load_dotenv
import os
import json
import random
from utils import question_cleaner, get_random_question

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


def user_action(bot, update):
    """Echo the user message."""
    tg_login = update['message']['chat']['username']
    if update.message.text == 'Новый вопрос':
        q_a = get_random_question()
        question = q_a['question']
        answer = q_a['answer']
        answer_shorted = answer.split('.')[0] or answer.split('(')[0]
        update.message.reply_text(question)
        r.set(tg_login, answer_shorted)
        print(answer)

    else:
        if update.message.text.lower() == r.get(tg_login).lower():

            update.message.reply_text(
                'Правильно! Поздравляю! '
                'Для следующего вопроса нажми «Новый вопрос»”')
        else:
            update.message.reply_text('Неправильно… Попробуете ещё раз?')


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():

    updater = Updater(os.getenv('TG_TOKEN'))
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, user_action))

    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
