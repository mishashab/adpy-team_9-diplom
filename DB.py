def drop_table(cur):
    cur.execute("""
        DROP TABLE photos;
        DROP TABLE find_users;
        DROP TABLE ask_user;
    """)

    return 'Таблицы очищены'


def create_db(cur):
    cur.execute('''
        CREATE TABLE IF NOT EXISTS ask_user (
        user_id INTEGER UNIQUE PRIMARY KEY,
        first_name VARCHAR(40) NOT NULL,
        last_name VARCHAR(40) NOT NULL,
        user_age VARCHAR(10) NOT NULL,
        user_city VARCHAR(20) NOT NULL,
        city_id INTEGER,
        user_sex VARCHAR(20) NOT NULL
    );
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS find_users (
        f_user_id INTEGER UNIQUE PRIMARY KEY,
        user_id INTEGER REFERENCES ask_user(user_id),
        f_first_name VARCHAR(40) NOT NULL,
        f_last_name VARCHAR(40) NOT NULL,
        user_url VARCHAR(40) NOT NULL UNIQUE,
        favourites BOOLEAN,
        iterator SERIAL
    );
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS photos (
        id SERIAL PRIMARY KEY,
        f_user_ids INTEGER REFERENCES find_users(f_user_id),
        photo_str VARCHAR(40)
    );
    ''')
    return 'Структура БД создана'


def add_ask_user(cur, user_id, first_name, last_name, user_age, user_city, city_id, user_sex):
    '''добавлят данные спрашивающего пользователя в базу данных'''
    cur.execute("""
        INSERT INTO ask_user(user_id, first_name, last_name, user_age, user_city, city_id, user_sex)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """, (user_id, first_name, last_name, user_age, user_city, city_id, user_sex))
    cur.execute('''
        SELECT * FROM ask_user
        WHERE user_id = %s;
        ''', (user_id,))

    return cur.fetchone()


def get_ask_user_data(cur, user_id):
    '''достает из базы данные спращивающего пользователя'''
    cur.execute('''
        SELECT * FROM ask_user
        WHERE user_id = %s;
        ''', (user_id,))
    return cur.fetchone()


def add_find_users(cur, f_user_id, user_id, f_first_name, f_last_name, user_url):
    '''Добавляет в базу данных всех найденных людей'''
    cur.execute("""
        INSERT INTO find_users(f_user_id, user_id, f_first_name, f_last_name, user_url)
        VALUES (%s, %s, %s, %s, %s);
        """, (f_user_id, user_id, f_first_name, f_last_name, user_url))
    cur.execute('''
        SELECT * FROM find_users
        WHERE f_user_id = %s;
        ''', (f_user_id,))
    return cur.fetchone()


def check_find_user(cur, user_id):
    '''проверяем пустая ли база данных'''
    cur.execute('''
        SELECT f_user_id FROM find_users
        WHERE user_id = %s;
    ''', (user_id,))
    return cur.fetchone()


#доработать случай когда блэк лист и избранное
def get_find_users(cur, user_id, iterator):
    '''получаем данные из базы о найденных пользователях'''
    cur.execute('''
        SELECT f_user_id, f_first_name, f_last_name, user_url FROM find_users
        WHERE user_id = %s AND favourites IS NOT true AND iterator = %s;
    ''', (user_id, iterator))
    return cur.fetchone()


def get_photo(cur, f_user_id):
    '''достает из базы данных фото'''
    cur.execute('''
        SELECT photo_str FROM photos
        WHERE f_user_ids = %s;
    ''', (f_user_id,))
    return cur.fetchall()


def add_find_users_photos(cur, f_user_id, photo_str):
    '''Добавляет в таблицу фото найденных людей'''
    cur.execute('''
        INSERT INTO photos(f_user_ids, photo_str)
        VALUES (%s, %s);
        ''', (f_user_id, photo_str))
    cur.execute('''
        SELECT * FROM photos
        WHERE f_user_ids = %s;
        ''', (f_user_id,))
    return cur.fetchone()


def add_favourites(cur, f_user_id):
    '''Добавляет в список избранных'''
    cur.execute('''
        UPDATE find_users SET favourites = %s WHERE f_user_id = %s;
    ''', ('true', f_user_id))
    cur.execute('''
        SELECT favourites FROM find_users
        WHERE f_user_id = %s;
    ''', (f_user_id,))
    return cur.fetchone()


def get_favourites(cur, user_id):
    '''Выгружает из базы данных список избранных'''
    cur.execute('''
        SELECT f_user_id, f_first_name, f_last_name, user_url FROM find_users
        WHERE user_id = %s AND favourites is true;
    ''', (user_id,))
    return cur.fetchall()


def count_db(cur):
    '''считаем размер базы данных'''
    cur.execute('''
        SELECT COUNT(user_id) FROM find_users;
    ''')
    return cur.fetchone()
