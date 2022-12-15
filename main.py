from token_id import bot_token, user_token
from VKinder.VKinder import VKinder
from VKinder import DB

from datetime import date
import time
import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
import psycopg2


def create_keyboard(response):
    """Создание клавиатуры"""
    keyboard = VkKeyboard(one_time=True)
    if response in ['привет', 'хай', 'Привет', 'К подбору']:
        keyboard.add_button('Заполнить базу')
        keyboard.add_line()
        keyboard.add_button('Просмотреть избранное',
                            color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Просмотреть анкеты',
                            color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Закончить')
    elif response in ['Заполнить базу']:
        keyboard.add_button('Просмотреть избранное',
                            color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Просмотреть анкеты',
                            color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Закончить')
    elif response in ['Просмотреть избранное']:
        keyboard.add_button('Просмотреть анкеты',
                            color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Закончить')
    elif response in ['Просмотреть анкеты', 'Вернуться к подбору', 'Дизлайк',
                      'Продолжить подбор', 'В избранное', 'Начать подбор']:
        keyboard.add_button('В избранное', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('В ЧС', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button('Продолжить подбор')
        keyboard.add_line()
        keyboard.add_button('Закончить')

    elif response in ['Лайк', 'Получить фото', 'Написать']:
        keyboard.add_button('Вернуться к подбору')
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


def write_message(authorize, sender, message, keyboard, attachment=''):
    authorize.method('messages.send', {'user_id': sender,
                                       'message': message,
                                       "random_id": get_random_id(),
                                       'attachment': attachment,
                                       'keyboard': keyboard})


def calculate_age(born):
    born = born.split(".")
    today = date.today()
    return today.year - int(born[2]) - (
            (today.month, today.day) < (int(born[1]), int(born[0])))


def get_str(url_photos):
    """Собираем из списка tuple строку для бота"""
    str_photo = ''
    for item in url_photos:
        if not str_photo:
            str_photo = item[0]
        else:
            str_photo += f',{item[0]}'
    return str_photo


def data_conversion(db_source, cur):
    """Преобразует данные из базы данных в нужный для бота вид"""
    users = list()
    for item in db_source:
        users.append({'id': item[0],
                      'name': f'{item[1]} {item[2]}',
                      'url': item[3],
                      'attachment': get_str(DB.get_photo(cur, item[0]))})
    return users


def get_find_user(cur, authorize, result, counter, sender_id, v_kinder, keyboard):
    '''Выводим найденных пользователей'''
    flag = True
    while flag and counter < len(result):
        if not DB.check_find_user(cur, sender_id, result[counter]['id']) and not result[counter]['is_closed']:
            flag = False
            result[counter]['attachment'] = v_kinder.find_photo(result[counter]['id'])
            write_message(authorize,
                          sender_id,
                          f"{result[counter]['first_name']} {result[counter]['last_name']}\n"
                          f"https://vk.com/id{result[counter]['id']}",
                          keyboard,
                          ','.join(result[counter]['attachment']))
            counter += 1
        else:
            counter += 1

        if counter >= len(result):
            write_message(authorize, sender_id,
                          'Мы посмотрели всё! Заново?',
                          keyboard)
            counter = 0
    return counter


def connection():
    authorize = vk_api.VkApi(token=bot_token)
    longpoll = VkLongPoll(authorize)

    user_session = vk_api.VkApi(token=user_token)
    session = user_session.get_api()

    return longpoll, session, authorize


def main():
    print("Hi bot")

    longpoll, session, authorize = connection()

    conn = psycopg2.connect(database="course_w", user="postgres",
                            password="netologyAL")
    with conn.cursor() as cur:
        # print(DB.drop_table(cur)) #если нужно сбросить БД
        print(DB.create_db(cur))

        counter = 0
        ask_user = dict()
        result = dict()
        flag = True
        while flag:
            try:
                for event in longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me \
                            and event.text:
                        received_message = event.text
                        msg_keyboard = create_keyboard(event.text)
                        sender_id = event.user_id

                        if not DB.get_ask_user_data(cur, sender_id):
                            print('ask_user в базе отсутствует')
                            user_info = session.account.getProfileInfo(
                                user_id=sender_id)
                            user_info['age'] = calculate_age(user_info['bdate'])
                            if user_info['sex'] == 2:
                                user_info['gender'] = 'Мужской'
                            elif user_info['sex'] == 1:
                                user_info['gender'] = 'Женский'
                            else:
                                user_info['gender'] = 'Пол не указан'

                            if DB.add_ask_user(cur, user_info['id'],
                                               user_info['first_name'],
                                               user_info['last_name'],
                                               user_info['age'],
                                               user_info['home_town'],
                                               user_info['city']['id'],
                                               user_info['gender']):
                                conn.commit()
                                print('ask_user добавлен в базу')
                            else:
                                print('ask_user НЕ добавлен в базу')

                        if received_message.lower() in ['привет',
                                                        'хай',
                                                        'Привет',
                                                        'Начать',
                                                        'К подбору']:
                            print(
                                f'Пользователь = '
                                f'{DB.get_ask_user_data(cur, sender_id)}')

                            ask_user = DB.get_ask_user_data(cur, sender_id)
                            write_message(authorize,
                                          sender_id,
                                          f"Доброго времени суток, "
                                          f"{ask_user[1]}!\nВаши параметры:\n"
                                          f"Город: {ask_user[4]}\nПол: "
                                          f"{ask_user[6]}\nВозраст: "
                                          f"{ask_user[3]}\n",
                                          msg_keyboard)

                        elif received_message.lower() in ['просмотреть избранное',
                                                  'избранное']:
                            if DB.get_favourites(cur, sender_id):
                                db_source = DB.get_favourites(cur, sender_id)
                                favourites = data_conversion(db_source, cur)
                                for item in favourites:
                                    write_message(authorize,
                                                  sender_id,
                                                  f"{item['name']}\n"
                                                  f"{item['url']}",
                                                  msg_keyboard,
                                                  item['attachment'])
                                write_message(authorize, sender_id,
                                              "Напоминаю о красоте.",
                                              msg_keyboard)
                            else:
                                write_message(authorize, sender_id,
                                              f"В избранном нет никого.",
                                              msg_keyboard)

                        elif received_message.lower() in ['ищем', 'поиск',
                                                          'выполнить',
                                                          'выполнить поиск',
                                                          'дальше']:
                            if not result:
                                v_kinder = VKinder(longpoll, session)
                                result = v_kinder.find_user(ask_user)
                            counter = get_find_user(cur,
                                                    authorize,
                                                    result,
                                                    counter,
                                                    sender_id,
                                                    v_kinder,
                                                    msg_keyboard)

                        elif received_message.lower() in ['в избранное',
                                                          'добавить в избранное']:

                            if DB.add_favourites(cur,
                                                 result[counter - 1]['id'],
                                                 sender_id,
                                                 result[counter - 1]['first_name'],
                                                 result[counter - 1]['last_name'],
                                                 f"https://vk.com/id{result[counter - 1]['id']}",
                                                 1):
                                for photo in result[counter - 1]['attachment']:
                                    if DB.add_find_users_photos(cur, result[counter - 1]['id'], photo):
                                        print(f"{photo} для user {result[counter - 1]['last_name']} успешно добавлено")
                                conn.commit()
                                print('Добавлено в избранное')
                                write_message(authorize,
                                              sender_id,
                                              "Тян на заметке",
                                              msg_keyboard)

                        elif received_message.lower() in ['в черный', 'чёрный',
                                                          'нет', 'в чс']:

                            if DB.add_favourites(cur,
                                                 result[counter - 1]['id'],
                                                 sender_id,
                                                 result[counter - 1]['first_name'],
                                                 result[counter - 1]['last_name'],
                                                 f"https://vk.com/id{result[counter - 1]['id']}",
                                                 0):
                                conn.commit()
                                print('Добавлено в чёрный список')
                                write_message(authorize,
                                              sender_id,
                                              "Больше не встретится)",
                                              msg_keyboard)
                        elif received_message == 'Закончить':
                            write_message(authorize,
                                          sender_id,
                                          f"Подбор окончен",
                                          msg_keyboard)
                        elif received_message == 'Пока, бро!':
                            write_message(authorize,
                                          sender_id,
                                          f"Сладких котёнок",
                                          msg_keyboard)
                        else:
                            write_message(authorize, sender_id,
                                          "Я вас не понимаю...",
                                          msg_keyboard)

            except Exception as exception:
                print(exception)
                time.sleep(5)
                if sender_id:
                    write_message(authorize, sender_id, "Бот на связи!",
                                  msg_keyboard)

    conn.close()


if __name__ == '__main__':
    main()
