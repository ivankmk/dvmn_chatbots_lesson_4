from telegram.ext import Updater, MessageHandler, Filters, \
    CommandHandler, ConversationHandler, RegexHandler
from telegram import ReplyKeyboardMarkup
import redis
import logging
from dotenv import load_dotenv
import os
from questions_utils import get_random_question, get_questions
from enum import Enum, auto
from functools import partial

logger = logging.getLogger(__name__)


class BotStates(Enum):
    NEW_QUESTION_REQUEST = auto()
    SOLUTION_ATTEMPT = auto()


def start(bot, update):
    custom_keyboard = [['Новый вопрос', 'Сдаться']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)

    update.message.reply_text(
        'Добро пожаловать на викторину!',
        reply_markup=reply_markup
    )

    return BotStates.NEW_QUESTION_REQUEST


def handle_question_request(bot, update, questions, r):
    tg_login = update['message']['chat']['username']
    q_a = get_random_question(questions)
    question = q_a['question']
    answer = q_a['answer']
    short_answer = answer.split('.')[0] or answer.split('(')[0]
    update.message.reply_text(question)
    r.set(tg_login, short_answer)
    return BotStates.SOLUTION_ATTEMPT


def handle_solution_attempt(bot, update, r):
    tg_login = update['message']['chat']['username']
    answer = r.get(tg_login)
    if update.message.text.lower() == answer.lower():
        update.message.reply_text(
            'Правильно! Поздравляю! '
            'Для следующего вопроса нажми «Новый вопрос»')

    else:
        update.message.reply_text('Неправильно… Попробуете ещё раз?')
        return BotStates.NEW_QUESTION_REQUEST


def handle_give_up(bot, update, r):
    tg_login = update['message']['chat']['username']
    answer = r.get(tg_login)
    update.message.reply_text(f'Ответ: {answer}')
    return BotStates.NEW_QUESTION_REQUEST


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def cancel(bot, update):
    update.message.reply_text('Пока!')
    return ConversationHandler.END


def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    load_dotenv()
    logger.info('TG bot is running.')
    r = redis.Redis(
        host=os.getenv('REDIS_HOST'),
        port=os.getenv('REDIS_PORT'),
        username=os.getenv('REDIS_USERNAME'),
        password=os.getenv('REDIS_PASSWORD'),
        decode_responses=True
    )

    questions = get_questions(os.getenv('JSON_FILE'))
    updater = Updater(os.getenv('TG_TOKEN'))
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            BotStates.NEW_QUESTION_REQUEST: [
                RegexHandler('^Новый вопрос',
                             partial(handle_question_request,
                                     questions=questions,
                                     r=r)
                             )
            ],

            BotStates.SOLUTION_ATTEMPT: [
                RegexHandler('^Новый вопрос',
                             partial(handle_question_request,
                                     questions=questions,
                                     r=r)),
                RegexHandler('^Сдаться', partial(handle_give_up, r=r)),
                MessageHandler(Filters.text, partial(handle_solution_attempt,
                                                     r=r))],

        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
