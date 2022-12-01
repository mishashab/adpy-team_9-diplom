import psycopg2

def create_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS vk_user(
                id INTEGER PRIMARY KEY,
                first_name VARCHAR(40) NOT NULL,
                second_name VARCHAR(40) NOT NULL,
                url VARCHAR(40) NOT NULL UNIQUE
            );
            """)
        conn.commit()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_photo(
                id SERIAL PRIMARY KEY,
                user_id int REFERENCES vk_user(id),
                user_picture VARCHAR(40) UNIQUE
            );
            """)
        conn.commit()  # фиксируем в БД
        cur.execute("""
             CREATE TABLE IF NOT EXISTS user_like(
                 user_id int NOT NULL REFERENCES vk_user(id),
                 favorit_id int NOT NULL REFERENCES vk_user(id)
             );
             """)
        conn.commit()  # фиксируем в БД
        cur.execute("""
             CREATE TABLE IF NOT EXISTS user_not_like(
                 user_id int NOT NULL REFERENCES vk_user(id),
                 dislike_id int NOT NULL REFERENCES vk_user(id)
             );
             """)
        conn.commit()  # фиксируем в БД

    pass

def add_user (conn, id, first_name, second_name, url, photo=None):
    with conn.cursor() as cur:
        postgres_insert_query = "INSERT INTO vk_user(id, first_name, second_name, url) VALUES(%s,%s,%s,%s);"
        record_to_insert = (id, first_name, second_name, url)
        cur.execute(postgres_insert_query, record_to_insert)
        if photo != None:
            for i in photo:
                postgres_insert_query = "INSERT INTO user_photo(user_id, user_picture) VALUES(%s,%s);"
                record_to_insert = (id, i)
                cur.execute(postgres_insert_query, record_to_insert)
        conn.commit()  # фиксируем в БД
    pass

def add_user_like(conn, user_id, favorit_id):
    with conn.cursor() as cur:
        postgres_insert_query = "INSERT INTO user_like(user_id, favorit_id) VALUES(%s,%s);"
        record_to_insert = (user_id, favorit_id)
        cur.execute(postgres_insert_query, record_to_insert)
    conn.commit()  # фиксируем в БД

def add_user_dislike(conn, user_id, dislike_id):
    with conn.cursor() as cur:
        postgres_insert_query = "INSERT INTO user_not_like(user_id, dislike_id) VALUES(%s,%s);"
        record_to_insert = (user_id, dislike_id)
        cur.execute(postgres_insert_query, record_to_insert)
    conn.commit()  # фиксируем в БД


def find_client(conn, user_id):
    with conn.cursor() as cur:
        postgres_insert_query = 'SELECT id FROM vk_user WHERE id = %s;'
        record_to_insert = (user_id,)
        cur.execute(postgres_insert_query, record_to_insert)
        return bool(cur.fetchall())
    pass

def find_like(conn, user_id, favorit_id):
    with conn.cursor() as cur:
        postgres_insert_query = 'SELECT EXISTS (SELECT * FROM user_like WHERE user_id = %s AND favorit_id = %s);'
        record_to_insert = (user_id, favorit_id)
        cur.execute(postgres_insert_query, record_to_insert)
        answer = cur.fetchall()
        for c in answer:
            for i in c:
                result = i
        return result



if __name__ == '__main__':
    with psycopg2.connect(database='VKinder', user='postgres', password='') as conn:
        create_db(conn)
        # add_user(conn, 1, 'Андрей', 'Заболотский', ['aaa.com.1', ])
        # add_user(conn, 2, 'Антон', 'Городецкий', ['aaa.com.2', ])
        # add_user(conn, 3, 'Сергей', 'Заболотский', ['aaa.com.3', ])
        find_client(conn, 4)
        # add_user_like(conn, 1, 2)
        # add_user_like(conn, 1, 3)
        # add_user_like(conn, 2, 1)
        # add_user_like(conn, 3, 2)
        find_like(conn, 3, 1)
