from aiogram import executor, Bot, Dispatcher
from aiogram.types import Message, CallbackQuery, LabeledPrice
from aiogram import types
from translategram import PythonTelegramBotTranslator, MtranslateTranslatorService

from database import *
from keyboards import *
from datetime import datetime

TOKEN = '7095963759:AAFvmu63Zn0av5neQFdi7ixiOGb3GPcnT8Y'
PAYMENT = '398062629:TEST:999999999_F91D8F69C042267444B74CC0B3C747757EB0E065'

bot = Bot(TOKEN, parse_mode='HTML')

dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def command_start(message: Message):
    await message.answer(f'Здравствуйте{message.from_user.full_name}. Вас прветствует бот вкусняха')
    await register_user(message)


async def register_user(message: Message):
    chat_id = message.chat.id
    full_name = message.from_user.full_name
    user = first_select_user(chat_id)
    if user:
        await message.answer('Авторизация прошла успешно')
        await show_main_menu(message)
        insert_to_cart(chat_id)
    else:
        first_register_user(chat_id, full_name)
        await message.answer('Для регистрации поделитесь контактом', reply_markup=send_contact_button())


@dp.message_handler(content_types=['contact'])
async def finish_register_user(message: Message):
    chat_id = message.chat.id
    phone = message.contact.phone_number
    update_user_to_finish_register(chat_id, phone)
    await create_cart_for_user(message)
    await message.answer('Регистрация прошла успешна')
    await show_main_menu(message)


async def create_cart_for_user(message: Message):
    chat_id = message.chat.id
    try:
        insert_to_cart(chat_id)
    except:
        pass


async def show_main_menu(message: Message):
    await message.answer('Выберите направление', reply_markup=generate_main_menu())


# ----------------------------------------------------------------------------------


# @dp.message_handler(regexp=r'✔️ Сделать заказ')
@dp.message_handler(lambda message: '👟 Заказать' in message.text)
async def make_order(message: Message):
    await message.answer('Выберите категорию', reply_markup=generate_category_menu())


@dp.callback_query_handler(lambda call: 'category' in call.data)
async def show_products(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    _, category_id = call.data.split('_')
    category_id = int(category_id)
    await bot.edit_message_text('Выберите продукт: ', chat_id, message_id,
                                reply_markup=generate_products_by_category(category_id))


@dp.callback_query_handler(lambda call: 'main_menu' in call.data)
async def return_to_main_menu(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    await  bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                 text='Выберите категорию',
                                 reply_markup=generate_category_menu())


@dp.callback_query_handler(lambda call: 'product' in call.data)
async def show_detail_product(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    _, product_id = call.data.split('_')
    product_id = int(product_id)
    product = get_product_detail(product_id)
    cart_id = get_user_cart_id(chat_id)
    try:
        quantity = get_quantity(cart_id, product[1])
        if quantity is None:
            quantity = 0
    except:
        quantity = 0
    await bot.delete_message(chat_id, message_id)
    with open(product[-2], mode='rb') as img:
        await bot.send_photo(chat_id=chat_id, photo=img,
                             caption=f'''{product[1]}


Ингридиенты: {product[3]}

Цена: {product[2]}''', reply_markup=generate_product_detail_menu(product_id=product_id, category_id=product[-1],
                                                                 cart_id=cart_id, product=product[1], c=quantity))


@dp.callback_query_handler(lambda call: 'back' in call.data)
async def return_to_category(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    _, category_id = call.data.split('_')
    await bot.delete_message(chat_id, message_id)
    await bot.send_message(chat_id, 'Выберите продукт', reply_markup=generate_products_by_category(category_id))


@dp.callback_query_handler(lambda call: 'plus' in call.data)
async def add_product_cart(call: CallbackQuery):
    chat_id = call.message.chat.id
    _, quantity, product_id = call.data.split('_')
    quantity, product_id = int(quantity), int(product_id)
    quantity += 1
    message_id = call.message.message_id
    product = get_product_detail(product_id)
    cart_id = get_user_cart_id(chat_id)
    await bot.edit_message_caption(chat_id=chat_id, message_id=message_id, caption=f'''{product[1]}


Ингридиенты: {product[3]}

Цена: {product[2]}''', reply_markup=generate_product_detail_menu(product_id=product_id,
                                                                 category_id=product[-1],
                                                                 cart_id=cart_id, c=quantity))


@dp.callback_query_handler(lambda call: 'minus' in call.data)
async def remove_product_cart(call: CallbackQuery):
    chat_id = call.message.chat.id
    _, quantity, product_id = call.data.split('_')
    quantity, product_id = int(quantity), int(product_id)
    message_id = call.message.message_id
    product = get_product_detail(product_id)
    cart_id = get_user_cart_id(chat_id)
    if quantity <= 1:
        await bot.answer_callback_query(call.id, 'Ниже нуля нельзя')
        pass
    else:
        quantity -= 1
        await bot.edit_message_caption(chat_id=chat_id, message_id=message_id,
                                       caption=f'''{product[1]}


Ингридиенты: {product[3]}

Цена: {product[2]}''', reply_markup=generate_product_detail_menu(product_id=product_id,
                                                                 category_id=product[-1],
                                                                 cart_id=cart_id, c=quantity))


@dp.callback_query_handler(lambda call: 'cart' in call.data)
async def add_choose_product_to_cart(call: CallbackQuery):
    chat_id = call.message.chat.id
    _, product_id, quantity = call.data.split('_')
    product_id, quantity = int(product_id), int(quantity)
    print(product_id, quantity)
    product = get_product_detail(product_id)
    cart_id = get_user_cart_id(chat_id)
    final_price = product[2] * quantity

    if insert_or_update_cart_product(cart_id, product[1], quantity, final_price):
        await bot.answer_callback_query(call.id, 'Продукт успешно добавлен')
        print('final')

    else:
        await bot.answer_callback_query(call.id, 'Количество успешно изменено')


@dp.message_handler(regexp='🧺 Корзина')
async def show_cart(message: Message, edit_message: bool = False):
    chat_id = message.chat.id
    cart_id = get_user_cart_id(chat_id)

    try:
        update_total_product_total_price(cart_id)
    except:
        await message.answer('Корзина не доступна. Обратитесь в тех поддержку')
        return

    cart_products = get_cart_products(cart_id)
    total_products, total_price = get_total_products_price(cart_id)

    text = 'Ваша корзина \n\n'
    i = 0
    for product_name, quantity, final_price in cart_products:
        i += 1
        text += f'''{i}. {product_name}
Количество: {quantity}
Общая стоимость: {final_price}\n\n'''

    text += f'''Общая количество продуктов: {0 if total_products is None else total_products}
Общая стоимость счета: {0 if total_price is None else total_price}'''
    print(text)
    if edit_message:
        await bot.edit_message_text(text, chat_id, message.message_id, reply_markup=generate_cart_menu(cart_id))
    else:
        await bot.send_message(chat_id, text, reply_markup=generate_cart_menu(cart_id))


@dp.callback_query_handler(lambda call: 'delete' in call.data)
async def delete_cart_products(call: CallbackQuery):
    _, cart_product_id = call.data.split('_')
    cart_product_id = int(cart_product_id)
    message = call.message

    delete_cart_product_from(cart_product_id)

    await bot.answer_callback_query(call.id, text='Продукт успешно удалён')
    await show_cart(message, edit_message=True)


@dp.callback_query_handler(lambda call: 'order' in call.data)
async def create_order(call: CallbackQuery):
    chat_id = call.message.chat.id
    _, cart_id = call.data.split('_')
    cart_id = int(cart_id)

    time_now = datetime.now().strftime('%H:%M')
    new_date = datetime.now().strftime('%d.%m.%Y')

    cart_products = get_cart_products(cart_id)
    total_products, total_price = get_total_products_price(cart_id)

    save_order_total(cart_id, total_products, total_price, time_now, new_date)
    orders_total_id = orders_total_price_id(cart_id)

    text = 'Ваша корзина \n\n'
    i = 0
    for product_name, quantity, final_price in cart_products:
        i += 1
        text += f'''{i}. {product_name}
        Количество: {quantity}
        Общая стоимость: {final_price}\n\n'''

        save_order(orders_total_id, product_name, quantity, final_price)
    text += f'''Общая количество продуктов: {0 if total_products is None else total_products}
    Общая стоимость счета: {0 if total_price is None else total_price}'''

    await bot.send_invoice(
        chat_id=chat_id,
        title=f'Заказ #{cart_id}',
        description=text,
        payload='bot-defined invoice payload',
        provider_token=PAYMENT,
        currency='UZS',
        prices=[
            LabeledPrice(label='Общая стоимость', amount=int(total_price * 100)),
            LabeledPrice(label='Доставка', amount=1000000)
        ],
        start_parameter='start_parameter'
    )


@dp.pre_checkout_query_handler(lambda query: True)
async def checkout(pre_checkout_query):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True, error_message='Ошибка оплаты не прошла')


@dp.message_handler(content_types=['successful_payment'])
async def get_payment(message: Message):
    chat_id = message.chat.id
    cart_id = get_user_cart_id(chat_id)
    await bot.send_message(chat_id, 'Ура оплата прошла успешно. Ожидайте свой заказ')
    drop_cart_products_default(cart_id)


@dp.message_handler(lambda message: '📓 История' in message.text)
async def show_history_orders(message: Message):
    chat_id = message.chat.id
    cart_id = get_user_cart_id(chat_id)
    orders_total_price = get_orders_total_price(cart_id)
    print(orders_total_price)
    for i in orders_total_price:
        text = f'''Дата заказа{i[-1]}
Время заказа: {i[-2]}
Общая количество: {i[3]}
Сумма счета: {i[2]}\n\n'''
        detail_product = get_detail_product(i[0])

        for j in detail_product:
            text += f'''
Продукт: {j[0]}
Количество: {j[1]}
Общая стоимость {j[2]}'''
            await bot.send_message(chat_id, text)


@dp.message_handler(lambda message: message.text == '⚙️ Настройки')
async def process_settings(message: types.Message):
    settings_keyboard = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("Связаться с поддержкой", callback_data='contact_support')
    )
    await bot.send_message(message.chat.id, "Выберите действие:", reply_markup=settings_keyboard)


@dp.callback_query_handler(lambda c: c.data == 'contact_support')
async def process_contact_support(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    # Отправка контактной информации поддержки
    support_message = """
    📞 **Контактная информация поддержки:**

    - Телефон: +1 234 567 890
    - Электронная почта: support@example.com

    Пожалуйста, не стесняйтесь обращаться к нам, если у вас возникнут вопросы или проблемы!
    """
    await bot.send_message(callback_query.from_user.id, support_message, parse_mode='Markdown')


executor.start_polling(dp)
