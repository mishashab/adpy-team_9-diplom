from token_id import bot_token, user_token
from VKinder import VKinder
from pprint import pprint
import vk_api
from datetime import date
#для загрузки файлов
from vk_api import VkUpload
#подключаем функции для работы с АПИ и событиями
from vk_api.longpoll import VkLongPoll, VkEventType
# from vk_api.bot_longpoll import longpoll import VkBotLongPoll, VkBotEventType
# подключаем функцию генерирующию случайные id, можно использовать любой другой инструмент для генерации
from vk_api.utils import get_random_id


def write_message(authorize, sender, message, attachment=''):
    #messages.send - название метода отправки сообщений. user_id - id пользователя
    # message - текст сообщения.  random_id - случайный идентификационный номер сообщения, чтобы одно сообщение не отправлялось дважды
    authorize.method('messages.send', {'user_id': sender, 'message': message, "random_id": get_random_id(),
                                       'attachment': attachment})


def calculate_age(born):
    born = born.split(".")
    today = date.today()
    return today.year - int(born[2]) - ((today.month, today.day) < (int(born[1]), int(born[0])))


def main():
    print("Hi bot")
    authorize = vk_api.VkApi(token=bot_token)
    longpoll = VkLongPoll(authorize)

    user_session = vk_api.VkApi(token=user_token)
    session = user_session.get_api()

    #бесконечный цикл, коотрые слушает сообщения от сервера ВК
    counter = 0
    user_param = dict()
    result = list()
    for event in longpoll.listen():
        # проверяет тип события и точто оно отправлено боту и то что оно текст
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            reseived_message = event.text
            # print(reseived_message)
            #определим вопрошающего
            sender_id = event.user_id
            # user = session.users.get(user_id=sender_id)
            user_info = session.account.getProfileInfo(user_id=sender_id)
            user_param['age'] = calculate_age(user_info['bdate'])
            if user_info['sex'] == 2:
                gender = 'Мужской'
                user_param['gender'] = 1
            elif user_info['sex'] == 1:
                gender = 'Женский'
                user_param['gender'] = 2
            else:
                gender = 'Пол не указан'
                user_param['gender'] = 0
            # print(user)
            user_param['city_id'] = user_info['city']['id']
            if reseived_message.lower() == "привет":
                write_message(authorize, sender_id, f"Доброго времени суток, {user_info['first_name']}!\n"
                                                    f"Ваши параметры:\nГород: {user_info['city']['title']}\n"
                                                    f"Пол: {gender}\nВозраст: {user_param['age']}\nИщем?")
            elif reseived_message.lower() in ['да', 'ищем', 'начали', 'ok', 'ок', 'yes', 'поехали'] and counter == 0:
                # if counter == 0:
                write_message(authorize, sender_id, f"Ищу...")
                v_kinder = VKinder(longpoll, session)
                result = v_kinder.find_user(user_param)
                # print(len(result))
                write_message(authorize, sender_id, f"{result[counter]['name']}\n{result[counter]['url']}",
                              result[counter]['attachment'])
                write_message(authorize, sender_id, "Дальше?")
                counter += 1
            elif reseived_message.lower() in ['дальше', 'да'] and counter < len(result):
                write_message(authorize, sender_id, f"{result[counter]['name']}\n{result[counter]['url']}",
                              result[counter]['attachment'])
                write_message(authorize, sender_id, "Дальше?")
                counter += 1
            elif len(result) <= counter:
                # print(counter)
                # print(len(result))
                write_message(authorize, sender_id, "Список закончился!")
            elif reseived_message.lower() == "пока":
                write_message(authorize, sender_id, "До свидания!")
            else:
                write_message(authorize, sender_id, "Я вас не понимаю...")


if __name__ == '__main__':
    main()
