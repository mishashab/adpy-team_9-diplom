# Командный проект VKinder
## Документрация по использованию программы:
1. Создать группу во Вкотакте, от имени которой будет общаться разрабатынный бот
2. Создать токен для бота:
    * Зайти в созданную группу -> Управление -> Работа с API. Вкладка "LongPoll API", ключить LongPoll API
    ![LongPoll API enable](media\LongPollAPI.jpg)
    * Перейти во вкладку "Типы событий" и дать боту соответствующие права
    ![LongPoll API Events](media\LongPollAPIEvents.jpg)
    * Вернуться во кладку "Ключи доступа". Создать ключ
     ![Create LongPoll API key](media\CreateLongPollAPI.jpg)
    * Перейти в Управление -> Сообщения Убедиться, что Сообщения сообщества включены:
    ![Enable message](media\EnableMsg.jpg)
    * Перейти в Управление -> Сообщения -> Настройки для бота, включить "Возможности ботов"
    ![Enable Bot Opportunities](media\BotOpportunities.jpg)
    * В корне проекта создать текстовый файл bot_token.txt, перейти  Управление -> Работа с API, скопировать созданный ключ и сохранить в этот файл
3. Далее необходимо создать токен для пользователя, который будет общаться с ботом:
    * Получить токен для ВК можно выполнив [инструкцию](https://docs.google.com/document/d/1_xt16CMeaEir-tWLbUFyleZl6woEdJt-7eyva1coT3w/edit?usp=sharing)
    * В корне проекта создать текстовый файл user_token.txt и сохранить в него полученый токен
4. Теперь всё готово для начала работы с ботом. Запустим программу
5. В созданной группе напишем сообщение боту "Привет". Бот получит данные о пользователе и выведет их в ответном приветственном сообщении и спросит вас о дальнейших действиях
![Hi bot](media\HImsg.jpg)
6. Если вы уже пользовались поиском, то база данных не пустая и следует продолжить просмотр выполнив команду "смотрим", либо если были добавлены люди в избранное, можно вывести его содержимое выполнив команду "смотреть избранное". Если база данных пустая, выполним команду "поиск". Бот выполнит поиск по вашим параметрам и сохранит в базу данных всех не приватных пользователей.
7. Когда бот завершит поиск, он выведет сообщение "Данные записаны в базу. Смотрим?(да)". Введем команду "Да" для начала просмотра каталога пользователей.
![View catalog](media\ViewCatalog.jpg)
8. Если человек понравился, можно добавить его в избранное, выполнив команду "В избранное" (*Если человек добавлен в избранное, то при повторном просмотре каталога он не будет выведен*)
9. Для перехода к следующему человеку введёс команду "да"
10. После того как будет просмотрен весь каталог, бот выведет сообщение "Мы посмотрели всё! Заново? (да/смотреть избранное)"
