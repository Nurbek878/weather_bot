import logging
import os
import sys
import requests
from datetime import datetime

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler

load_dotenv()

BOT_TOKEN = os.getenv('bot_token')
OPEN_WEATHER_TOKEN = os.getenv('open_weather_token')
ICONS = {
        'Clear': ' Ясно \U000026000',
        'Clouds': 'Облачно \U00002601',
        'Rain': ' Дождь \U00002614',
        'Drizzle': 'Дождь \U00002614',
        'Thunderstorm': 'Гроза \U000026A1',
        'Snow': 'Снег \U00001F328',
        'Mist': 'Туман \U00001F32B'
    }

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        RotatingFileHandler('program.log',
                            maxBytes=5000000,
                            backupCount=5)
    ]
)

logger = logging.getLogger(__name__)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


def check_tokens() -> bool:
    '''Функция проверяет доступность переменных окружения.'''
    return all((BOT_TOKEN, OPEN_WEATHER_TOKEN))


@dp.message_handler(commands=['start', 'help'])
async def start_command(message: types.Message) -> None:
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ['Туймазы', 'Санкт-Петербург']
    keyboard.add(*buttons)
    await message.answer('Напиши название города,'
                         'в котором хочешь узнать погоду в настоящее время',
                         reply_markup=keyboard)


def get_current_weather(city: str) -> str:
    try:
        r = requests.get("http://api.openweathermap.org/data/2.5/weather",
                         params={'q': city,
                                 'units': 'metric',
                                 'lang': 'ru',
                                 'APPID': OPEN_WEATHER_TOKEN})
        data = r.json()
        cur_city = data['name']
        cur_temp = data['main']['temp']
        cur_humidity = data['main']['humidity']
        cur_wind = data['wind']['speed']
        cur_timezone = data['timezone']
        cur_sunrise = datetime.fromtimestamp(
            data['sys']['sunrise'] + cur_timezone)
        cur_sunset = datetime.fromtimestamp(data['sys']['sunset']+cur_timezone)
        cur_length_of_day = cur_sunset - cur_sunrise
        cur_icons = data['weather'][0]['main']
        if cur_icons in ICONS:
            icons = ICONS[cur_icons]
        else:
            return 'Лучше посмотри в окно сам'
        message_text = (
            f'{datetime.now()}\n'
            f'Погода в городе: {cur_city}\nТемпература: {cur_temp}°C {icons}\n'
            f'Влажность: {cur_humidity}%\nСкорость ветра: {cur_wind} м/с\n'
            f'Рассвет: {cur_sunrise}\nЗакат: {cur_sunset}\n'
            f'Продолжительность дня: {cur_length_of_day}\n'
            f'Хорошего дня!')
    except Exception as error:
        logging.error(f'Ошибка при запросе к API weather: {error}')
    return message_text


def get_forecast_weather(city: str) -> str:
    try:
        r = requests.get('http://api.openweathermap.org/data/2.5/forecast',
                         params={'q': city,
                                 'units': 'metric',
                                 'lang': 'ru',
                                 'APPID': OPEN_WEATHER_TOKEN})
        data = r.json()
        message_text = ''
        prev_date_weather = str
        send_date_weather = str
        for i in data['list'][::2]:
            date_weather, time_weather = i['dt_txt'].split(' ')
            send_date_weather = (date_weather + '\n'
                                 if date_weather != prev_date_weather else '')
            prev_date_weather = date_weather
            send_time_weather = time_weather[:5]
            icon_weather = i['weather'][0]['main']
            icon = ICONS[icon_weather] if icon_weather in ICONS else ''
            send_temp = ' {0:+3.0f}'.format(i['main']['temp'])
            message_text += (f'<b>{send_date_weather}</b>'
                             f'{send_time_weather}'
                             f'{send_temp} °C '
                             f'{icon}\n')
    except Exception as error:
        logging.error(f'Ошибка при запросе к API forecast: {error}')
    return message_text


@dp.message_handler()
async def send_and_receive_weather(message: types.Message) -> None:
    city = message.text
    current_weather = get_current_weather(city)
    forecast_weather = get_forecast_weather(city)
    logging.debug('Начало обработки сообщения')
    try:
        await message.reply(f'Текущая погода:\n {current_weather}\n\n'
                            f'Прогноз:\n{forecast_weather}', parse_mode='html')
        logging.debug('Сообщение о погоде в отправлено')
    except Exception as error:
        logging.error(f'Ошибка при отправке сообщения: {error}')
        await message.reply('\U00002620 Название города введено не верно')


def main():
    '''Основная логика работы бота.'''
    if not check_tokens():
        logger.critical('Отсутствие обязательных переменных '
                        'окружения во время запуска бота')
        raise SystemExit()
    logger.info('Бот запущен')
    executor.start_polling(dp, timeout=60)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.exception('Бот остановлен')
