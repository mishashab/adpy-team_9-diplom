from DB.token_id import bot_token, user_token
from VKinder.VKinder import VKinder
import DB
from keyboard import CreateKeyboard

from datetime import date
import time
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id


def write_message(authorize, sender, message, keyboard='', attachment=''):
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


def data_conversion(db_source):
    """Преобразует данные из базы данных в нужный для бота вид"""
    users = list()
    for item in db_source:
        users.append({'id': item[0],
                      'name': f'{item[1]} {item[2]}',
                      'url': item[3],
                      'attachment': get_str(DB.get_photo(item[0]))})
    return users


def get_find_user(authorize, result, counter, sender_id, v_kinder, keyboard):
    '''Выводим найденных пользователей'''
    flag = True
    while flag and counter < len(result):
        if not DB.check_find_user(sender_id, result[counter]['id']) and not result[counter]['is_closed']:
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

    # print(DB.drop_table()) #если нужно сбросить БД
    print(DB.create_db())

    counter = 0
    ask_user = dict()
    result = dict()
    flag = True
    sender_id = 0
    create_k = CreateKeyboard()
    while flag:
        try:
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me \
                        and event.text:
                    received_message = event.text
                    # msg_keyboard = create_keyboard(event.text.lower())
                    sender_id = event.user_id

                    if not DB.get_ask_user_data(sender_id):
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

                        if DB.add_ask_user(user_info['id'],
                                           user_info['first_name'],
                                           user_info['last_name'],
                                           user_info['age'],
                                           user_info['home_town'],
                                           user_info['city']['id'],
                                           user_info['gender']):
                            print('ask_user добавлен в базу')
                        else:
                            print('ask_user НЕ добавлен в базу')

                    if received_message.lower() in ['привет',
                                                    'хай',
                                                    'Привет',
                                                    'начать',
                                                    'к подбору']:
                        print(
                            f'Пользователь = '
                            f'{DB.get_ask_user_data(sender_id)}')

                        ask_user = DB.get_ask_user_data(sender_id)
                        write_message(authorize,
                                      sender_id,
                                      f"Доброго времени суток, "
                                      f"{ask_user[1]}!\nВаши параметры:\n"
                                      f"Город: {ask_user[4]}\nПол: "
                                      f"{ask_user[6]}\nВозраст: "
                                      f"{ask_user[3]}\n",
                                      create_k.hi())

                    elif received_message.lower() in ['просмотреть избранное',
                                              'избранное']:
                        if DB.get_favourites(sender_id):
                            db_source = DB.get_favourites(sender_id)
                            favourites = data_conversion(db_source)
                            for item in favourites:
                                write_message(authorize,
                                              sender_id,
                                              f"{item['name']}\n"
                                              f"{item['url']}",
                                              '',
                                              item['attachment'])
                            write_message(authorize, sender_id,
                                          "Напоминаю о красоте.",
                                          create_k.view())
                        else:
                            write_message(authorize, sender_id,
                                          f"В избранном нет никого.",
                                          create_k.view())

                    elif received_message.lower() in ['ищем', 'поиск',
                                                      'выполнить',
                                                      'выполнить поиск',
                                                      'дальше']:
                        v_kinder = VKinder(longpoll, session)
                        if not result:
                            result = v_kinder.find_user(ask_user)
                        counter = get_find_user(authorize,
                                                result,
                                                counter,
                                                sender_id,
                                                v_kinder,
                                                create_k.search())

                    elif received_message.lower() in ['в избранное',
                                                      'добавить в избранное']:

                        if DB.add_favourites(result[counter - 1]['id'],
                                             sender_id,
                                             result[counter - 1]['first_name'],
                                             result[counter - 1]['last_name'],
                                             f"https://vk.com/id{result[counter - 1]['id']}",
                                             1):
                            for photo in result[counter - 1]['attachment']:
                                if DB.add_find_users_photos(result[counter - 1]['id'], photo):
                                    print(f"{photo} для user {result[counter - 1]['last_name']} успешно добавлено")
                            print('Добавлено в избранное')
                            write_message(authorize,
                                          sender_id,
                                          "Тян на заметке",
                                          create_k.favorite())

                    elif received_message.lower() in ['в черный', 'чёрный',
                                                      'нет', 'в чс']:

                        if DB.add_favourites(result[counter - 1]['id'],
                                             sender_id,
                                             result[counter - 1]['first_name'],
                                             result[counter - 1]['last_name'],
                                             f"https://vk.com/id{result[counter - 1]['id']}",
                                             0):
                            print('Добавлено в чёрный список')
                            write_message(authorize,
                                          sender_id,
                                          "Больше не встретится)",
                                          create_k.favorite())
                    elif received_message == 'Закончить':
                        write_message(authorize,
                                      sender_id,
                                      f"Подбор окончен",
                                      create_k.finish())
                    elif received_message == 'Пока, бро!':
                        write_message(authorize,
                                      sender_id,
                                      f"Сладких котёнок",
                                      create_k.bro())
                    else:
                        write_message(authorize, sender_id,
                                      "Я вас не понимаю...",
                                      create_k.hi())

        except Exception as exception:
            print(exception)
            time.sleep(5)
            if sender_id:
                write_message(authorize, sender_id, "Бот на связи!", create_k.hi())


if __name__ == '__main__':
    main()
