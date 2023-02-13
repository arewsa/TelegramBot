import datetime
import pickle
import random
import time
from collections import defaultdict
from enum import Enum
from pathlib import Path

import pandas as pd
import requests
import telebot
from balaboba import Balaboba
from telebot import types

bot = telebot.TeleBot('5764219780:AAGMJTZxzbPo0fxTuB9tgoXl8BQA1h4nNDA')

a = time.gmtime()
clasi = []
doc = pd.read_excel('Shablon.xlsx')
file_reg = 'reg_users.pkl'
for i in doc:
    if i != 'Расписание':
        clasi.append(i)


def clasu(message):
    return f'{message.chat.id}'


def schedule(clas, file):
    if not file.is_file():
        return 'Извините пожалуйста, расписание отсутствует, все вопросы к Администрации школы!'
    dos = pd.read_excel(file)
    sched = dos[[clas, 'Расписание']]
    sched.index = sched.index + 1
    result = ''
    for index, row in sched.iterrows():
        if isinstance(row[0], str):
            result += f'{index}. {row[0]:<15}    {row[1]:<5}\n'
    if result == '':
        result = 'Ниче нет'
    else:
        result = f'<pre>{result}</pre>'
    return result


def registration(message):
    with open(file_reg, 'rb') as f:
        reg_users = pickle.load(f)
        reg_users[f'{message.chat.id}'] = f'{message.text}'
    with open(file_reg, 'wb') as f:
        pickle.dump(reg_users, f)


class State(Enum):
    DEFAULT = 1
    BALABOBA_WAITING_FOR_A_MESSAGE = 2
    REGISTRATION = 3
    CHANGE = 4


def get_state():
    return State.DEFAULT


states = defaultdict(get_state)

RANDOM_CHOISES = ("Понять бы что это значит, давай-ка проверь что написал!",
                  "Что ты сейчас сказал, я не понимаю:(",
                  "Да, какой-то ты странный, что вообще написано?",
                  "Ээээ... как всё непонятно, ты точно это хотел сказать?")


@bot.message_handler(commands=['start'])
def reg_user(message):
    global states
    with open(file_reg, 'rb') as f:
        reg_users = pickle.load(f)
    if f'{message.chat.id}' in reg_users:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        balabobich = types.KeyboardButton("Давай сделаем текст")
        website = types.KeyboardButton("Электронный Дневник")
        timetable = types.KeyboardButton("Хочу расписание")
        menu = types.KeyboardButton("А что будет в столовой?")
        joke = types.KeyboardButton('Давай шутку(бат ин инглиш)')
        change = types.KeyboardButton('Хочу сменить класс:(')
        markup.add(website, timetable, menu, balabobich, joke, change)
        bot.send_message(message.chat.id, 'Привет, чем займёмся!?', parse_mode='html', reply_markup=markup)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=8)
        marks = []
        for g in clasi:
            marks.append(types.KeyboardButton(f'{g}'))
        markup.add(*marks)
        bot.send_message(message.chat.id,
                         f'Приветствую {message.from_user.first_name}, давай узнаем в каком ты классе!')
        bot.send_message(message.chat.id, 'Выбирай свой класс', reply_markup=markup)
        states[message.from_user.id] = State.REGISTRATION


@bot.message_handler(content_types=["text"])
def get_user_text(message):
    global states
    if states[message.from_user.id] == State.DEFAULT:
        with open(file_reg, 'rb') as f:
            reg_users = pickle.load(f)
            if f'{message.chat.id}' in reg_users:
                if message.text.lower() == 'привет':
                    bot.send_message(message.chat.id, f'И тебе привет, <b>{message.from_user.first_name}</b>',
                                     parse_mode='html')
                elif message.text == 'id':
                    bot.send_message(message.chat.id, message, parse_mode='html')
                elif message.text == 'Хочу расписание':
                    shediki = Path('shedule')
                    tomorrow = shediki / f'{datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=1), "%d.%m.%Y")}.xlsx'
                    today = shediki / f'{datetime.datetime.strftime(datetime.datetime.now(), "%d.%m.%Y")}.xlsx'
                    file = tomorrow if tomorrow.is_file() else today if today.is_file() else Path()
                    bot.send_message(message.chat.id, "Вот твоё расписание на завтра:", parse_mode='html')
                    if file == Path():
                        time.sleep(3)
                    bot.send_message(message.chat.id, schedule(f'{reg_users[clasu(message)]}', file), parse_mode='html')
                    if file == today:
                        time.sleep(3)
                        bot.send_message(message.chat.id, 'А, сорян, это на сегодня, на завтра ещё нет', parse_mode='html')
                elif message.text == "Электронный Дневник":
                    markup1 = types.InlineKeyboardMarkup()
                    markup1.add(
                        types.InlineKeyboardButton("Открыть Электронный дневник", url="https://edu.tatar.ru/logon"))
                    bot.send_message(message.chat.id, "Надеюсь там одни пятёрки:)", reply_markup=markup1)
                elif message.text == "А что будет в столовой?":
                    bot.send_message(message.chat.id, "Погоди, сейчас узнаем")
                    time.sleep(3)
                    bot.send_message(message.chat.id, "Дело сделано")
                    time.sleep(1)
                    photo_menu = open("ccf7a86d37854b4e911c67a6d10c024b.jpg", 'rb')
                    bot.send_photo(message.chat.id, photo_menu)
                elif message.text == "Давай сделаем текст":
                    bot.send_message(message.chat.id, "Смотри, пиши начало своего текста, а потом тебе отдадут конец",
                                     parse_mode='html')
                    bot.send_message(message.chat.id,
                                     "Но знай, тут всё не идеально, если будет что то странное, просто смейся и пробуй заново!",
                                     parse_mode='html')
                    bot.send_message(message.chat.id,
                                     "А, точно, когда напишешь, жди, он думает, чисто на мысле",
                                     parse_mode='html')
                    states[message.from_user.id] = State.BALABOBA_WAITING_FOR_A_MESSAGE
                elif message.text == 'test':
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                    asd = types.KeyboardButton('123')
                    dsa = types.KeyboardButton('312')
                    a = [asd, dsa]
                    markup.add(a[i])
                    bot.send_message(message.chat.id, 'asd', reply_markup=markup)
                elif message.text == 'ты лох':
                    bot.send_sticker(message.chat.id,
                                     'CAACAgIAAxkBAAEHoRJj4pG-t7cLLekXTFeRx3TICJ3CPAACgBYAAtpaGUj4uq5mLvVLZi4E')
                elif message.text == 'Давай шутку(бат ин инглиш)':
                    url = "https://official-joke-api.appspot.com/random_joke"
                    response = requests.get(url)
                    question = response.json()['setup']
                    answer = response.json()['punchline']
                    text = []
                    text.append(question)
                    for _ in range(6):
                        text.append('.')
                    text.append(answer)
                    bot.send_message(message.chat.id, '\n'.join(text))
                elif message.text == ('Хочу сменить класс:('):
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=8)
                    marks = []
                    for g in clasi:
                        marks.append(types.KeyboardButton(f'{g}'))
                    markup.add(*marks)
                    bot.send_message(message.chat.id, 'Выбирай тогда', reply_markup=markup)
                    states[message.from_user.id] = State.CHANGE
                else:
                    bot.send_message(message.chat.id, random.choice(RANDOM_CHOISES))
            else:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=8)
                marks = []
                for g in clasi:
                    marks.append(types.KeyboardButton(f'{g}'))
                markup.add(*marks)
                bot.send_message(message.chat.id,
                                 f'Приветствую {message.from_user.first_name}, давай узнаем в каком ты классе!')
                bot.send_message(message.chat.id, 'Выбирай свой класс', reply_markup=markup)
                states[message.from_user.id] = State.REGISTRATION
    elif states[message.from_user.id] == State.BALABOBA_WAITING_FOR_A_MESSAGE:
        bb = Balaboba()

        intros = bb.intros(language="ru")

        intro = next(intros)

        response = bb.balaboba(message.text, intro=intro.number)
        bot.send_message(message.chat.id, response, parse_mode='html')
        states[message.from_user.id] = State.DEFAULT
    elif states[message.from_user.id] == State.REGISTRATION:
        registration(message)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        balabobich = types.KeyboardButton("Давай сделаем текст")
        website = types.KeyboardButton("Электронный Дневник")
        timetable = types.KeyboardButton("Хочу расписание")
        menu = types.KeyboardButton("А что будет в столовой?")
        joke = types.KeyboardButton('Давай шутку(бат ин инглиш)')
        change = types.KeyboardButton('Хочу сменить класс:(')
        markup.add(website, timetable, menu, balabobich, joke, change)
        bot.send_message(message.chat.id, f'Теперь ты в {message.text} классе', parse_mode='html', reply_markup=markup)
        bot.send_message(message.chat.id, 'Чего хочешь?')
        states[message.from_user.id] = State.DEFAULT
    elif states[message.from_user.id] == State.CHANGE:
        registration(message)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        balabobich = types.KeyboardButton("Давай сделаем текст")
        website = types.KeyboardButton("Электронный Дневник")
        timetable = types.KeyboardButton("Хочу расписание")
        menu = types.KeyboardButton("А что будет в столовой?")
        joke = types.KeyboardButton('Давай шутку(бат ин инглиш)')
        change = types.KeyboardButton('Хочу сменить класс:(')
        markup.add(website, timetable, menu, balabobich, joke, change)
        bot.send_message(message.chat.id, f'Теперь ты в {message.text} классе', parse_mode='html', reply_markup=markup)
        bot.send_message(message.chat.id, 'Чего теперь?')
        states[message.from_user.id] = State.DEFAULT


@bot.message_handler(content_types=["photo"])
def get_user_photo(message):
    bot.send_message(message.chat.id, "Ну да, используй меня как склад фото, да да, пожалуйста", parse_mode="html")


bot.polling(none_stop=True)
