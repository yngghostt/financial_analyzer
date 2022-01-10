import calendar
import datetime

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import module


def get_start_keyboard() -> InlineKeyboardMarkup:
    """
    Вывод стартовой клавиатуры для приветственного сообщения
    :return: Стартовая клавиатура с переходом к меню
    """
    start_keyboard = InlineKeyboardMarkup()
    menu = InlineKeyboardButton('📋 Меню', callback_data='menu')
    start_keyboard.add(menu)

    return start_keyboard


def get_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Вывод клаиватуры меню
    :return: Клавиатура меню
    """
    menu_keyboard = InlineKeyboardMarkup(row_width=1)
    position = InlineKeyboardButton('↪ Добавить', callback_data='add')
    statistics = InlineKeyboardButton('📈 Меню статистики', callback_data='statistics')
    menu_keyboard.add(position, statistics)

    return menu_keyboard


def get_plus_minus_keyboard() -> InlineKeyboardMarkup:
    """
    Вывод клаиватуры выбора типа позиции
    :return: Клавиатура для выбора дохода или расхода
    """
    plus_minus_keyboard = InlineKeyboardMarkup(row_width=2)
    plus_button = InlineKeyboardButton("➕ Доход", callback_data='income')
    minus_button = InlineKeyboardButton("➖ Расход", callback_data='expense')
    back = InlineKeyboardButton('⬅ Назад', callback_data='menu')
    plus_minus_keyboard.add(plus_button, minus_button, back)

    return plus_minus_keyboard


def get_categories_keyboard(position_type: str) -> InlineKeyboardMarkup:
    """
    Вывод клаиватуры выбора категории
    :return: Клавиатура с категориями
    """
    categories_keyboard = InlineKeyboardMarkup(row_width=1)
    categories = module.get_categories(position_type)
    for id in range(len(categories)):
        category = InlineKeyboardButton(str(categories[id][0]), callback_data=str(id))
        categories_keyboard.add(category)

    return categories_keyboard


def get_date_keyboard() -> InlineKeyboardMarkup:
    """
    Вывод клаиватуры для выбора даты
    :return: Клавиатура выбора даты
    """
    date_keyboard = InlineKeyboardMarkup(row_width=3)
    today = InlineKeyboardButton("Сегодня", callback_data='today')
    yesterday = InlineKeyboardButton("Вчера", callback_data='yesterday')
    other = InlineKeyboardButton('Другой день', callback_data='other')
    date_keyboard.add(today, yesterday, other)

    return date_keyboard


def get_confirm_keyboard() -> InlineKeyboardMarkup:
    """
    Вывод клаиватуры подтверждения информации о позиции
    :return: Клавиатура для подтверждения
    """
    confirm_keyboard = InlineKeyboardMarkup(row_width=2)
    yes = InlineKeyboardButton("Да", callback_data='confirm')
    no = InlineKeyboardButton("Отмена", callback_data='cancel')
    confirm_keyboard.add(yes, no)

    return confirm_keyboard


def get_calendar_keyboard(year=None, month=None) -> InlineKeyboardMarkup:
    """
    Вывод клаиватуры с календарём для выбора даты
    :return: Клавиатура календаря
    """
    now = datetime.datetime.now()
    if year is None:
        year = now.year
    if month is None:
        month = now.month
    keyboard = []
    row1 = [InlineKeyboardButton(module.month_name(month) + " " + str(year),
                                 callback_data=";".join(['ignore', str(0), str(month), str(year)]))]
    keyboard.append(row1)
    row2 = []
    for day in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]:
        row2.append(InlineKeyboardButton(day,
                                         callback_data=";".join(['ignore', str(day), str(month), str(year)])))
    keyboard.append(row2)

    my_calendar = calendar.monthcalendar(year, month)
    for week in my_calendar:
        row3 = []
        for day in week:
            if day == 0:
                row3.append(InlineKeyboardButton(" ",
                                                     callback_data=";".join(
                                                         ['ignore', str(day), str(month), str(year)])))
            else:
                row3.append(InlineKeyboardButton(str(day),
                                                     callback_data=";".join(['day', str(day), str(month), str(year)])))
        keyboard.append(row3)

    row4 = [InlineKeyboardButton("<",
                                 callback_data=";".join(['prev_month', str(1), str(month), str(year)])),
            InlineKeyboardButton(" ",
                                 callback_data=";".join(['ignore', str(0), str(month), str(year)])),
            InlineKeyboardButton(">",
                                 callback_data=";".join(['next_month', str(1), str(month), str(year)]))]
    keyboard.append(row4)

    return InlineKeyboardMarkup(keyboard)


def get_statistics_keyboard() -> InlineKeyboardMarkup:
    """
    Вывод клаиватуры меню статистики
    :return: Клавиатура меню статистики
    """
    statistics_keyboard = InlineKeyboardMarkup(row_width=2)
    default = InlineKeyboardButton('Статистика доходов', callback_data='income_statistics')
    categories = InlineKeyboardButton('Статистика расходов', callback_data='expense_statistics')
    back = InlineKeyboardButton('⬅ Назад️', callback_data='menu')
    statistics_keyboard.add(default, categories, back)

    return statistics_keyboard


def get_statistics_keyboard_types() -> InlineKeyboardMarkup:
    """
    Вывод клаиватуры статистики с типами
    :return: Клавиатура меню статистики
    """
    statistics_keyboard = InlineKeyboardMarkup(row_width=2)
    default = InlineKeyboardButton('Общая статистика', callback_data='default_statistics')
    categories = InlineKeyboardButton('По категориям', callback_data='categories_statistics')
    back = InlineKeyboardButton('⬅ Назад️', callback_data='statistics')
    statistics_keyboard.add(default, categories, back)

    return statistics_keyboard


def get_statistics_period_keyboard(positions_type: str) -> InlineKeyboardMarkup:
    """
    Вывод клавиатуры периода показа статистики
    :param positions_type: Тип позиций для показа статисики
    :return: Клаиватура для выбора периода
    """
    period_keyboard = InlineKeyboardMarkup(row_width=2)
    all_time = InlineKeyboardButton('За всё время', callback_data='all_time')
    month = InlineKeyboardButton('За месяц', callback_data='month')
    back = InlineKeyboardButton('⬅ Назад️', callback_data=positions_type)

    period_keyboard.add(all_time, month, back)

    return period_keyboard


def get_month_slider(request_type: str, year=None, month=None) -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора месяца для показа статистики
    :param request_type: Тип запрашиваемой статистики
    :param year: Год
    :param month: Месяц
    :return: Клаиватура для выбора месяца
    """
    now = datetime.datetime.now()
    if year is None:
        year = now.year
    if month is None:
        month = now.month
    month_slider = InlineKeyboardMarkup(row_width=3)
    prev = InlineKeyboardButton('<<', callback_data=";".join(['prev_slide', str(month), str(year)]))
    empty = InlineKeyboardButton(module.month_name(int(month)) + " " + str(year),
                                 callback_data=";".join(['current_month', str(month), str(year)]))
    nex = InlineKeyboardButton('>>', callback_data=";".join(['next_slide', str(month), str(year)]))
    back = InlineKeyboardButton('⬅ Назад', callback_data=request_type)
    month_slider.add(prev, empty, nex, back)

    return month_slider
