import psycopg2
from VKinder.token_id import database, user, password


def db_connect():
    conn = psycopg2.connect(database=database,
                            user=user,
                            password=password)
    cur = conn.cursor()
    return conn, cur


def db_connect_close(cur, conn):
    conn.commit()
    cur.close()
    conn.close()


def drop_table():
    conn, cur = db_connect()
    cur.execute("""
        DROP TABLE photos;
        DROP TABLE find_users;
        DROP TABLE ask_user;
    """)
    db_connect_close(cur, conn)
    return 'Таблицы очищены'


def create_db():
    conn, cur = db_connect()
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
        favourites INTEGER
    );
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS photos (
        id SERIAL PRIMARY KEY,
        f_user_ids INTEGER REFERENCES find_users(f_user_id),
        photo_str VARCHAR(40)
    );
    ''')
    db_connect_close(cur, conn)
    return 'Структура БД создана'


def add_ask_user(user_id, first_name, last_name, user_age, user_city, city_id, user_sex):
    '''добавлят данные спрашивающего пользователя в базу данных'''
    conn, cur = db_connect()
    cur.execute("""
        INSERT INTO ask_user(user_id, first_name, last_name, user_age, user_city, city_id, user_sex)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """, (user_id, first_name, last_name, user_age, user_city, city_id, user_sex))
    cur.execute('''
        SELECT * FROM ask_user
        WHERE user_id = %s;
        ''', (user_id,))
    result = cur.fetchone()
    db_connect_close(cur, conn)
    return result


def get_ask_user_data(user_id):
    '''достает из базы данные спращивающего пользователя'''
    conn, cur = db_connect()
    cur.execute('''
        SELECT * FROM ask_user
        WHERE user_id = %s;
        ''', (user_id,))
    result = cur.fetchone()
    db_connect_close(cur, conn)
    return result


def check_find_user(user_id, f_user_id):
    '''проверяем есть ли человек в избранном или в блоке'''
    conn, cur = db_connect()
    cur.execute('''
        SELECT f_user_id FROM find_users
        WHERE user_id = %s AND f_user_id = %s;
    ''', (user_id, f_user_id))
    result = cur.fetchone()
    db_connect_close(cur, conn)
    return result


def get_photo(f_user_id):
    '''достает из базы данных фото'''
    conn, cur = db_connect()
    cur.execute('''
        SELECT photo_str FROM photos
        WHERE f_user_ids = %s;
    ''', (f_user_id,))
    result = cur.fetchall()
    db_connect_close(cur, conn)
    return result


def add_favourites(f_user_id, user_id, f_first_name, f_last_name, user_url, flag):
    '''Добавляет в список избранных'''
    conn, cur = db_connect()
    cur.execute('''
        INSERT INTO find_users(f_user_id, user_id, f_first_name, f_last_name, user_url, favourites)
        VALUES (%s, %s, %s, %s, %s, %s);
    ''', (f_user_id, user_id, f_first_name, f_last_name, user_url, flag))
    cur.execute('''
        SELECT favourites FROM find_users
        WHERE f_user_id = %s;
    ''', (f_user_id,))
    result = cur.fetchone()
    db_connect_close(cur, conn)
    return result


def add_find_users_photos(f_user_id, photo_str):
    '''Добавляет в таблицу фото найденных людей'''
    conn, cur = db_connect()
    cur.execute('''
        INSERT INTO photos(f_user_ids, photo_str)
        VALUES (%s, %s);
        ''', (f_user_id, photo_str))
    cur.execute('''
        SELECT * FROM photos
        WHERE f_user_ids = %s;
        ''', (f_user_id,))
    result = cur.fetchone()
    db_connect_close(cur, conn)
    return result


def get_favourites(user_id):
    '''Выгружает из базы данных список избранных'''
    conn, cur = db_connect()
    cur.execute('''
        SELECT f_user_id, f_first_name, f_last_name, user_url FROM find_users
        WHERE user_id = %s AND favourites = %s;
    ''', (user_id, 1))
    result = cur.fetchall()
    db_connect_close(cur, conn)
    return result
