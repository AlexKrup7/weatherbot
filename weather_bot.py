import os
import requests
import datetime as dt
import logging
import telegram
import sqlite3
import re
from telegram.ext import MessageHandler, Updater

from dotenv import load_dotenv
from wind_direct import wind

load_dotenv()
TORR = 133.3223684
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TOKEN = os.getenv('WEATHER_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
NN = '56.20, 44.00'
WEATHER_URL_4_DAYS = 'https://api.openweathermap.org/data/2.5/forecast?q=' \
                     '{}&units={}&appid={}'

WEATHER_URL = f'https://wttr.in/{NN}'
UNITS = {'format': 2,
         'M': '',
         'Q': '',
         'lang': 'ru'}
bot = telegram.Bot(TELEGRAM_TOKEN)


def what_weather(city):
    response = requests.get(WEATHER_URL, params=UNITS)
    if response.status_code == 200:
        return f'Погода в Н.Новогороде: {response.text.strip()}'
    else:
        return '<ошибка на сервере>'


def weather_send(update, context):
    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id,
                             text=what_weather(NN))


def weather(update, context):
    keyword = ' '.join(context.args)
    hours = ''.join(re.findall(r'\d+', keyword))
    word = ' '.join(keyword.replace(hours, '').split())
    if hours == '':
        hours = 21
    conn = sqlite3.connect("weather.sqlite", check_same_thread=False)
    cursor = conn.cursor()
    chat = update.effective_chat
    city_name = word
    units = 'metric'
    r4 = requests.get(WEATHER_URL_4_DAYS.format(
        city_name, units, TOKEN)).json()
    if requests.get(WEATHER_URL_4_DAYS.format(
            city_name, units, TOKEN)).json()['cod'] == '404':
        r4 = requests.get(WEATHER_URL_4_DAYS.format(
            'Moscow', units, TOKEN)).json()
    counts1 = int(hours) // 3
    text1 = f"Погода в н.п. - {r4['city']['name']} на {counts1 * 3} часов:"
    bot.send_message(chat_id=chat.id, text=text1)
    r4 = r4['list']
    counts = 0
    for resp in r4:
        if counts == counts1:
            break
        counts += 1
        timestamp = int(resp['dt'])
        value = dt.datetime.fromtimestamp(timestamp)
        sql = "SELECT icon FROM weather_id WHERE id=?"
        des = (str(resp['weather'][0]['id']),)
        logging.debug(des)
        cursor.execute(sql, des)
        sql1 = "SELECT icon FROM weather_icons WHERE day_icon=?"
        q1 = cursor.fetchall()[0][0]
        logging.debug(q1)
        cursor.execute(sql1, (q1,))
        q2 = cursor.fetchall()[0][0]
        bot.send_message(
            chat_id=chat.id,
            text=(f"🕗 {value.strftime('%Y-%m-%d %H:%M')} "
                  f"⛅{resp['clouds']['all']}"
                  f"🌡{resp['main']['temp']}°С "
                  f"💧{resp['main']['humidity']}% "
                  f"P{round(float(resp['main']['pressure']) * 100 / TORR)} "
                  f"👀{round(resp['visibility'] / 1000)} км "
                  f"{q2} "
                  f"🌬{round(resp['wind']['speed'], 1)}"
                  f"{wind(int(resp['wind']['deg']))} м/с"))
    conn.close()
