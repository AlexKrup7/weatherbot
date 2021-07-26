import os
import time
import requests
import telegram
import logging
from telegram.ext import Updater, CommandHandler
from dotenv import load_dotenv
from weather import weather, weather_send

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
HEADERS = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
bot = telegram.Bot(TELEGRAM_TOKEN)
updater = Updater(TELEGRAM_TOKEN, use_context=True)

url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s',
    filename='main.log', filemode='a'
)


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    if homework_name is None:
        return 'Пришли пустые данные!'
    homework_status = homework.get('status')
    if homework_status is None:
        return 'Пришли пустые данные!'
    homework_statuses = {
        'rejected': 'rejected',
        'approved': 'approved',
        'reviewing': 'reviewing'
    }
    if homework_status == homework_statuses['rejected']:
        verdict = 'К сожалению, в работе нашлись ошибки.'
    elif homework_status == homework_statuses['reviewing']:
        verdict = 'Работа взята в ревью.'
    else:
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


class FailBotException(Exception):
    pass


def get_homeworks(current_timestamp):
    headers = HEADERS
    if current_timestamp is None:
        current_timestamp = int(time.time())
    payload = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(url, headers=headers, params=payload)
        return homework_statuses.json()
    except requests.RequestException as e:
        raise FailBotException(f'Бот упал с ошибкой: {e}')


def send_message(message):
    logging.info(message)
    return bot.send_message(CHAT_ID, message)


def main():
    updater.dispatcher.add_handler(
        CommandHandler('weather', weather))
    current_timestamp = int(time.time())  # Начальное значение timestamp

    updater.dispatcher.add_handler(
        CommandHandler('weathernow', weather_send))

    while True:
        try:
            updater.start_polling(poll_interval=15.0)
            homework = get_homeworks(current_timestamp)
            new_homework = homework['homeworks']
            if new_homework:
                send_message(parse_homework_status(new_homework[0]))

            current_timestamp = homework['current_date']
            time.sleep(5 * 60)  # Опрашивать раз в пять минут

        except Exception as e:
            logging.error(f'Бот упал с ошибкой: {e}')
            time.sleep(5 * 60)


if __name__ == '__main__':
    main()
