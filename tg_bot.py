from telegram.ext import Updater, MessageHandler, Filters, \
    CommandHandler, ConversationHandler, RegexHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import redis
import logging
from dotenv import load_dotenv
import os
from utils import get_random_question
from enum import Enum, auto

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


class BotStates(Enum):
    NEW_QUESTION_REQUEST = auto()
    GIVE_UP = auto()
    MY_SCORE = auto()
    SOLUTION_ATTEMPT = auto()
    USER_COMMUNICATION = auto()


def start(bot, update):
    custom_keyboard = [['Новый вопрос', 'Сдаться'],
                       ['Мой счет']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)

    update.message.reply_text(
        'Добро пожаловать на викторину!', reply_markup=reply_markup)

    return BotStates.NEW_QUESTION_REQUEST


def handle_new_question_request(bot, update):
    """Echo the user message."""
    tg_login = update['message']['chat']['username']
    q_a = get_random_question()
    question = q_a['question']
    answer = q_a['answer']
    answer_shorted = answer.split('.')[0] or answer.split('(')[0]
    update.message.reply_text(question)
    r.set(tg_login, answer_shorted)
    print(answer)
    return BotStates.SOLUTION_ATTEMPT


def handle_solution_attempt(bot, update):
    tg_login = update['message']['chat']['username']
    if update.message.text.lower() == r.get(tg_login).lower():

        update.message.reply_text(
            'Правильно! Поздравляю! '
            'Для следующего вопроса нажми «Новый вопрос»”')
    else:
        update.message.reply_text('Неправильно… Попробуете ещё раз?')
        return NEW_QUESTION_REQUEST


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def main():

    updater = Updater(os.getenv('TG_TOKEN'))
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            BotStates.NEW_QUESTION_REQUEST: [
                RegexHandler('^(Новый вопрос)$', handle_new_question_request)],
            BotStates.SOLUTION_ATTEMPT: [
                MessageHandler(Filters.text, handle_solution_attempt)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
