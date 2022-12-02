from token_id import bot_token, user_token
from VKinder import VKinder

from pprint import pprint
import vk_api
from datetime import date
#подключаем функции для работы с АПИ и событиями
from vk_api.longpoll import VkLongPoll, VkEventType
# подключаем функцию генерирующию случайные id, можно использовать любой другой инструмент для генерации
from vk_api.utils import get_random_id
import psycopg2
import DB


def write_message(authorize, sender, message, attachment=''):
    #messages.send - название метода отправки сообщений. user_id - id пользователя
    # message - текст сообщения.  random_id - случайный идентификационный номер сообщения, чтобы одно сообщение не отправлялось дважды
    authorize.method('messages.send', {'user_id': sender, 'message': message, "random_id": get_random_id(),
                                       'attachment': attachment})


def calculate_age(born):
    born = born.split(".")
    today = date.today()
    return today.year - int(born[2]) - ((today.month, today.day) < (int(born[1]), int(born[0])))


def db_list_to_dict(db_list):
    db_dict = dict()
    db_source = list()
    counter = -1
    for item in db_list:
        if item[0] in db_source:
            print(f'Зашел добавить!')
            db_source[counter]['photo'].append(item[4])
        else:
            db_dict['name'] = f'{item[1]} {item[2]}'
            db_dict['url'] = item[3]
            db_dict['photo'] = item[4]
            db_source.append(db_dict)
            counter += 1

    return db_source


def main():
    print("Hi bot")
    authorize = vk_api.VkApi(token=bot_token)
    longpoll = VkLongPoll(authorize)

    user_session = vk_api.VkApi(token=user_token)
    session = user_session.get_api()

    conn = psycopg2.connect(database="course_w", user="postgres", password="")
    with conn.cursor() as cur:
        # print(DB.drop_table(cur))
        print(DB.create_db(cur))

        #бесконечный цикл, коотрые слушает сообщения от сервера ВК
        flag = 0
        ask_user = dict()
        result = list()
        for event in longpoll.listen():
            # проверяет тип события и точто оно отправлено боту и то что оно текст
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                reseived_message = event.text
                # определим вопрошающего
                sender_id = event.user_id

                #проверет наличие такого спрашивающего юзера в базе
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
                    # pprint(user_info)
                    if DB.add_ask_user(cur, user_info['id'], user_info['first_name'], user_info['last_name'],
                                       user_info['age'], user_info['home_town'], user_info['city']['id'],
                                       user_info['gender']):
                        conn.commit()
                        print('ask_user добавлен в базу')
                    else:
                        print('ask_aser НЕ добавлен в базу')

                else:
                    print('ask_user присутствует в базе')

                if reseived_message.lower() == "привет":
                    print(f'Пользователь = {DB.get_ask_user_data(cur, sender_id)}')
                    #достаем данные запрашивающего юзера из базы данных
                    ask_user = DB.get_ask_user_data(cur, sender_id)
                    write_message(authorize, sender_id, f"Доброго времени суток, {ask_user[1]}!\n"
                                                        f"Ваши параметры:\nГород: {ask_user[4]}\n"
                                                        f"Пол: {ask_user[6]}\nВозраст: {ask_user[3]}\n"
                                                        f"Поиск или посмотрим базу?")

                elif reseived_message.lower() in ['ищем', 'поиск', 'выполнить', 'выполнить поиск']:

                    write_message(authorize, sender_id, f"Ищу...")

                    v_kinder = VKinder(longpoll, session)
                    result = v_kinder.find_user(ask_user)

                    for i_user in result:
                        if not DB.check_find_user(cur, i_user['id']):
                            if DB.add_find_users(cur, i_user['id'], ask_user[0], i_user['first_name'],
                                                 i_user['last_name'],i_user['url']):
                                print(f"User id={i_user['id']} добавлен")
                            for item in i_user['attachment']:
                                if DB.add_find_users_photos(cur, i_user['id'], item):
                                    print('Фото добавлены')
                        else:
                            print(f'User {i_user["id"]} присутствует в базе')
                            # print(i_user['attachment'])
                    conn.commit()
                    # write_message(authorize, sender_id, f"{result[counter]['name']}\n{result[counter]['url']}",
                    #               result[counter]['attachment'])
                    write_message(authorize, sender_id, "Данные записаны в базу. Смотрим?")
                    # pprint(result)
                elif reseived_message.lower() in ['смотрим', 'просмотр', 'просмотр', 'просмотрим']:
                    if DB.check_find_user(cur, ask_user[0]):
                        db_source = DB.get_find_users(cur, ask_user[0])
        #ЗАСТРЯЛ ТУТ!!!
                        db_source = db_list_to_dict(db_source)
                        print('Данные записаны в словарь')
                        pprint(db_source)
                    else:
                        print('База пустая')
                        write_message(authorize, sender_id, "База пустая, выполните поиск")

                # elif reseived_message.lower() in ['дальше', 'да'] and counter < len(result):
                #     write_message(authorize, sender_id, f"{result[counter]['name']}\n{result[counter]['url']}",
                #                   result[counter]['attachment'])
                #     write_message(authorize, sender_id, "Дальше?")
                #     counter += 1
                # elif len(result) <= counter:
                #     write_message(authorize, sender_id, "Список закончился!")
                # elif reseived_message.lower() == "пока":
                #     write_message(authorize, sender_id, "До свидания!")
                else:
                    write_message(authorize, sender_id, "Я вас не понимаю...")

    conn.close()


if __name__ == '__main__':
    main()
