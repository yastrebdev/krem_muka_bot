import sqlite3


async def create_user(username, name):
    connection = sqlite3.connect('db/database.db')
    cursor = connection.cursor()

    cursor.execute('INSERT INTO Users (username, name) VALUES (?, ?)', (username, name))

    connection.commit()
    connection.close()


async def find_user_by_username(username):
    connection = sqlite3.connect('db/database.db')
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM Users WHERE username = ?', (username,))

    user = cursor.fetchone()

    connection.close()

    return user[0] if user else None


async def get_user_id_by_username(username):
    connection = sqlite3.connect('db/database.db')
    cursor = connection.cursor()

    cursor.execute('SELECT id FROM Users WHERE username = ?', (username,))

    user_id = cursor.fetchone()

    connection.close()

    if user_id:
        return user_id[0]
    return None