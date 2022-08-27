import random
from dotenv import load_dotenv
import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import os
import redis
from utils import get_random_question, answer_shortening

load_dotenv()
r = redis.Redis(
    host=os.getenv('REDIS_HOST'),
    port=os.getenv('REDIS_PORT'),
    username=os.getenv('REDIS_USERNAME'),
    password=os.getenv('REDIS_PASSWORD'),
    decode_responses=True
)


def start(event, vk_api, keyboard):
    vk_api.messages.send(
        user_id=event.user_id,
        message=('Добро пожаловать на викторину!'
                 ' Нажмите "Новый Вопрос"'),
        random_id=random.randint(1, 1000),
        keyboard=keyboard.get_keyboard()
    )


def handle_new_question_request(event, vk_api, keyboard):
    q_a = get_random_question()
    question = q_a['question']
    answer = q_a['answer']
    answer_shorted = answer_shortening(answer)
    r.set(event.user_id, answer_shorted)
    vk_api.messages.send(
        user_id=event.user_id,
        message=question,
        random_id=random.randint(1, 1000),
        keyboard=keyboard.get_keyboard()
    )


def handle_solution_attempt(event, vk_api, user_response):
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


def handle_give_up(event, vk_api, keyboard):
    answer = r.get(event.user_id)
    vk_api.messages.send(
        user_id=event.user_id,
        message=f'Ответ: {answer}',
        random_id=random.randint(1, 1000),
        keyboard=keyboard.get_keyboard()
    )


if __name__ == "__main__":
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
                handle_new_question_request(event, vk_api, keyboard)
            elif event.text.lower() == 'сдаться':
                handle_give_up(event, vk_api, keyboard)
            else:
                handle_solution_attempt(event, vk_api, event.text.lower())
