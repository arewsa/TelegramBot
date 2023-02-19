import datetime
import pickle
import random
import threading
import time
from pathlib import Path

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import pandas as pd
import requests
import telebot
from balaboba import Balaboba
from telebot import types
import schedule


bot = telebot.TeleBot('5764219780:AAGMJTZxzbPo0fxTuB9tgoXl8BQA1h4nNDA')


gauth = GoogleAuth()
gauth.LoadCredentialsFile("mycreds.txt")
if gauth.credentials is None:
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    gauth.Refresh()
else:
    gauth.Authorize()
gauth.SaveCredentialsFile("mycreds.txt")
drive = GoogleDrive(gauth)


def reset():
    file_eating = 'eating_list.pkl'
    with open(file_eating, 'wb') as f:
        eating_list = {}
        for i in pd.read_excel('Shablon.xlsx'):
            if i != 'Расписание':
                eating_list[i] = 'Сегодня ещё не отмечали'
        pickle.dump(eating_list, f)


now_time = time.time()
a = time.gmtime()
clasi = []
doc = pd.read_excel('Shablon.xlsx')
file_reg = 'reg_users.pkl'
for i in doc:
    if i != 'Расписание':
        clasi.append(i)


def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()

def install_folder():
    file_list = drive.ListFile({'q': "'1RZxfvg7mvBMb-lozg8NuWbKwslQ2hQVl' in parents and trashed=false"}).GetList()
    for file1 in file_list:
        shedules = Path('shedule') /file1['title']
        if not shedules.is_file():
            file1.GetContentFile(str(shedules))

def run_schedule():
    schedule.every().day.at('00:00').do(reset)
    schedule.every(10).minutes.do(install_folder)
    while True:
        schedule.run_pending()
        time.sleep(1)


def update_eating_list(message):
    if not message.text.isdigit():
        mes = bot.send_message(
            message.chat.id, 'Ты чё угараешь?\nЯ число хочу')
        bot.register_next_step_handler(mes, update_eating_list)
        return
    if int(message.text) > 40:
        mes = bot.send_message(
            message.chat.id, 'Ты чё угараешь?\nЧё так много')
        bot.register_next_step_handler(mes, update_eating_list)
        return
    with open(file_reg, 'rb') as f:
        reg_user = pickle.load(f)
    with open('eating_list.pkl', 'rb') as g:
        eating_list = pickle.load(g)
        eating_list[reg_user[message.from_user.id]] = message.text
    with open('eating_list.pkl', 'wb') as g:
        pickle.dump(eating_list, g)
    bot.send_message(
        message.chat.id, f'Отмечено:\n{reg_user[message.from_user.id]}: {eating_list[reg_user[message.from_user.id]]}')


def balaboba(message):
    bb = Balaboba()

    intros = bb.intros(language="ru")

    intro = next(intros)

    response = bb.balaboba(message.text, intro=intro.number)
    bot.send_message(message.chat.id, response, parse_mode='html')


def check_pass(message):
    if message.text.lower() == 'отметить':
        mes = bot.send_message(
            message.chat.id, 'И сколько человек сегодня едят?')
        bot.register_next_step_handler(mes, update_eating_list)
    else:
        bot.send_message(message.chat.id, 'Не знаешь пароль: не лезь-убьёт!')


def main_marks():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    balabobich = types.KeyboardButton("Давай сделаем текст")
    website = types.KeyboardButton("Электронный Дневник")
    timetable = types.KeyboardButton("Хочу расписание")
    menu = types.KeyboardButton("А что будет в столовой?")
    joke = types.KeyboardButton('Давай шутку(бат ин инглиш)')
    change = types.KeyboardButton('Хочу сменить класс:(')
    check = types.KeyboardButton('Отметить в столовую')
    check_mean_see = types.KeyboardButton('Кто сегодня кушает?')
    markup.add(website, timetable, menu, balabobich,
               joke, change, check, check_mean_see)
    return markup


def output_schedule(clas, file):
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


def update_user_db(message):
    with open(file_reg, 'rb') as f:
        reg_users = pickle.load(f)
        reg_users[message.from_user.id] = message.text
    with open(file_reg, 'wb') as f:
        pickle.dump(reg_users, f)


def registration(message):
    update_user_db(message)
    bot.send_message(
        message.chat.id, f'Теперь ты в {message.text} классе', parse_mode='html', reply_markup=main_marks())
    bot.send_message(message.chat.id, 'Чего хочешь?')


def change_class(message):
    update_user_db(message)
    bot.send_message(
        message.chat.id, f'Теперь ты в {message.text} классе', parse_mode='html', reply_markup=main_marks())
    bot.send_message(message.chat.id, 'Чего теперь?')


RANDOM_CHOISES = ("Понять бы что это значит, давай-ка проверь что написал!",
                  "Что ты сейчас сказал, я не понимаю:(",
                  "Да, какой-то ты странный, что вообще написано?",
                  "Ээээ... как всё непонятно, ты точно это хотел сказать?")


@bot.message_handler(commands=['start'])
def reg_user(message):
    with open(file_reg, 'rb') as f:
        reg_users = pickle.load(f)
    if message.chat.id in reg_users:
        bot.send_message(message.chat.id, 'Привет, чем займёмся!?',
                         parse_mode='html', reply_markup=main_marks())
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=8)
        marks = []
        for g in clasi:
            marks.append(types.KeyboardButton(f'{g}'))
        markup.add(*marks)
        bot.send_message(message.chat.id,
                         f'Приветствую {message.from_user.first_name}, давай узнаем в каком ты классе!')
        mes = bot.send_message(
            message.chat.id, 'Выбирай свой класс', reply_markup=markup)
        bot.register_next_step_handler(mes, registration)


@bot.message_handler(content_types=["text"])
def get_user_text(message):
    with open(file_reg, 'rb') as f:
        reg_users = pickle.load(f)
        if message.chat.id in reg_users:
            if message.text.lower() == 'привет':
                bot.send_message(message.chat.id, f'И тебе привет, <b>{message.from_user.first_name}</b>',
                                 parse_mode='html')
            elif message.text == 'id':
                bot.send_message(message.chat.id, message, parse_mode='html')
            elif message.text == 'Хочу расписание':
                shediki = Path('shedule')
                tomorrow = shediki / \
                    f'{datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=1), "%d.%m.%Y")}.xlsx'
                today = shediki / \
                    f'{datetime.datetime.strftime(datetime.datetime.now(), "%d.%m.%Y")}.xlsx'
                file = tomorrow if tomorrow.is_file() else today if today.is_file() else Path()
                bot.send_message(
                    message.chat.id, "Вот твоё расписание на завтра:", parse_mode='html')
                if file == Path():
                    time.sleep(3)
                bot.send_message(message.chat.id, output_schedule(
                    reg_users[message.from_user.id], file), parse_mode='html')
                if file == today:
                    time.sleep(3)
                    bot.send_message(
                        message.chat.id, 'А, сорян, это на сегодня, на завтра ещё нет', parse_mode='html')
            elif message.text == "Электронный Дневник":
                markup1 = types.InlineKeyboardMarkup()
                markup1.add(
                    types.InlineKeyboardButton("Открыть Электронный дневник", url="https://edu.tatar.ru/logon"))
                bot.send_message(
                    message.chat.id, "Надеюсь там одни пятёрки:)", reply_markup=markup1)
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
                mes = bot.send_message(message.chat.id,
                                       "А, точно, когда напишешь, жди, он думает, чисто на мысле",
                                       parse_mode='html')
                bot.register_next_step_handler(mes, balaboba)
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
                markup = types.ReplyKeyboardMarkup(
                    resize_keyboard=True, row_width=8)
                marks = []
                for g in clasi:
                    marks.append(types.KeyboardButton(f'{g}'))
                markup.add(*marks)
                mes = bot.send_message(
                    message.chat.id, 'Выбирай тогда', reply_markup=markup)
                bot.register_next_step_handler(mes, change_class)
            elif message.text == 'Отметить в столовую':
                mes = bot.send_message(message.chat.id, 'А пароль-то знаешь?')
                bot.register_next_step_handler(mes, check_pass)
            elif message.text == 'Кто сегодня кушает?':
                with open('eating_list.pkl', 'rb') as g:
                    eating_list = pickle.load(g)
                result = ''
                for key, value in eating_list.items():
                    key = key + ':'
                    result += f'{key:<4} {value}\n'
                result = f'<pre>{result}</pre>'
                bot.send_message(message.chat.id, result, parse_mode='html')
            else:
                bot.send_message(
                    message.chat.id, random.choice(RANDOM_CHOISES))
        else:
            reg_user(message)


@bot.message_handler(content_types=["photo"])
def get_user_photo(message):
    bot.send_message(
        message.chat.id, "Ну да, используй меня как склад фото, да да, пожалуйста", parse_mode="html")


run_threaded(run_schedule)



bot.polling(none_stop=True)
