import sqlite3


def create_users_tables():
    database = sqlite3.connect('vkusnyaha.db')
    cursor = database.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT,
    telegram_id BIGINT NOT NULL UNIQUE,
    phone TEXT
    );
    ''')


# create_users_tables()


def create_cart_table():
    database = sqlite3.connect('vkusnyaha.db')
    cursor = database.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS carts(
    cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(user_id),
    total_price DECIMAL(12, 2) DEFAULT 0,
    total_products INTEGER DEFAULT 0
    );
    ''')


# create_cart_table()


def create_cart_products_table():
    database = sqlite3.connect('vkusnyaha.db')
    cursor = database.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cart_products(
    card_products_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL,
    final_price DECIMAL(12, 2) NOT NULL,
    cart_id INTEGER REFERENCES carts(cart_id),
    UNIQUE(product_name, cart_id)
    )
    ''')


# create_cart_products_table()


def create_categories_table():
    database = sqlite3.connect('vkusnyaha.db')
    cursor = database.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories(
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name VARCHAR(30) NOT NULL UNIQUE
    )
    ''')


# create_categories_table()


def insert_categories():
    database = sqlite3.connect('vkusnyaha.db')
    cursor = database.cursor()
    cursor.execute('''
    INSERT INTO categories(category_name) VALUES
    ('NIKE'),
    ('NEW BALANCE'),
    ('the underdogs'),
    ('ADIDAS'),
    ('REEBOK'),
    ('PUMA')
    ''')
    database.commit()
    database.close()


# insert_categories()


def create_products_table():
    database = sqlite3.connect('vkusnyaha.db')
    cursor = database.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products(
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name VARCHAR(30) NOT NULL UNIQUE,
    price DECIMAL(12,2) NOT NULL,
    description VARCHAR(200),
    image TEXT,
    category_id INTEGER NOT NULL,
    FOREIGN KEY(category_id) REFERENCES categories(category_id)
    );
''')


# create_products_table()


def insert_products_table():
    database = sqlite3.connect('vkusnyaha.db')
    cursor = database.cursor()
    cursor.execute('''
        INSERT INTO products(category_id, product_name, price, description, image) VALUES
        (1, 'Nike Dunk low sneakers', 1800000, 'The Nike Dunk Low Valerian Blue released in May of 2022 and retailed for $100.', 'media/nike/air_jordan.jpg'),
        (1, 'Air Jordan 1 High 85 shoes', 1600000, 'Air Jordan 1 Retro High OG "Chicago Lost And Found" sneakers', 'media/nike/dunk_low.jpg'),
        (1, 'Nike x Stüssy Air Penny 2', 2000000, 'The sneaker was released on the 20th of December 2022 for $200.', 'media/nike/air_penny.jpg')
    ''')
    database.commit()
    database.close()


#
# insert_products_table()


def first_select_user(chat_id):
    database = sqlite3.connect('vkusnyaha.db')
    cursor = database.cursor()
    cursor.execute('''
    SELECT * FROM users WHERE telegram_id = ?
    ''', (chat_id,))
    user = cursor.fetchone()
    database.close()

    return user


def first_register_user(chat_id, full_name):
    database = sqlite3.connect('vkusnyaha.db')
    cursor = database.cursor()
    cursor.execute('''
        INSERT INTO users(telegram_id, full_name) VALUES(?, ?)
    ''', (chat_id, full_name))
    database.commit()
    database.close()


def update_user_to_finish_register(chat_id, phone):
    database = sqlite3.connect('vkusnyaha.db')
    cursor = database.cursor()
    cursor.execute('''
        UPDATE users
        SET phone = ?
        WHERE telegram_id = ?
    ''', (chat_id, phone))
    database.commit()
    database.close()


def insert_to_cart(chat_id):
    database = sqlite3.connect('vkusnyaha.db')
    cursor = database.cursor()
    cursor.execute('''
    INSERT INTO carts(user_id) VALUES
    (
    (SELECT user_id FROM users WHERE telegram_id = ?)
    );
    ''', (chat_id,))
    database.commit()
    database.close()
    return chat_id


def get_all_categories():
    database = sqlite3.connect('vkusnyaha.db')
    cursor = database.cursor()
    cursor.execute('''
    SELECT * FROM categories;
    ''')
    categories = cursor.fetchall()
    database.close()
    return categories


def get_products_by_category_id(category_id):
    database = sqlite3.connect('vkusnyaha.db')
    cursor = database.cursor()
    cursor.execute('''
    SELECT product_id, product_name FROM products
    WHERE category_id = ?
    ''', (category_id,))
    products = cursor.fetchall()
    database.close()
    return products


def get_product_detail(product_id):
    database = sqlite3.connect('vkusnyaha.db')
    cursor = database.cursor()
    cursor.execute('''
    SELECT * FROM products
    WHERE product_id = ?
    ''', (product_id,))
    product = cursor.fetchone()
    database.close()
    return product


def get_user_cart_id(chat_id):
    database = sqlite3.connect('vkusnyaha.db')
    cursor = database.cursor()
    cursor.execute('''
    SELECT cart_id FROM carts
    WHERE user_id = (
        SELECT user_id FROM users WHERE telegram_id = ?
    )
    ''', (chat_id,))
    cart_id_tuple = cursor.fetchone()
    database.close()
    print('cart_id', cart_id_tuple)
    if cart_id_tuple is not None:
        return cart_id_tuple[0]
    else:
        return None


def get_quantity(cart_id, product):
    database = sqlite3.connect('vkusnyaha.db')
    cursor = database.cursor()
    cursor.execute('''
    SELECT quantity FROM cart_products
    WHERE cart_id = ? AND product_name = ?
    ''', (cart_id, product))

    quantity = cursor.fetchone()[0]
    database.close()
    return quantity


def insert_or_update_cart_product(cart_id, product_name, quantity, final_price):
    database = sqlite3.connect('vkusnyaha.db')
    cursor = database.cursor()
    try:
        cursor.execute('''
            INSERT INTO cart_products(cart_id, product_name, quantity, final_price)
            VALUES(?, ?, ?, ?)
        ''', (cart_id, product_name, quantity, final_price))
        database.commit()
        return True
    except:
        cursor.execute('''
        UPDATE cart_products
        SET quantity = ?,
        final_price = ?
        WHERE product_name = ? AND cart_id = ?
        ''', (quantity, final_price, product_name, cart_id))
        database.commit()
        return False
    finally:
        database.close()


def update_total_product_total_price(cart_id):
    database = sqlite3.connect("vkusnyaha.db")
    cursor = database.cursor()
    cursor.execute("""
    UPDATE carts
    SET total_products = (
        SELECT SUM(quantity) FROM cart_products
        WHERE cart_id = :cart_id
    ),
    total_price = (
        SELECT SUM(final_price) FROM cart_products
        WHERE cart_id = :cart_id
    )
    WHERE cart_id = :cart_id
    """, {'cart_id': cart_id})
    database.commit()
    database.close()


def get_cart_products(cart_id):
    database = sqlite3.connect('vkusnyaha.db')
    cursor = database.cursor()
    print('cart_id', cart_id)
    cursor.execute('''
    SELECT product_name, quantity, final_price
    FROM cart_products
    WHERE cart_id = ?
    ''', (cart_id,))
    cart_products = cursor.fetchall()
    print('cart_products', cart_products)
    database.close()
    return cart_products


def get_total_products_price(cart_id):
    database = sqlite3.connect('vkusnyaha.db')
    cursor = database.cursor()
    cursor.execute('''
    SELECT total_products, total_price FROM carts WHERE cart_id = ?
    ''', (cart_id,))
    data = cursor.fetchone()
    database.close()
    if data is None:
        total_products = 0
        total_price = 0
    else:
        total_products, total_price = data
    return total_products, total_price


def get_cart_products_for_delete(cart_id):
    database = sqlite3.connect('vkusnyaha.db')
    cursor = database.cursor()
    cursor.execute('''
    SELECT card_products_id, product_name FROM
    cart_products
    WHERE cart_id = ?
    ''', (cart_id,))
    cart_product = cursor.fetchall()
    database.close()
    return cart_product


def delete_cart_product_from(cart_product_id):
    database = sqlite3.connect('vkusnyaha.db')
    cursor = database.cursor()
    cursor.execute('''
    DELETE FROM cart_products WHERE card_products_id = ?
    ''', (cart_product_id,))
    database.commit()
    database.close()


def drop_cart_products_default(cart_id):
    database = sqlite3.connect('vkusnyaha.db')
    cursor = database.cursor()
    cursor.execute('''
    DELETE FROM cart_products WHERE cart_id = ?
    ''', (cart_id,))
    database.commit()
    database.close()


def order_total_price():
    database = sqlite3.connect('vkusnyaha.db')
    cursor = database.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders_total_price(
    orders_total_price_id INTEGER PRIMARY KEY AUTOINCREMENT,
    cart_id INTEGER REFERENCES carts(cart_id),
    total_price DECIMAL(12, 2) DEFAULT 0,
    total_products INTEGER  DEFAULT 0,
    time_now TEXT,
    new_date TEXT
    )
    ''')


def order():
    database = sqlite3.connect('vkusnyaha.db')
    cursor = database.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders(
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    orders_total_price_id INTEGER REFERENCES orders_total_price(orders_total_price_id),
    product_name VARCHAR(100) NOT NULL,
    quantity INTEGER NOT NULL,
    final_price DECIMAL(12, 2) NOT NULL
    )
    ''')


# order_total_price()
# order()


def save_order_total(cart_id, total_products, total_price, time_now, new_date):
    database = sqlite3.connect('vkusnyaha.db')
    cursor = database.cursor()
    cursor.execute('''
    INSERT INTO orders_total_price(cart_id, total_products, total_price, time_now, new_date)
    VALUES(?,?,?,?,?)
    ''', (cart_id, total_products, total_price, time_now, new_date))
    database.commit()
    database.close()


def orders_total_price_id(cart_id):
    database = sqlite3.connect('vkusnyaha.db')
    cursor = database.cursor()
    cursor.execute('''
    SELECT orders_total_price_id FROM orders_total_price
    WHERE cart_id = ?
    ''', (cart_id,))
    order_total_id = cursor.fetchall()[-1][0]
    database.close()
    return order_total_id


def save_order(orders_total_id, product_name, quantity, final_price):
    database = sqlite3.connect('vkusnyaha.db')
    cursor = database.cursor()
    cursor.execute('''
    INSERT INTO orders(orders_total_price_id, product_name, quantity, final_price)
    VALUES(?,?,?,?)
    ''', (orders_total_id, product_name, quantity, final_price))
    database.commit()
    database.close()


def get_orders_total_price(cart_id):
    database = sqlite3.connect('vkusnyaha.db')
    cursor = database.cursor()
    cursor.execute('''
    SELECT * FROM orders_total_price
    WHERE cart_id = ?
    ''', (cart_id,))
    orders_total_price = cursor.fetchall()
    database.close()
    return orders_total_price


def get_detail_product(id):
    database = sqlite3.connect('vkusnyaha.db')
    cursor = database.cursor()
    cursor.execute('''
    SELECT product_name, quantity, final_price FROM orders
    WHERE orders_total_price_id = ?
    ''', (id,))
    detail_product = cursor.fetchall()
    database.close()
    return detail_product
