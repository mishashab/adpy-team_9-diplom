from token_id import bot_token, user_token
from VKinder.VKinder import VKinder
from VKinder import DB

import vk_api
from datetime import date
import time
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
import psycopg2


def write_message(authorize, sender, message, attachment=''):
    authorize.method('messages.send', {'user_id': sender, 'message': message, "random_id": get_random_id(),
                                       'attachment': attachment})


def calculate_age(born):
    born = born.split(".")
    today = date.today()
    return today.year - int(born[2]) - ((today.month, today.day) < (int(born[1]), int(born[0])))


def get_str(url_photos):
    '''Собираем из списка tuple строку для бота'''
    str_photo = ''
    for item in url_photos:
        if not str_photo:
            str_photo = item[0]
        else:
            str_photo += f',{item[0]}'
    return str_photo


def data_conversion(db_source, cur):
    '''Преобразует данные из базы данных в нужный для бота вид'''
    users = list()
    for item in db_source:
        users.append({'id': item[0], 'name': f'{item[1]} {item[2]}', 'url': item[3],
                      'attachment': get_str(DB.get_photo(cur, item[0]))})
    return users


def add_to_database(cur, sender_id, result):
    '''Пишет полученные данные из поиска в базу данных'''
    for i_user in result:
        if not DB.check_find_user(cur, i_user['id']):
            if DB.add_find_users(cur, i_user['id'], sender_id, i_user['first_name'],
                                 i_user['last_name'], i_user['url']):
                for item in i_user['attachment']:
                    DB.add_find_users_photos(cur, i_user['id'], item)
    return True


def get_from_database(cur, authorize, counter, sender_id):
    '''Достаёт данные о найденном пользователе из базы данных'''
    if counter < DB.count_db(cur)[0]:
        flag = True
        while flag and counter < DB.count_db(cur)[0]:
            db_source = DB.get_find_users(cur, sender_id, counter)
            if db_source:
                users = {'id': db_source[0],
                         'name': f'{db_source[1]} {db_source[2]}',
                         'url': db_source[3],
                         'attachment': get_str(DB.get_photo(cur, db_source[0]))}
                write_message(authorize, sender_id, f"{users['name']}\n{users['url']}",
                              users['attachment'])
                write_message(authorize, sender_id, 'Дальше? или в избранное?(да/в избранное/в чёрный список)')
                flag = False
            counter += 1
    else:
        write_message(authorize, sender_id, 'Мы посмотрели всё! Заново? (да/смотреть избранное)')
        counter = 1
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

    conn = psycopg2.connect(database="course_w", user="postgres", password="")
    with conn.cursor() as cur:
        # print(DB.drop_table(cur)) #если нужно сбросить БД
        print(DB.create_db(cur))

        counter = 1
        ask_user = dict()
        flag = True
        while flag:
            try:
                for event in longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                        reсeived_message = event.text
                        sender_id = event.user_id

                        if not DB.get_ask_user_data(cur, sender_id):
                            print('ask_user в базе отсутствует')
                            user_info = session.account.getProfileInfo(user_id=sender_id)
                            user_info['age'] = calculate_age(user_info['bdate'])
                            if user_info['sex'] == 2:
                                user_info['gender'] = 'Мужской'
                            elif user_info['sex'] == 1:
                                user_info['gender'] = 'Женский'
                            else:
                                user_info['gender'] = 'Пол не указан'

                            if DB.add_ask_user(cur, user_info['id'], user_info['first_name'], user_info['last_name'],
                                               user_info['age'], user_info['home_town'], user_info['city']['id'],
                                               user_info['gender']):
                                conn.commit()
                                print('ask_user добавлен в базу')
                            else:
                                print('ask_aser НЕ добавлен в базу')

                        if reсeived_message.lower() == "привет":
                            print(f'Пользователь = {DB.get_ask_user_data(cur, sender_id)}')

                            ask_user = DB.get_ask_user_data(cur, sender_id)
                            write_message(authorize, sender_id, f"Доброго времени суток, {ask_user[1]}!\n"
                                                                f"Ваши параметры:\nГород: {ask_user[4]}\n"
                                                                f"Пол: {ask_user[6]}\nВозраст: {ask_user[3]}\n"
                                                                f"Поиск или посмотрим базу? Или смотрим избранное?"
                                                                f"(поиск\смотрим\смотреть избраноное)")

                        elif reсeived_message.lower() in ['смотреть избранное']:
                            if DB.get_favourites(cur, sender_id):
                                db_source = DB.get_favourites(cur, sender_id)
                                favourites = data_conversion(db_source, cur)
                                for item in favourites:
                                    write_message(authorize, sender_id, f"{item['name']}\n{item['url']}",
                                                  item['attachment'])
                                write_message(authorize, sender_id, "Смотрим базу? Выполнить поиск?(смотрим/поиск)")
                            else:
                                write_message(authorize, sender_id, f"Избранное пусто. Выпольните поиск или загрузите "
                                                                    f"базу. (поиск/загрузить)")

                        elif reсeived_message.lower() in ['ищем', 'поиск', 'выполнить', 'выполнить поиск']:

                            if not DB.check_find_user(cur, sender_id):

                                write_message(authorize, sender_id, f"Ищу...")

                                v_kinder = VKinder(longpoll, session)
                                result = v_kinder.find_user(ask_user)

                                if add_to_database(cur, ask_user[0], result):
                                    print('Добавлено в базу')
                                    conn.commit()
                                    write_message(authorize, sender_id, "Данные записаны в базу. Смотрим?(да)")
                                else:
                                    print('Что-то пошло не так...')
                            else:
                                write_message(authorize, sender_id, "База данных не пустая. Посмотрим?(да/смотреть "
                                                                    "избранное")

                        elif reсeived_message.lower() in ['смотрим', 'смотреть', 'просмотр', 'да', 'дальше']:

                            if DB.check_find_user(cur, ask_user[0]):
                                counter = get_from_database(cur, authorize, counter, sender_id)
                            else:
                                print('База пустая')
                                write_message(authorize, sender_id, "База пустая, выполните поиск(Поиск)")

                        elif reсeived_message.lower() in ['в избранное', 'добавить в избранное']:

                            if DB.add_favourites(cur, counter - 1, 1):
                                conn.commit()
                                print('Добавлено в избранное')
                                write_message(authorize, sender_id, "Добавлен в избранное. Дальше?"
                                                                    "(да/смотреть избранное)")

                        elif reсeived_message.lower() in ['в черный', 'чёрный', 'нет']:

                            if DB.add_favourites(cur, counter - 1, 2):
                                conn.commit()
                                print('Добавлено в чёрный список')
                                write_message(authorize, sender_id, "Добавлен в чёрный список. Дальше?(да)")

                        else:
                            write_message(authorize, sender_id, "Я вас не понимаю...")

            except Exception as exception:
                print(exception)
                time.sleep(5)
                if sender_id:
                    write_message(authorize, sender_id, "Бот на связи!")

    conn.close()


if __name__ == '__main__':
    main()
