import sqlite3

def init_db():
    connection = sqlite3.connect('db/database.db')
    cursor = connection.cursor()

    # 1. Создаем таблицу Users (с правильными типами)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY,
        username VARCHAR(24) NOT NULL,
        name VARCHAR(24) NOT NULL
    );
    ''')

    # 2. Создаем таблицу Products
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Products (
        product_id INTEGER PRIMARY KEY,
        name VARCHAR(32) NOT NULL,
        filling VARCHAR(32) NOT NULL,
        price INTEGER NOT NULL
    );
    ''')

    # 3. Создаем таблицу Orders (исправлено)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Orders (
        order_id INTEGER PRIMARY KEY,
        product VARCHAR(32) NOT NULL,
        description VARCHAR(256),
        event VARCHAR(32),
        count INTEGER NOT NULL,
        price INTEGER NOT NULL,
        discount INTEGER DEFAULT 0 NOT NULL CHECK(discount >= 0 AND discount <= 100),
        prepayment INTEGER DEFAULT 0 NOT NULL,
        summ INTEGER GENERATED ALWAYS AS (count * price * (1 - discount/100)) STORED,
        delivery_method CHAR(1) NOT NULL CHECK(delivery_method = 'С' OR delivery_method = 'Д'),
        delivery_price INTEGER DEFAULT 0,
        flau_price INTEGER DEFAULT 0,
        source VARCHAR(32) NOT NULL,
        time TIME,
        order_date DATE,
        is_completed BOOLEAN NOT NULL,
        user_id INTEGER,
        FOREIGN KEY (product) REFERENCES Products(name),
        FOREIGN KEY (user_id) REFERENCES Users(id)
    );
    ''')

    connection.commit()
    connection.close()

if __name__ == '__main__':
    init_db()