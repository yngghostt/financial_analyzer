import telebot

import plot
import qr
import tableform
from keyboards import *

# Тело телеграм бота

API = 'YOUR_IP_HERE'
bot = telebot.TeleBot(API)

temp_dict = {}


# Команды бота

@bot.message_handler(commands=['start'])
def command_start(message):
    """
    Команда /start
    :param message: Объект сообщения
    """
    module.add_user(message.chat.username, message.chat.id)
    start_keyboard = get_start_keyboard()
    bot.send_message(message.chat.id, f'Приветствую, {message.chat.username}! '
                                      f'Я помогу учитывать доходы и расходы\n'
                                      f'Я умею:\n'
                                      f'* Добавлять доходы и расходы\n'
                                      f'* Считывать QR коды чеков\n'
                                      f'* Выводить различную статистику \n'
                                      f'* Отправлять инфографику и таблицы \n'
                                      f'Для работы со мной перейдите в меню\n'
                                      f'/help - помощь и обратная связь', reply_markup=start_keyboard)


@bot.message_handler(commands=['menu'])
def command_menu(message):
    """
    Команда /menu
    :param message: Объект сообщения
    """
    menu_keyboard = get_menu_keyboard()
    bot.send_message(message.chat.id, '📋 Меню бота\n'
                                      'Выберете действие:\n'
                                      '* Для добавления расхода нажмите "Добавить" и введите нужную информацию\n'
                                      '* Для получения статистики нажмите "Меню" статистики и выберете нужную '
                                      'статистику\n',
                     reply_markup=menu_keyboard)


@bot.message_handler(commands=['add'])
def command_add(message):
    """
    Команда /add
    :param message: Объект сообщения
    """
    plus_minus_keyboard = get_plus_minus_keyboard()
    bot.send_message(chat_id=message.chat.id,
                     text='Что вы хотите добавить?', reply_markup=plus_minus_keyboard)


@bot.message_handler(commands=['statistics'])
def command_statistics(message):
    """
    Команда /statistics
    :param message: Объект сообщения
    """
    statistics_keyboard = get_statistics_keyboard()
    bot.send_message(chat_id=message.chat.id,
                     text='📈 Меню статистики\n',
                     reply_markup=statistics_keyboard)


@bot.message_handler(commands=['help'])
def command_help(message):
    """
    Команда /help
    :param message: Объект сообщения
    """
    bot.send_message(message.chat.id, 'Помощь\n'
                                      'Для работы с ботом используйте меню и клавиатуру\n'
                                      '* Добавить: добавление нового дохода или расхода с соответствующими '
                                      'параметрами\n '
                                      '* Меню статистики: '
                                      '   Общая статистика возвращает таблицу формата .xlsx с расходами и доходами за '
                                      'выбранный период\n '
                                      '   Статистика по категориям возвращает инфорграфику, показывающую расходы по '
                                      'категорями за выбранный период\n'
                                      'Бот поддерживает использование команд\n'
                                      '/start - начало работы с ботом, переход в меню\n'
                                      '/menu - вызов сообщения меню бота \n'
                                      '/add - вызов функции добавления расхода или дохода\n'
                                      '/statistics - вызов сообщения с меню статистики \n')


# Функции добавления расхода или дохода


def process_name_step(message):
    """
    Добавление имени позиции
    :param message: Объект сообщения
    """
    if message.content_type == 'text':
        temp_dict[message.chat.id].name = message.text
        position_type = temp_dict[message.chat.id].type
        categories_keyboard = get_categories_keyboard(position_type)
        bot.send_message(message.chat.id, '🗂 Выберете категорию из списка:', reply_markup=categories_keyboard)
    elif message.content_type == 'document' or message.content_type == 'photo':
        if message.content_type == 'photo':
            photo_id = message.photo[0].file_id
        if message.content_type == 'document':
            if not message.document.mime_type.split('/')[0] == 'image':
                reply = bot.send_message(message.chat.id, '‼ Ошибка при распознании QR кода. Пришлите именно фото '
                                                          'QR кода или используйте ручной ввод')
                bot.register_next_step_handler(reply, process_name_step)
                return
            photo_id = message.document.file_id

        bot.send_message(message.chat.id, 'Подождите, идёт обработка...')
        file_info = bot.get_file(photo_id)
        downloaded_file = bot.download_file(file_info.file_path)
        path = 'userfiles/qr/' + str(message.chat.id) + '.jpg'
        with open(path, 'wb') as new_file:
            new_file.write(downloaded_file)
        info = qr.read_qr(path)

        if info is None:
            reply = bot.send_message(message.chat.id, '‼ Ошибка при распознании QR кода. Пришлите чёткое фото самого '
                                                      'кода или попробуйте ручной ввод')
            bot.register_next_step_handler(reply, process_name_step)
            return
        temp_dict[message.chat.id].type = 'expense'
        temp_dict[message.chat.id].day = info[0]
        temp_dict[message.chat.id].month = info[1]
        temp_dict[message.chat.id].year = info[2]
        temp_dict[message.chat.id].price = info[3]

        reply = bot.send_message(message.chat.id, '✅ Код успешно распознан.\nВведите название расхода:')
        bot.register_next_step_handler(reply, process_name_step)
    else:
        reply = bot.send_message(message.chat.id,
                                 '‼ Ошибка при распознании QR кода. '
                                 'Пришлите фотографию QR кода фотографией или документом')
        bot.register_next_step_handler(reply, process_name_step)


def process_price_step(message):
    """
    Добавление стоимости позиции
    :param message: Объект сообщения
    """
    try:
        temp_dict[message.chat.id].price = float(message.text.replace(',', '.'))
        if float(message.text) <= 0:
            reply = bot.send_message(message.chat.id, "Введено не положительное число, введите цену корректно")
            bot.register_next_step_handler(reply, process_price_step)
            return

    except ValueError:
        reply = bot.send_message(message.chat.id, "Введено не число, введите цену корректно")
        bot.register_next_step_handler(reply, process_price_step)
        return
    date_keyboard = get_date_keyboard()
    bot.send_message(message.chat.id, "📅 Выберете дату", reply_markup=date_keyboard)


def process_confirm_step(message):
    """
    Подтверждение добавления позиции
    :param message: Объект сообщения
    """
    confirm_keyboard = get_confirm_keyboard()
    position = temp_dict[message.chat.id]
    if position.type == 'income':
        bot.send_message(
            message.chat.id,
            f'ℹ️Информация о доходе:\n'
            f'Название: {position.name}\n'
            f'Сумма:  {round(position.price, 2)} руб\n'
            f'Категория: '
            f'{module.get_category_name(position.category_id, position.type)}\n '
            f'Дата: {position.day}/'
            f'{position.month}/'
            f'{position.year}\n'
            f'Всё ли верно?', reply_markup=confirm_keyboard)

    if position.type == 'expense':
        bot.send_message(
            message.chat.id,
            f'ℹ️Информация о расходе:\n'
            f'Название: {position.name}\n'
            f'Цена: {round(position.price, 2)} руб\n'
            f'Категория: '
            f'{module.get_category_name(position.category_id, position.type)}\n '
            f'Дата: {position.day}/'
            f'{position.month}/'
            f'{position.year}\n'
            f'Всё ли верно?', reply_markup=confirm_keyboard)


# Функции обработки callback для Inline клавиатур


@bot.callback_query_handler(func=lambda call: call.data == 'menu')
def call_menu(call):
    """
    Вызов меню
    :param call: Объект вызова Inline клавиатуры
    """
    bot.answer_callback_query(callback_query_id=call.id)
    menu_keyboard = get_menu_keyboard()
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text='📋 Меню бота\n'
                               'Выберете действие:\n'
                               '* Для добавления расхода нажмите "Добавить" и введите нужную информацию\n'
                               '* Для получения статистики нажмите "Меню" статистики и выберете нужную '
                               'статистику\n', reply_markup=menu_keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'to_menu')
def call_to_menu(call):
    """
    Возврат к меню
    :param call: Объект вызова Inline клавиатуры
    """
    bot.answer_callback_query(callback_query_id=call.id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
    del temp_dict[call.message.chat.id]
    command_menu(call.message)


@bot.callback_query_handler(func=lambda call: call.data == 'add')
def call_add(call):
    """
    Добавление позиции
    :param call: Объект вызова Inline клавиатуры
    """
    bot.answer_callback_query(callback_query_id=call.id)
    plus_minus_keyboard = get_plus_minus_keyboard()
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text='Что вы хотите добавить?', reply_markup=plus_minus_keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'income')
def call_income(call):
    """
    Добавление дохода
    :param call: Объект вызова Inline клавиатуры
    """
    bot.answer_callback_query(callback_query_id=call.id)
    position = module.Account(type='income', user_id=module.get_user_id(call.message.chat.id))
    temp_dict[call.message.chat.id] = position
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "📝 Введите наименование дохода")
    bot.register_next_step_handler(call.message, process_name_step)


@bot.callback_query_handler(func=lambda call: call.data == 'expense')
def call_expense(call):
    """
    Добавление расхода
    :param call: Объект вызова Inline клавиатуры
    """
    bot.answer_callback_query(callback_query_id=call.id)
    position = module.Account(type='expense', user_id=module.get_user_id(call.message.chat.id))
    temp_dict[call.message.chat.id] = position
    bot.send_message(call.message.chat.id, "📝 Введите наименование расхода или пришлите фотографию QR кода на чеке")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
    bot.register_next_step_handler(call.message, process_name_step)


@bot.callback_query_handler(func=lambda call: str(call.data).isdigit())
def callback_category(call):
    """
    Выбор категории
    :param call: Объект вызова Inline клавиатуры
    """
    bot.answer_callback_query(callback_query_id=call.id)
    id = -1
    position_type = temp_dict[call.message.chat.id].type

    categories = module.get_categories(position_type)
    for i in range(len(categories)):
        if str(call.data) == str(i):
            id = i + 1
            break
    temp_dict[call.message.chat.id].category_id = id
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
    if temp_dict[call.message.chat.id].price is not None:
        process_confirm_step(call.message)
    else:
        bot.send_message(call.message.chat.id, "💰 Введите сумму")
        bot.register_next_step_handler(call.message, process_price_step)


@bot.callback_query_handler(func=lambda call: call.data == 'today')
def callback_today(call):
    """
    Выбор "сегодня" в выборе времени
    :param call: Объект вызова Inline клавиатуры
    """
    bot.answer_callback_query(callback_query_id=call.id)
    date = datetime.datetime.today().strftime("%d/%m/%Y").split("/")
    temp_dict[call.message.chat.id].day = int(date[0])
    temp_dict[call.message.chat.id].month = int(date[1])
    temp_dict[call.message.chat.id].year = int(date[2])
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
    process_confirm_step(call.message)


@bot.callback_query_handler(func=lambda call: call.data == 'yesterday')
def callback_yesterday(call):
    """
    Выбор "вчера" в выборе времени
    :param call: Объект вызова Inline клавиатуры
    """
    bot.answer_callback_query(callback_query_id=call.id)
    date = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime("%d/%m/%Y").split("/")
    temp_dict[call.message.chat.id].day = int(date[0])
    temp_dict[call.message.chat.id].month = int(date[1])
    temp_dict[call.message.chat.id].year = int(date[2])
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
    process_confirm_step(call.message)


@bot.callback_query_handler(func=lambda call: call.data == 'other')
def callback_other(call):
    """
    Выбор иной даты и вызов календаря
    :param call: Объект вызова Inline клавиатуры
    """
    bot.answer_callback_query(callback_query_id=call.id)
    calendar_keyboard = get_calendar_keyboard()
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=calendar_keyboard)


@bot.callback_query_handler(func=lambda call: str(call.data).split(";")[0] == 'ignore')
def callback_calendar_ignore(call):
    """
    Пустые клопки для календаря
    :param call: Объект вызова Inline клавиатуры
    """
    bot.answer_callback_query(callback_query_id=call.id)


@bot.callback_query_handler(func=lambda call: str(call.data).split(";")[0] == 'day')
def callback_calendar_day(call):
    """
    Выбор даты на календаре
    :param call: Объект вызова Inline клавиатуры
    """
    bot.answer_callback_query(callback_query_id=call.id)
    date = str(call.data).split(';')
    temp_dict[call.message.chat.id].day = int(date[1])
    temp_dict[call.message.chat.id].month = int(date[2])
    temp_dict[call.message.chat.id].year = int(date[3])
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
    process_confirm_step(call.message)


@bot.callback_query_handler(func=lambda call: str(call.data).split(";")[0] == 'prev_month')
def callback_calendar_prev_month(call):
    """
    Вызов прерыдушего месяца на календаре
    :param call: Объект вызова Inline клавиатуры
    """
    bot.answer_callback_query(callback_query_id=call.id)
    date = str(call.data).split(';')
    current = datetime.datetime(int(date[3]), int(date[2]), 1)
    prev = current - datetime.timedelta(days=1)
    bot.edit_message_text(text=call.message.text,
                          chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          reply_markup=get_calendar_keyboard(int(prev.year), int(prev.month)))


@bot.callback_query_handler(func=lambda call: str(call.data).split(";")[0] == 'next_month')
def callback_calendar_next_month(call):
    """
    Вызов следуюшего месяца на календаре
    :param call: Объект вызова Inline клавиатуры
    """
    bot.answer_callback_query(callback_query_id=call.id)
    date = str(call.data).split(';')
    current = datetime.datetime(int(date[3]), int(date[2]), 1)
    nex = current + datetime.timedelta(days=31)
    bot.edit_message_text(text=call.message.text,
                          chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          reply_markup=get_calendar_keyboard(int(nex.year), int(nex.month)))


@bot.callback_query_handler(func=lambda call: call.data == 'confirm')
def callback_confirm(call):
    """
    Подтверждение информации о позиции
    :param call: Объект вызова Inline клавиатуры
    """
    bot.answer_callback_query(callback_query_id=call.id)
    position = temp_dict[call.message.chat.id]
    module.add_position(position)
    if position.type == 'income':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f'ℹ️Информация о доходе:\n'
                                   f'Название: {position.name}\n'
                                   f'Сумма:  {round(position.price, 2)} руб\n'
                                   f'Категория: '
                                   f'{module.get_category_name(position.category_id, position.type)}\n '
                                   f'Дата: {position.day}/'
                                   f'{position.month}/'
                                   f'{position.year}\n'
                                   f'---\n'
                                   f'✅ Доход успешно добавлен')
    if position.type == 'expense':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f'ℹ️Информация о расходе:\n'
                                   f'Название: {position.name}\n'
                                   f'Цена: {round(position.price, 2)} руб\n'
                                   f'Категория: '
                                   f'{module.get_category_name(position.category_id, position.type)}\n '
                                   f'Дата: {position.day}/'
                                   f'{position.month}/'
                                   f'{position.year}\n'
                                   f'---\n'
                                   f'✅ Расход успешно добавлен')

    del temp_dict[call.message.chat.id]
    command_menu(call.message)


@bot.callback_query_handler(func=lambda call: call.data == 'cancel')
def callback_cancel(call):
    """
    Отмена добавления позиции
    :param call: Объект вызова Inline клавиатуры
    """
    bot.answer_callback_query(callback_query_id=call.id)
    position = temp_dict[call.message.chat.id]
    if position.type == 'income':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f'ℹ️Информация о доходе:\n'
                                   f'Название: {position.name}\n'
                                   f'Сумма:  {round(position.price, 2)} руб\n'
                                   f'Категория: '
                                   f'{module.get_category_name(position.category_id, position.type)}\n '
                                   f'Дата: {position.day}/'
                                   f'{position.month}/'
                                   f'{position.year}\n'
                                   f'---\n'
                                   f'🚫 Отмена')
    if position.type == 'expense':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f'ℹ️Информация о расходе:\n'
                                   f'Название: {position.name}\n'
                                   f'Цена: {round(position.price, 2)} руб\n'
                                   f'Категория: '
                                   f'{module.get_category_name(position.category_id, position.type)}\n '
                                   f'Дата: {position.day}/'
                                   f'{position.month}/'
                                   f'{position.year}\n'
                                   f'---\n'
                                   f'🚫 Отмена')
    del temp_dict[call.message.chat.id]
    command_menu(call.message)


@bot.callback_query_handler(func=lambda call: call.data == 'statistics')
def callback_statistic(call):
    """
    Вызов меню статистики
    :param call: Объект вызова Inline клавиатуры
    """
    bot.answer_callback_query(callback_query_id=call.id)
    statistics_keyboard = get_statistics_keyboard()
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text='📈 Меню статистики\n',
                          reply_markup=statistics_keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'income_statistics' or call.data == 'expense_statistics')
def callback_positions_type_statistics(call):
    """
    Выбор типа статистики
    :param call: Объект вызова Inline клавиатуры
    """
    bot.answer_callback_query(callback_query_id=call.id)
    positions_type = call.data.split('_')[0]
    temp_dict[call.message.chat.id] = module.StatisticsRequest(positions_type=positions_type)
    statistics_types_keyboard = get_statistics_keyboard_types()
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  reply_markup=statistics_types_keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'default_statistics' or call.data == 'categories_statistics')
def callback_request_type_statistics(call):
    """
    Выбор периода статистики
    :param call: Объект вызова Inline клавиатуры
    """
    bot.answer_callback_query(callback_query_id=call.id)
    temp_dict[call.message.chat.id].request_type = call.data
    positions_type = temp_dict[call.message.chat.id].positions_type
    statistics_period_keyboard = get_statistics_period_keyboard(positions_type + '_statistics')
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  reply_markup=statistics_period_keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'month')
def callback_month(call):
    """
    Выбор месяца для показа статистики
    :param call: Объект вызова Inline клавиатуры
    """
    now = datetime.datetime.now()
    bot.answer_callback_query(callback_query_id=call.id)
    statistics_type = temp_dict[call.message.chat.id].request_type
    month_keyboard = get_month_slider(statistics_type, now.year, now.month)
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  reply_markup=month_keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'all_time')
def callback_all_time(call):
    """
    Вывод статистики за всё время
    :param call: Объект вызова Inline клавиатуры
    """
    bot.answer_callback_query(callback_query_id=call.id)
    statistics_request = temp_dict[call.message.chat.id]
    all_price, all_count = module.get_positions(call.message.chat.id, statistics_request.positions_type)
    word = ''
    if statistics_request.positions_type == 'income':
        word = 'доход'
    if statistics_request.positions_type == 'expense':
        word = 'расход'

    if statistics_request.request_type == 'default_statistics':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f'📊 Cтатистика {word}ов за всё время:\n'
                                   f'---\n'
                                   f'Всего {word}ов: {all_count}\n'
                                   f'Сумма {word}ов: {all_price} руб.\n'
                                   f'Средний {word}: {module.get_medium(all_price, all_count)}')
        if not all_count == 0:
            tableform.form_table(call.message.chat.id, module.get_data(call.message.chat.id,
                                                                       statistics_request.positions_type))

            table = open(f'userfiles/tables/{call.message.chat.id}.xlsx', 'rb')
            bot.send_document(call.message.chat.id, table)

    if statistics_request.request_type == 'categories_statistics':
        categories_dict = module.get_categories_positions(call.message.chat.id, statistics_request.positions_type)
        message = ''
        for i in categories_dict.keys():
            pr = module.get_medium(categories_dict[i][0], all_price)
            if not pr == '-':
                pr *= 100

            message += i + ': ' + str(round(categories_dict[i][0], 2)) + 'руб. (' + str(round(pr, 2)) + '%)\n'

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f'📊 Cтатистика {word}ов за всё время: \n' + message + '---\n' + f'Всего {word}ов: {all_count}\n' + f'Cумма {word}ов: {all_price}')
        if not all_count == 0:
            prices = []
            for i in list(categories_dict.values()):
                prices.append(i[0])
            plot.create_pie_diagram(call.message.chat.id, list(categories_dict.keys()), prices)
            pie = open(f'userfiles/statistics/{call.message.chat.id}pie.png', 'rb')
            bot.send_photo(chat_id=call.message.chat.id, photo=pie)

            counts = []
            for i in list(categories_dict.values()):
                counts.append(i[1])
            plot.create_barh_diagram(call.message.chat.id, list(categories_dict.keys()), counts)
            barh = open(f'userfiles/statistics/{call.message.chat.id}barh.png', 'rb')

            bot.send_photo(chat_id=call.message.chat.id, photo=barh)

    statistics_period_keyboard = get_statistics_period_keyboard(statistics_request.positions_type + '_statistics')
    bot.send_message(call.message.chat.id, '📈 Меню статистики', reply_markup=statistics_period_keyboard)


@bot.callback_query_handler(func=lambda call: str(call.data).split(";")[0] == 'current_month')
def callback_current_month(call):
    """
    Вывод статистики за месяц
    :param call: Объект вызова Inline клавиатуры
    """
    bot.answer_callback_query(callback_query_id=call.id)
    statistics_request = temp_dict[call.message.chat.id]
    date = str(call.data).split(';')
    statistics_request.month = date[1]
    statistics_request.year = date[2]
    all_price, all_count = module.get_positions(call.message.chat.id, statistics_request.positions_type,
                                                statistics_request.month, statistics_request.year)
    word = ''
    if statistics_request.positions_type == 'income':
        word = 'доход'
    if statistics_request.positions_type == 'expense':
        word = 'расход'

    if statistics_request.request_type == 'default_statistics':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f'📊 Cтатистика за {word}ов за {module.month_name(int(statistics_request.month))} '
                                   f'{statistics_request.year}:\n '
                                   f'---\n'
                                   f'Всего {word}ов: {all_count} \n'
                                   f'Сумма {word}ов: {all_price} руб.\n'
                                   f'Средний {word}: {module.get_medium(all_price, all_count)}')
        if not all_count == 0:
            tableform.form_table(call.message.chat.id, module.get_data(call.message.chat.id,
                                                                       statistics_request.positions_type,
                                                                       statistics_request.month,
                                                                       statistics_request.year))

            table = open(f'userfiles/tables/{call.message.chat.id}.xlsx', 'rb')
            bot.send_document(call.message.chat.id, table)

    if statistics_request.request_type == 'categories_statistics':
        categories_dict = module.get_categories_positions(call.message.chat.id, statistics_request.positions_type,
                                                          statistics_request.month, statistics_request.year)
        message = ''
        for i in categories_dict.keys():
            pr = module.get_medium(categories_dict[i][0], all_price)
            if not pr == '-':
                pr = round(pr * 100, 2)

            message += i + ': ' + str(categories_dict[i][0]) + 'руб. (' + str(pr) + '%)\n'

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f'📊 Cтатистика {word}ов за {module.month_name(int(statistics_request.month))} '
                                   f'{statistics_request.year}:\n' + message + '---\n' + f'Всего {word}ов: {all_count}\n' + f'Cумма {word}ов: {all_price}')
        if not all_count == 0:
            prices = []
            for i in list(categories_dict.values()):
                prices.append(i[0])
            plot.create_pie_diagram(call.message.chat.id, list(categories_dict.keys()), prices)
            pie = open(f'userfiles/statistics/{call.message.chat.id}pie.png', 'rb')
            bot.send_photo(chat_id=call.message.chat.id, photo=pie)

            counts = []
            for i in list(categories_dict.values()):
                counts.append(i[1])
            plot.create_barh_diagram(call.message.chat.id, list(categories_dict.keys()), counts)
            barh = open(f'userfiles/statistics/{call.message.chat.id}barh.png', 'rb')

            bot.send_photo(chat_id=call.message.chat.id, photo=barh)

    month_slider = get_month_slider(statistics_request.request_type)
    bot.send_message(call.message.chat.id, text='📈 Меню статистики', reply_markup=month_slider)


@bot.callback_query_handler(func=lambda call: str(call.data).split(";")[0] == 'prev_slide')
def callback_prev_slide(call):
    """
    Пердыдущий месяц в выборе месяца
    :param call: Объект вызова Inline клавиатуры
    """
    bot.answer_callback_query(callback_query_id=call.id)
    date = str(call.data).split(';')
    current = datetime.datetime(int(date[2]), int(date[1]), 1)
    prev = current - datetime.timedelta(days=1)
    statistics_type = temp_dict[call.message.chat.id].request_type
    bot.edit_message_text(text=call.message.text,
                          chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          reply_markup=get_month_slider(statistics_type, int(prev.year), int(prev.month)))


@bot.callback_query_handler(func=lambda call: str(call.data).split(";")[0] == 'next_slide')
def callback_next_slide(call):
    """
    Следуюший месяц в выборе месяца
    :param call: Объект вызова Inline клавиатуры
    """
    bot.answer_callback_query(callback_query_id=call.id)
    date = str(call.data).split(';')
    print(date)
    current = datetime.datetime(int(date[2]), int(date[1]), 1)
    nex = current + datetime.timedelta(days=31)
    statistics_type = temp_dict[call.message.chat.id].request_type
    bot.edit_message_text(text=call.message.text,
                          chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          reply_markup=get_month_slider(statistics_type, int(nex.year), int(nex.month)))


bot.enable_save_next_step_handlers()
bot.load_next_step_handlers()

if __name__ == '__main__':
    bot.polling()
