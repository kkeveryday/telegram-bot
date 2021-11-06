import telebot
from telebot import types
import time
import psycopg2
from collections import defaultdict
import os

try:
    # Подключение к БД
    connection = psycopg2.connect(
        database=os.getenv("DATABASE"),
        user=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        host=os.getenv("HOST"),
        port="5432"
    )
except psycopg2.OperationalError:
    print('Connection error')
else:
    print('Database opened successfully')
    cursor = connection.cursor()

    bot = telebot.TeleBot(os.getenv("TG_TOKEN"))

    # Начальное сообщение с команды /start
    @bot.message_handler(commands=['start'])
    def start_command(message):
        time.sleep(0.7)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
            types.KeyboardButton(text='/menu'))
        bot.reply_to(message, f'Я бот ИУЦТ. Приятно познакомиться, {message.from_user.first_name}. С моей помощью ты '
                              f'можешь узнать расписание группы, аудитории, преподавателя или посмотреть другие '
                              f'документы. Нажми на кнопку, '
                              f'чтобы продолжить', reply_markup=keyboard)

    # Главное меню с команды /menu
    @bot.message_handler(commands=['menu'])
    def menu_command(message):
        time.sleep(0.7)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        key_schedule_group = types.KeyboardButton(text='Расписание учебных групп')
        keyboard.add(key_schedule_group)
        key_schedule_room = types.KeyboardButton(text='Расписание аудиторий')
        keyboard.add(key_schedule_room)
        key_schedule_people = types.KeyboardButton(text='Расписание преподавателей')
        keyboard.add(key_schedule_people)
        key_regulations = types.KeyboardButton(text='Нормативные документы')
        keyboard.add(key_regulations)
        bot.send_message(message.from_user.id, 'Что тебя интересует?', reply_markup=keyboard)

    # Функция, которая выводит кнопку /menu для того, чтобы вернуться в главное меню
    def home(mes):
        keyboard_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
            types.KeyboardButton(text='/menu'))
        bot.send_message(mes.from_user.id, 'Вернуться в главное меню', reply_markup=keyboard_menu)

    # Работа с расписанием учебных групп
    @bot.message_handler(func=lambda message: message.text == 'Расписание учебных групп', content_types=['text'])
    def get_text_schedule_group(message):
        time.sleep(0.7)
        keyboard1 = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

        cursor.execute("select course_number, group_name from schedule_group")  # Запрос БД
        query = cursor.fetchall()
        course_group_dict = defaultdict(list)
        all_group_names = []
        for key, value in query:
            course_group_dict[key].append(value)
            all_group_names.append(value)

        course_numbers = []
        for num in course_group_dict.keys():
            key1 = types.KeyboardButton(text=f'{num} курс')
            course_numbers.append(f'{num} курс')
            keyboard1.add(key1)
        bot.send_message(message.from_user.id, 'Какой у тебя курс?', reply_markup=keyboard1)

        @bot.message_handler(func=lambda message2: message2.text in course_numbers, content_types=['text'])
        def get_text_course(message2):
            time.sleep(0.7)
            group_names = course_group_dict[int(message2.text.split()[0])]
            keyboard2 = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            for name in group_names:
                key2 = types.KeyboardButton(text=name)
                keyboard2.add(key2)
            bot.send_message(message2.from_user.id, 'Какая у тебя группа?', reply_markup=keyboard2)

            @bot.message_handler(func=lambda message3: message3.text in all_group_names, content_types=['text'])
            def get_text_group(message3):
                time.sleep(0.7)
                remove_keyboard = types.ReplyKeyboardRemove()
                cursor.execute(f"select schedule_link from schedule_group where group_name = '{message3.text}'")  #
                # Запрос БД
                link = [str(*i) for i in cursor.fetchall()]
                bot.send_message(message3.from_user.id, *link, reply_markup=remove_keyboard)
                time.sleep(0.7)
                home(message3)

    # Работа с расписанием аудиторий
    @bot.message_handler(func=lambda message: message.text == 'Расписание аудиторий', content_types=['text'])
    def get_text_schedule_room(message):
        time.sleep(0.7)
        keyboard1 = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

        cursor.execute("select room_floor, room_number from schedule_room order by room_floor")  # Запрос БД
        query = cursor.fetchall()
        floor_room_dict = defaultdict(list)
        all_room_numbers = []
        for key, value in query:
            floor_room_dict[key].append(value)
            all_room_numbers.append(value)

        floor_numbers = []
        for num in floor_room_dict.keys():
            key1 = types.KeyboardButton(text=f'{num} этаж')
            floor_numbers.append(f'{num} этаж')
            keyboard1.add(key1)
        bot.send_message(message.from_user.id, 'Какой этаж у аудитории?', reply_markup=keyboard1)

        @bot.message_handler(func=lambda message2: message2.text in floor_numbers, content_types=['text'])
        def get_text_floor(message2):
            time.sleep(0.7)
            room_numbers = floor_room_dict[int(message2.text.split()[0])]
            keyboard2 = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            for room_num in room_numbers:
                key2 = types.KeyboardButton(text=room_num)
                keyboard2.add(key2)
            bot.send_message(message2.from_user.id, 'Какая аудитория?', reply_markup=keyboard2)

            @bot.message_handler(func=lambda message3: message3.text in all_room_numbers, content_types=['text'])
            def get_text_room(message3):
                time.sleep(0.7)
                remove_keyboard = types.ReplyKeyboardRemove()
                cursor.execute(f"select schedule_link from schedule_room where room_number = '{message3.text}'")  #
                # Запрос БД
                link = [str(*i) for i in cursor.fetchall()]
                bot.send_message(message3.from_user.id, *link, reply_markup=remove_keyboard)
                time.sleep(0.7)
                home(message3)

    # Работа с расписанием преподавателей
    @bot.message_handler(func=lambda message: message.text == 'Расписание преподавателей', content_types=['text'])
    def get_text_schedule_people(message):
        time.sleep(0.7)
        keyboard1 = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

        cursor.execute("select full_name from schedule_people")  # Запрос БД
        people_full_names = [str(*i) for i in cursor.fetchall()]
        for full_name in people_full_names:
            key1 = types.KeyboardButton(text=full_name)
            keyboard1.add(key1)
        bot.send_message(message.from_user.id, 'Какой преподаватель тебе нужен?', reply_markup=keyboard1)

        @bot.message_handler(func=lambda message2: message2.text in people_full_names, content_types=['text'])
        def get_text_full_name(message2):
            time.sleep(0.7)
            remove_keyboard = types.ReplyKeyboardRemove()
            cursor.execute(f"select schedule_link from schedule_people where full_name = '{message2.text}'")  #
            # Запрос БД
            link = [str(*i) for i in cursor.fetchall()]
            bot.send_message(message2.from_user.id, *link, reply_markup=remove_keyboard)
            time.sleep(0.7)
            home(message2)

    # Работа с нормативными документами
    @bot.message_handler(func=lambda message: message.text == 'Нормативные документы', content_types=['text'])
    def get_text_regulations(message):
        time.sleep(0.7)
        keyboard1 = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

        cursor.execute("select doc_name from regulations")  # Запрос БД
        doc_names = [str(*i) for i in cursor.fetchall()]
        for name in doc_names:
            key1 = types.KeyboardButton(text=name)
            keyboard1.add(key1)
        bot.send_message(message.from_user.id, 'Какой документ тебе нужен?', reply_markup=keyboard1)

        @bot.message_handler(func=lambda message2: message2.text in doc_names, content_types=['text'])
        def get_text_doc_name(message2):
            time.sleep(0.7)
            remove_keyboard = types.ReplyKeyboardRemove()
            cursor.execute(f"select doc_link from regulations where doc_name = '{message2.text}'")  #
            # Запрос БД
            link = [str(*i) for i in cursor.fetchall()]
            bot.send_message(message2.from_user.id, *link, reply_markup=remove_keyboard)
            time.sleep(0.7)
            home(message2)


    bot.polling(none_stop=True, interval=0)

