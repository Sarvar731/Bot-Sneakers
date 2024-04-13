from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from database import *


def send_contact_button():
    return ReplyKeyboardMarkup([
        [KeyboardButton(text='Поделиться контактом', request_contact=True)]
    ], resize_keyboard=True)


def generate_main_menu():
    return ReplyKeyboardMarkup([
        [KeyboardButton(text='👟 Заказать')],
        [KeyboardButton(text='📓 История'), KeyboardButton(text='🧺 Корзина'), KeyboardButton(text='⚙️ Настройки'), ]
    ], resize_keyboard=True)


def generate_category_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    categories = get_all_categories()
    buttons = []
    for category in categories:
        btn = InlineKeyboardButton(text=category[1], callback_data=f'category_{category[0]}')
        buttons.append(btn)

    markup.add(*buttons)
    return markup


def generate_products_by_category(category_id):
    markup = InlineKeyboardMarkup(row_width=2)
    products = get_products_by_category_id(category_id)
    buttons = []
    for product in products:
        btn = InlineKeyboardButton(text=product[1], callback_data=f'product_{product[0]}')
        buttons.append(btn)
    markup.add(*buttons)
    markup.row(
        InlineKeyboardButton(text='🔙 Назад', callback_data='main_menu')
    )

    return markup


def generate_product_detail_menu(product_id, category_id, cart_id, product='', c=1):
    markup = InlineKeyboardMarkup(row_width=3)
    try:
        quantity = get_quantity(cart_id, product)

    except:
        quantity = c
        print(quantity)

    buttons = []
    btn_minus = InlineKeyboardButton(text=str('➖'), callback_data=f'minus_{quantity}_{product_id}')
    btn_quantity = InlineKeyboardButton(text=str(quantity), callback_data=f'coll')
    btn_plus = InlineKeyboardButton(text=str('➕'), callback_data=f'plus_{quantity}_{product_id}')
    buttons.append(btn_minus)
    buttons.append(btn_quantity)
    buttons.append(btn_plus)
    markup.add(*buttons)
    markup.row(
        InlineKeyboardButton(text='Добавить в корзину', callback_data=f'cart_{product_id}_{quantity}')
    )
    markup.row(
        InlineKeyboardButton(text='Назад', callback_data=f'back_{category_id}')
    )
    return markup



def generate_cart_menu(cart_id):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(text='Оформить заказ', callback_data=f'order_{cart_id}')
    )
    cart_products = get_cart_products_for_delete(cart_id)
    for cart_product_id, product_name in cart_products:
        markup.row(
            InlineKeyboardButton(text=f'❌ {product_name}', callback_data=f'delete_{cart_product_id}')
        )
    return markup