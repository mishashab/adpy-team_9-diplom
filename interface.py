import random

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from token_id import bot_token

vk = vk_api.VkApi(token=bot_token)
longpoll = VkLongPoll(vk)


def create_keyboard(response):
    keyboard = VkKeyboard(one_time=True)

    if response in ['привет', 'хай', 'Привет', 'Начать', 'К подбору']:
        keyboard.add_button('Подобрать пару', color=VkKeyboardColor.POSITIVE)

    elif response in ['Подобрать пару', 'Вернуться к подбору', 'Дизлайк',
                      'Продолжить подбор']:
        keyboard.add_button('Лайк', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('Дизлайк', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button('Продолжить подбор')
        keyboard.add_line()
        keyboard.add_button('Закончить')

    elif response in ['Лайк', 'Получить фото', 'Написать']:
        keyboard.add_button('Получить фото', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('Написать', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Вернуться к подбору')

    elif response == 'Закончить':
        keyboard.add_button('Пока, бро!')
        keyboard.add_line()
        keyboard.add_button('К подбору')

    elif response == 'Пока, бро!':
        keyboard.add_button('Привет')

    else:
        keyboard.add_button('Начать подбор', color=VkKeyboardColor.POSITIVE)

    keyboard = keyboard.get_keyboard()
    return keyboard


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message,
                                'random_id': random.randrange(10 ** 7),
                                'keyboard': keyboard})


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            request = event.text
            keyboard = create_keyboard(request)
            if request in ['привет', 'хай', 'Привет', 'Начать']:
                write_msg(event.user_id, f"Хай, {event.user_id}")
            elif request in ['Подобрать пару', 'К подбору']:
                write_msg(event.user_id,
                          f"Начинаю подбор")
            elif request in ['Вернуться к подбору', 'Далее',
                             'Продолжить подбор']:
                write_msg(event.user_id,
                          f"Продолжаю подбор")
            elif request == 'Лайк':
                write_msg(event.user_id,
                          f"Выберите действие")
            elif request == 'Написать':
                write_msg(event.user_id,
                          f"Перевожу в лс")
            elif request == 'Получить фото':
                write_msg(event.user_id,
                          f"Лови")
            elif request == 'Вернуться к подбору':
                write_msg(event.user_id,
                          f"Продолжаю подбор")
            elif request == 'Закончить':
                write_msg(event.user_id,
                          f"Подбор окончен")
            elif request == 'Дизлайк':
                write_msg(event.user_id,
                          f"больше не появится в подборе")
            elif request == 'Пока, бро!':
                write_msg(event.user_id,
                          f"Сладких котёнок")
            else:
                write_msg(event.user_id,
                          f"Сообщение не распознано")
