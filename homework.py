import os
import time
import logging
import json

import requests
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'

time_sleep = 900

status_dict = {
    'reviewing': 'Работа взята в ревью.',
    'rejected': 'К сожалению в работе нашлись ошибки.',
    'approved':
        'Ревьюеру всё понравилось, можно приступать к следующему уроку.',
}

logging.basicConfig(
    level=logging.DEBUG,
    filename='main.log',
    filemode='w',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    if homework_name is None:
        logging.error('Не удалось получить данные дз, homework_name is None')
        return 'Не удалось получить данные homework_name, ' \
               'homework_name is None'

    status = homework.get('status')

    if status in status_dict:
        verdict = status_dict[status]
        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'
    else:
        return 'Пришел неожиданный статус'


def get_homework_statuses(current_timestamp):
    if current_timestamp is None:
        current_timestamp = int(time.time())

    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    params = {'from_date': current_timestamp}

    try:
        homework_statuses = requests.get(url=URL, params=params,
                                         headers=headers)
        if 'error' in homework_statuses.json():
            logging.error(f"Ошибка распаковки json: "
                          f"{homework_statuses.json().get('error')}",
                          exc_ifo=True)

        return homework_statuses.json()

    except requests.RequestException as e:
        logging.error(f'Произошло исключение: {e}', exc_ifo=True)

    except json.JSONDecodeError as e:
        logging.error(f'Произошло исключение: {e}', exc_ifo=True)


def send_message(message, bot):
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    bot = Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)

            if new_homework.get('homeworks'):
                send_message(parse_homework_status(
                    new_homework.get('homeworks')[0]), bot)
            current_timestamp = new_homework.get('current_date',
                                                 current_timestamp)
            time.sleep(time_sleep)

        except Exception as e:
            print(f'Бот столкнулся с ошибкой: {e}')
            time.sleep(time_sleep)
            logging.error(f'Произошло исключение: {e}', exc_ifo=True)


if __name__ == '__main__':
    main()
