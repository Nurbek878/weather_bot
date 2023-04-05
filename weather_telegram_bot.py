import logging
import os
import requests
from datetime import datetime

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('bot_token')
OPEN_WEATHER_TOKEN = os.getenv('open_weather_token')
ICONS = {
        "Clear": " Ясно \U000026000",
        "Clouds": "Облачно \U00002601",
        "Rain": " Дождь \U00002614",
        "Drizzle": "Дождь \U00002614",
        "Thunderstorm": "Гроза \U000026A1",
        "Snow": "Снег \U00001F328",
        "Mist": "Туман \U00001F32B"
    }


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler()
async def get_weather(message: types.Message) -> None:
    logging.debug('')
    try:
        r = requests.get(
            f'http://api.openweathermap.org/'
            f'data/2.5/weather?q={message.text}'
            f'&appid={OPEN_WEATHER_TOKEN}&units=metric'
            f'&lang=ru'
        )
        data = r.json()
        cur_city = data["name"]
        cur_temp = data["main"]["temp"]
        cur_humidity = data["main"]["humidity"]
        cur_wind = data["wind"]["speed"]
        cur_sunrise = datetime.fromtimestamp(data["sys"]["sunrise"])
        cur_sunset = datetime.fromtimestamp(data["sys"]["sunset"])
        cur_length_of_day = cur_sunset - cur_sunrise
        cur_icons = data["weather"][0]["main"]
        if cur_icons in ICONS:
            icons = ICONS[cur_icons]
        else:
            await message.reply("Лучше посмотри в окно сам")
        await message.reply(
            f"{datetime.now()}\n"
            f"Погода в городе: {cur_city}\nТемпература: {cur_temp}°C {icons}\n"
            f"Влажность: {cur_humidity}%\nСкорость ветра: {cur_wind} м/с\n"
            f"Рассвет: {cur_sunrise}\nЗакат: {cur_sunset}\n"
            f"Продолжительность дня: {cur_length_of_day}\n"
            f"Хорошего дня!")
        logging.debug(f'Сообщение о погоде в {cur_city} отправлено')
    except Exception as error:
        logging.error(f'Ошибка при запросе к API: {error}')
        await message.reply('\U00002620 Название города введено не верно')


def main():
    executor.start_polling(dp, timeout=60)


if __name__ == '__main__':
    main()

