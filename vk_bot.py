import random
from dotenv import load_dotenv
import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import os
import redis
from questions_utils import get_random_question, shorten_answer, \
    get_questions
import logging

logger = logging.getLogger(__name__)


def start(event, vk_api, keyboard):
    vk_api.messages.send(
        user_id=event.user_id,
        message=('Добро пожаловать на викторину!'
                 ' Нажмите "Новый Вопрос"'),
        random_id=random.randint(1, 1000),
        keyboard=keyboard.get_keyboard()
    )


def handle_question_request(event, vk_api, keyboard, questions, r):
    q_a = get_random_question(questions)
    question = q_a['question']
    answer = q_a['answer']
    short_answer = shorten_answer(answer)
    r.set(event.user_id, short_answer)
    vk_api.messages.send(
        user_id=event.user_id,
        message=question,
        random_id=random.randint(1, 1000),
        keyboard=keyboard.get_keyboard()
    )


def handle_solution_attempt(event, vk_api, keyboard, user_response, r):
    answer = r.get(event.user_id)
    if user_response.lower() == answer.lower():
        vk_api.messages.send(
            user_id=event.user_id,
            message=('Правильно! Поздравляю! '
                     'Для следующего вопроса нажми «Новый вопрос»'),
            random_id=random.randint(1, 1000),
            keyboard=keyboard.get_keyboard()
        )
    else:
        vk_api.messages.send(
            user_id=event.user_id,
            message=('Хмм.. Не верный ответ или команда'
                     ' Для начала, введите "Привет"'),
            random_id=random.randint(1, 1000),
            keyboard=keyboard.get_keyboard()
        )


def handle_give_up(event, vk_api, keyboard, r):
    answer = r.get(event.user_id)
    vk_api.messages.send(
        user_id=event.user_id,
        message=f'Ответ: {answer}',
        random_id=random.randint(1, 1000),
        keyboard=keyboard.get_keyboard()
    )


def main():
    logger.info('VK bot is running.')
    r = redis.Redis(
        host=os.getenv('REDIS_HOST'),
        port=os.getenv('REDIS_PORT'),
        username=os.getenv('REDIS_USERNAME'),
        password=os.getenv('REDIS_PASSWORD'),
        decode_responses=True
    )

    questions = get_questions(os.getenv('JSON_FILE'))
    vk_session = vk.VkApi(token=os.getenv('VK_TOKEN'))
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text.lower() == 'привет':
                start(event, vk_api, keyboard)
            elif event.text.lower() == 'новый вопрос':
                handle_question_request(
                    event, vk_api, keyboard, questions, r)
            elif event.text.lower() == 'сдаться':
                handle_give_up(event, vk_api, keyboard, r)
            else:
                handle_solution_attempt(
                    event, vk_api, keyboard, event.text.lower(), r
                )


if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    load_dotenv()
    main()
