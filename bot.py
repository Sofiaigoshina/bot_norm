import json
from googletrans import Translator
import telebot
from telebot import types
from datetime import datetime, timedelta
import threading
from threading import Timer
import requests
import pytesseract
from PIL import Image
from io import BytesIO
from telethon import TelegramClient, events
import asyncio
import threading





# Токен и Telethon API
TOKEN = "7741801519:AAFwBZl5bOhyUd6PXdwRXTV7tDnrWtQQcGI"
api_id = '28911485'
api_hash = '8fd9f69233ba05a7a5a162a0c99e4223'

# Создаем клиентов
bot = telebot.TeleBot(TOKEN)
client = TelegramClient('session_name', api_id, api_hash)

# Идентификатор второго бота
TARGET_BOT_USERNAME = 'GPT4Tbot'

# Словарь для отслеживания пользователей в чате
user_in_chat = {}

# =========================
# Команда /chat: Начать диалог с ИИ-ботом
@bot.message_handler(commands=['chat'])
def start_chat(message):
    chat_id = message.chat.id
    user_in_chat[chat_id] = True  # Помечаем пользователя как активного в чате
    bot.send_message(chat_id, "Теперь вы можете общаться с ИИ-ботом. Напишите сообщение или отправьте /stop для выхода из чата.")

# =========================
# Команда /stop: Завершить диалог
@bot.message_handler(commands=['stop'])
def stop_chat(message):
    chat_id = message.chat.id
    if user_in_chat.get(chat_id):
        user_in_chat.pop(chat_id)
        bot.send_message(chat_id, "Вы вышли из чата с ИИ-ботом.")
    else:
        bot.send_message(chat_id, "Вы не находитесь в чате с ИИ-ботом.")

# =========================
# Перехват сообщений для чата с ИИ-ботом
@bot.message_handler(func=lambda message: message.chat.id in user_in_chat)
def handle_chat_message(message):
    chat_id = message.chat.id
    user_message = message.text  # Сообщение пользователя

    # Отправка сообщения ИИ-боту через Telethon
    async def send_to_target_bot():
        try:
            async with client.conversation(TARGET_BOT_USERNAME) as conv:
                await conv.send_message(user_message)  # Отправляем сообщение второму боту
                response = await conv.get_response()  # Получаем ответ
                bot.send_message(chat_id, f"Ответ от ИИ:\n\n{response.text}")  # Отправляем ответ пользователю
        except Exception as e:
            bot.send_message(chat_id, "Произошла ошибка при общении с ИИ-ботом.")
            print(f"Ошибка Telethon: {e}")

    # Запускаем асинхронную функцию
    loop = asyncio.get_event_loop()
    loop.create_task(send_to_target_bot())

# =========================
# Запуск Telethon клиента
def start_telethon():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    with client:
        print("Telethon клиент запущен")
        client.run_until_disconnected()






















































# назад

@bot.message_handler(func=lambda message: message.text == "\U0001F519 Назад")
def go_back_to_main_menu(message):
    send_welcome(message)  # Возвращаем в главное меню


# Команда /start

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn3 = types.KeyboardButton("\U0001F522 Калькулятор")
    btn5 = types.KeyboardButton("\U0001F30F Переводчик")
    markup.add(btn3, btn5)
    bot.send_message(message.chat.id, "Привет! Я твой помощник. Выбери нужное:", reply_markup=markup)


# Обработка калькулятора
@bot.message_handler(func=lambda message: message.text == "\U0001F522 Калькулятор")
def calculator_start(message):
    bot.send_message(message.chat.id, "Введите выражение для вычисления. Например: 2 + 2. Используйте + - * :.")
    bot.register_next_step_handler(message, calculate)

def calculate(message):
    try:
        expression = message.text.replace(" ", "").replace(":", "/")
        if not all(c in "0123456789+-*./:()" for c in expression):
            raise ValueError("⛔ Некорректное выражение")
        result = eval(expression, {"__builtins__": None}, {})
        bot.send_message(message.chat.id, f"✅ Результат: {result}")
    except ZeroDivisionError:
        bot.send_message(message.chat.id, "⛔ Ошибка: Деление на ноль!")
    except Exception as e:
        bot.send_message(message.chat.id, "⛔ Ошибка вычисления. Проверьте выражение.")
        print(f"⛔ Ошибка калькулятора: {e}")

        # Кнопка "Назад" для возвращения в главное меню
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        back_button = types.KeyboardButton("\U0001F519 Назад")
        markup.add(back_button)
        bot.send_message(message.chat.id, "Вы можете вернуться в главное меню:", reply_markup=markup)

    # Обработка кнопки "Назад"
    @bot.message_handler(func=lambda message: message.text == "\U0001F519 Назад")
    def go_back_to_main_menu(message):
        send_welcome(message)


# ИЗ ФОТО В ТЕКСТ


# Установите путь к Tesseract, если он не добавлен в системный PATH
# Пример для Windows:
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Привет! Я твой помощник. Отправь мне изображение с текстом, и я попробую распознать текст на нем.")

# Обработчик команды /recognize_text
@bot.message_handler(commands=['recognize_text'])
def recognize_text(message):
    bot.send_message(message.chat.id, "Отправь мне изображение, и я распознаю текст.")

# Обработчик изображений
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    # Получаем ID фото
    photo_id = message.photo[-1].file_id
    file_info = bot.get_file(photo_id)

    # Скачиваем изображение
    file = bot.download_file(file_info.file_path)

    # Открываем изображение с помощью Pillow
    img = Image.open(BytesIO(file))

    # Распознаем текст на изображении
    text = pytesseract.image_to_string(img)

    # Если текст найден, отправляем его пользователю
    if text.strip():
        bot.send_message(message.chat.id, f"Я распознал текст:\n\n{text}")
    else:
        bot.send_message(message.chat.id, "Извините, я не смог распознать текст на этом изображении.")


# ПОГОДА


# Ваш API-ключ OpenWeatherMap
API_KEY = "fae9e0450787495c7125a0ebf3f00f83"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

# Словарь для хранения напоминаний о погоде
weather_reminders = {}

# Функция для получения погоды
def get_weather(city):
    try:
        params = {
            'q': city,
            'appid': API_KEY,
            'units': 'metric',  # Температура в Цельсиях
            'lang': 'ru'  # Язык на русском
        }
        response = requests.get(BASE_URL, params=params)
        data = response.json()

        if data["cod"] == 200:
            # Получаем данные о погоде
            main_data = data["main"]
            weather_data = data["weather"][0]
            temperature = main_data["temp"]
            weather_description = weather_data["description"]
            city_name = data["name"]

            # Форматируем результат
            weather_info = (
                f"Погода в {city_name}:\n"
                f"Температура: {temperature}°C\n"
                f"Описание: {weather_description.capitalize()}"
            )
            return weather_info
        else:
            return None  # Если города нет, возвращаем None
    except Exception as e:
        print(f"Ошибка при получении погоды: {e}")
        return None  # При ошибке возвращаем None

# Функция для установки напоминания о погоде
def set_weather_reminder(message, city):
    if message.text.lower() == "да":
        bot.send_message(message.chat.id, """На какое время вы хотите установить напоминание о погоде? 
Пожалуйста, введите время в формате 'HH:MM' 
Например, 08:00.""")
        bot.register_next_step_handler(message, save_weather_time, city)
    elif message.text.lower() == "нет":
        bot.send_message(message.chat.id, "Напоминание не установлено.")
    else:
        bot.send_message(message.chat.id, "Пожалуйста, ответьте 'Да' или 'Нет'.")
        bot.register_next_step_handler(message, set_weather_reminder, city)

# Сохраняем время напоминания
def save_weather_time(message, city):
    user_id = message.chat.id
    try:
        reminder_time = datetime.strptime(message.text, "%H:%M").replace(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day)

        # Если время меньше текущего, устанавливаем напоминание на следующий день
        if reminder_time < datetime.now():
            reminder_time += timedelta(days=1)

        # Сохраняем время напоминания в словарь
        weather_reminders[user_id] = {
            'time': reminder_time,
            'city': city
        }

        bot.send_message(message.chat.id, f"✅ Напоминание о погоде для города {city} установлено на {reminder_time.strftime('%H:%M')} каждый день.")

        # Запускаем таймер для первого напоминания
        delta_seconds = (reminder_time - datetime.now()).total_seconds()
        Timer(delta_seconds, send_weather_reminder, args=[user_id, city]).start()

    except ValueError:
        bot.send_message(message.chat.id, "⛔ Некорректный формат времени. Попробуйте снова.")
        bot.register_next_step_handler(message, save_weather_time, city)

# Функция для отправки напоминания о погоде
def send_weather_reminder(user_id, city):
    weather_info = get_weather(city)
    if weather_info:
        bot.send_message(user_id, f"🌤️ Напоминание о погоде для города {city}:\n{weather_info}")
    else:
        bot.send_message(user_id, "❌ Не удалось получить информацию о погоде. Проверьте правильность города.")

    # Запускаем таймер на следующий день (каждые 24 часа)
    Timer(86400, send_weather_reminder, args=[user_id, city]).start()

# Команда /weather
@bot.message_handler(commands=['weather'])
def weather_start(message):
    bot.send_message(message.chat.id, """📅 ПОГОДА
——————————————————
Введите название города, чтобы узнать погоду:""")
    bot.register_next_step_handler(message, get_weather_info)

# Обработка текста города для погоды
def get_weather_info(message):
    city = message.text.strip()
    weather_info = get_weather(city)

    if weather_info:
        bot.send_message(message.chat.id, weather_info)

        # После показа погоды предлагаем установить напоминание
        bot.send_message(message.chat.id, "Хотите установить ежедневное напоминание о погоде? (Да/Нет)")
        bot.register_next_step_handler(message, set_weather_reminder, city)
    else:
        bot.send_message(message.chat.id, "❌ Город не найден. Пожалуйста, попробуйте ввести город снова.")
        bot.register_next_step_handler(message, get_weather_info)

    # Убедитесь, что кнопка "Назад" всегда отображает главное меню
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    back_button = types.KeyboardButton("\U0001F519 Назад")
    markup.add(back_button)
    bot.send_message(message.chat.id, "Вы можете вернуться в главное меню:", reply_markup=markup)


# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_calculator = types.KeyboardButton("\U0001F522 Калькулятор")
    btn_translator = types.KeyboardButton("\U0001F30F Переводчик")

    markup.add(btn_calculator, btn_translator)
    bot.send_message(message.chat.id, "Привет! Я твой помощник. Выбери нужное:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "🌤 Погода")
def weather_button(message):
    # Здесь используем команду weather_start для отображения погоды
    weather_start(message)



# НАПОМИНАНИЯ

reminders = {}  # Словарь для напоминаний

# Начальный запрос на установку даты и времени
def set_reminder_date_time(message):
    bot.send_message(message.chat.id,
                     """Введите дату и время напоминания в формате:
'dd.mm.yyyy HH:MM' (Например: '16.12.2024 15:00')""")
    bot.register_next_step_handler(message, set_reminder_text)


# Обработка даты и времени и запрос текста напоминания
def set_reminder_text(message):
    try:
        # Парсим дату и время
        reminder_time = datetime.strptime(message.text, "%d.%m.%Y %H:%M")

        # Проверяем, что время в будущем
        if reminder_time < datetime.now():
            bot.send_message(message.chat.id, "⛔ Нельзя установить напоминание в прошлом. Попробуйте снова.")
            set_reminder_date_time(message)
            return

        # Сохраняем время напоминания в словаре для дальнейшего использования
        user_id = message.chat.id
        if user_id not in reminders:
            reminders[user_id] = {"pending": {"time": reminder_time}}
        else:
            reminders[user_id]["pending"] = {"time": reminder_time}

        bot.send_message(message.chat.id, "Введите текст напоминания: ")
        bot.register_next_step_handler(message, save_reminder)
    except ValueError:
        bot.send_message(message.chat.id, "⛔ Некорректный формат даты и времени. Попробуйте снова: 'dd.mm.yyyy HH:MM'")
        set_reminder_date_time(message)

# Сохранение напоминания
def save_reminder(message):
    user_id = message.chat.id
    if user_id in reminders and "pending" in reminders[user_id]:
        reminder_time = reminders[user_id]["pending"]["time"]
        reminder_text = message.text

        # Сохраняем напоминание
        if "reminders" not in reminders[user_id]:
            reminders[user_id]["reminders"] = []
        reminders[user_id]["reminders"].append({"text": reminder_text, "time": reminder_time})
        del reminders[user_id]["pending"]  # Удаляем временные данные

        # Подтверждение пользователю
        bot.send_message(message.chat.id,
                         f"✅ Напоминание установлено: '{reminder_text}' на {reminder_time.strftime('%d.%m.%Y %H:%M')}")

        # Запускаем таймер для напоминания
        delta_seconds = (reminder_time - datetime.now()).total_seconds()
        Timer(delta_seconds, send_reminder, args=[user_id, reminder_text]).start()

        # Возвращаем пользователя в меню
        handle_reminders(message)
    else:
        bot.send_message(message.chat.id, "⚠️ Произошла ошибка. Начните заново.")
        set_reminder_date_time(message)

# Функция отправки напоминания
def send_reminder(user_id, reminder_text):
    try:
        bot.send_message(user_id, f"⏰ Напоминание: {reminder_text}")
    except Exception as e:
        print(f"Ошибка при отправке напоминания: {e}")

# Функция для обработки команды /reminders
@bot.message_handler(commands=['reminders'])
def handle_reminders(message):
    user_id = message.chat.id

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("➕ Установить напоминание")
    btn2 = types.KeyboardButton("📋 Мои напоминания")
    btn3 = types.KeyboardButton("\U0001F519 Назад")  # Кнопка "Назад"
    markup.add(btn1, btn2, btn3)

    # Проверяем наличие напоминаний
    if user_id not in reminders or "reminders" not in reminders[user_id] or not reminders[user_id]["reminders"]:
        bot.send_message(message.chat.id, """📅 НАПОМИНАНИЯ
——————————————————
У вас нет установленных напоминаний. Что бы вы хотели сделать?""",
                         reply_markup=markup)
    else:
        reminders_list = "\n".join([
            f"{i + 1}. {r['text']} на {r['time'].strftime('%d.%m.%Y %H:%M')}"
            for i, r in enumerate(reminders[user_id]["reminders"])
        ])
        bot.send_message(message.chat.id, f"Ваши текущие напоминания:\n{reminders_list}", reply_markup=markup)

    bot.register_next_step_handler(message, reminder_options)

# Обработка опций в меню
def reminder_options(message):
    if message.text == "➕ Установить напоминание":
        set_reminder_date_time(message)  # Начинаем с запроса даты и времени
    elif message.text == "📋 Мои напоминания":
        user_id = message.chat.id
        if user_id in reminders and "reminders" in reminders[user_id] and reminders[user_id]["reminders"]:
            reminders_list = "\n".join([
                f"{i + 1}. {r['text']} на {r['time'].strftime('%d.%m.%Y %H:%M')}"
                for i, r in enumerate(reminders[user_id]["reminders"])
            ])
            bot.send_message(message.chat.id, f"Ваши напоминания:\n{reminders_list}")
        else:
            bot.send_message(message.chat.id, "У вас нет активных напоминаний.")
        handle_reminders(message)
    elif message.text == "\U0001F519 Назад":
        send_welcome(message)  # Возвращаем в главное меню
    else:
        bot.send_message(message.chat.id, "Пожалуйста, выберите один из вариантов.")
        handle_reminders(message)



# РАСПИСАНИЕ

# Расписание
schedule = {
    "Числитель": {
        "Понедельник": "КСРС",
        "Вторник": "4. 12:40-14:00 (А305)\nЛК: Техн. созд. и поддерж. ПО\nВишняков Р.Ю.\n5. 14:10-15:30 (103а)\nЛР: Техн. созд. и поддерж. ПО\nЗдоровцов А.А.",
        "Среда": "3. 11:10-12:30 (А305)\nЛК: Физ. теория функц. компьютера\nРубцов С.Е.\n4. 12:40-14:00 (103а)\nЛР: нечет. и гибрид. системы\nГиш А.З.",
        "Четверг": "1. География - 10:00",
        "Пятница": "1. Химия - 12:00\n2. Физкультура - 14:00",
        "Суббота": "Выходной",
        "Воскресенье": "КСРС",
    },
    "Знаменатель": {
        "Понедельник": "КСРС",
        "Вторник": "4. 12:40-14:00 (А305)\nЛК: Техн. созд. и поддерж. ПО\nВишняков Р.Ю.\n5. 14:10-15:30 (103а)\nЛР: Техн. созд. и поддерж. ПО\nЗдоровцов А.А.",
        "Среда": "3. 11:10-12:30 (А305)\nЛК: Физ. теория функц. компьютера\nРубцов С.Е.\n4. 12:40-14:00 (103а)\nЛР: нечет. и гибрид. системы\nГиш А.З.",
        "Четверг": "3. 11:10-12:30 (А305)\nЛК: Физ. теория функц. компьютера\nРубцов С.Е.\n4. 12:40-14:00 (103а)\nЛР: нечет. и гибрид. системы\nГиш А.З.",
        "Пятница": "3. 11:10-12:30 (А305)\nЛК: Физ. теория функц. компьютера\nРубцов С.Е.\n4. 12:40-14:00 (103а)\nЛР: нечет. и гибрид. системы\nГиш А.З.",
        "Суббота": "Выходной",
        "Воскресенье": "Выходной",
    },
}
# Обработка команды /schedule
@bot.message_handler(commands=['schedule'])
def handle_schedule(message):
    send_schedule_week_type(message)

def send_schedule_week_type(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Числитель")
    btn2 = types.KeyboardButton("Знаменатель")
    btn3 = types.KeyboardButton("\U0001F519 Назад")
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id, """📚 РАСПИСАНИЕ
——————————————————
Выберите тип недели:""", reply_markup=markup)
    bot.register_next_step_handler(message, send_schedule_days)

def send_schedule_days(message):
    week_type = message.text
    if week_type in schedule:
        user_data[message.chat.id] = week_type
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for day in schedule[week_type].keys():
            markup.add(types.KeyboardButton(day))
        markup.add(types.KeyboardButton("\U0001F519 Назад"))
        bot.send_message(message.chat.id, f"Вы выбрали: {week_type}. Теперь выберите день недели:", reply_markup=markup)
        bot.register_next_step_handler(message, show_schedule)
    elif message.text == "\U0001F519 Назад":
        send_welcome(message)
    else:
        bot.send_message(message.chat.id, "Пожалуйста, выберите Числитель или Знаменатель.")
        send_schedule_week_type(message)

def show_schedule(message):
    day = message.text
    week_type = user_data.get(message.chat.id)
    if day in schedule.get(week_type, {}):
        # Формируем текст с расписанием
        schedule_text = f"Расписание на {day} ({week_type}):\n{schedule[week_type][day]}"
        # Создаем клавиатуру с кнопкой "Назад"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        back_button = types.KeyboardButton("\U0001F519 Назад")
        markup.add(back_button)
        # Отправляем расписание и добавляем кнопку "Назад"
        bot.send_message(message.chat.id, schedule_text, reply_markup=markup)
        bot.register_next_step_handler(message, send_schedule_week_type)  # Возвращаемся к выбору недели
    elif day == "\U0001F519 Назад":
        send_schedule_week_type(message)
    else:
        bot.send_message(message.chat.id, "Пожалуйста, выберите день из списка.")
        send_schedule_days(message)

# ПОДДЕРЖКА
# Обработчик команды /support
@bot.message_handler(commands=['support'])
def handle_support(message):
    # Ссылка на ваш Telegram-аккаунт
    support_url = "https://t.me/sofia_son"  # Замените на свой username

    markup = types.InlineKeyboardMarkup()  # Используем InlineKeyboardMarkup для кнопки с ссылкой
    button = types.InlineKeyboardButton(text="Написать в поддержку", url=support_url)  # Кнопка с ссылкой
    markup.add(button)

    bot.send_message(message.chat.id, """💬 ПОДДЕРЖКА
—————————————————
По всем вопросам и предложениям обращайтесь в официальный аккаунт сервиса:""", reply_markup=markup)


# ПЕРЕВОДЧИК

translator = Translator()

user_data = {}  # Хранение данных пользователя для переводчика

# Добавление новых языков
LANGUAGES = {
    "🇬🇧 Английский": "en",
    "🇷🇺 Русский": "ru",
    "🇪🇸 Испанский": "es",
    "🇫🇷 Французский": "fr",
    "🇩🇪 Немецкий": "de",
    "🇮🇹 Итальянский": "it",
    "🇨🇳 Китайский": "zh-cn",
    "🇯🇵 Японский": "ja"
}

@bot.message_handler(func=lambda message: message.text == "\U0001F30F Переводчик")
def translator_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for language in LANGUAGES:
        markup.add(types.KeyboardButton(language))
    back = types.KeyboardButton("\U0001F519 Назад")
    markup.add(back)

    bot.send_message(message.chat.id, "🌍 Выберите язык, с которого переводить:", reply_markup=markup)
    bot.register_next_step_handler(message, translator_select_from_language)

def translator_select_from_language(message):
    if message.text == "\U0001F519 Назад":
        send_welcome(message)
        return
    if message.text in LANGUAGES:
        user_data[message.chat.id] = {"from_lang": LANGUAGES[message.text]}
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for language in LANGUAGES:
            markup.add(types.KeyboardButton(language))
        back = types.KeyboardButton("\U0001F519 Назад")
        markup.add(back)
        bot.send_message(message.chat.id, "Теперь выберите язык, на который переводить:", reply_markup=markup)
        bot.register_next_step_handler(message, translator_select_to_language)
    else:
        bot.send_message(message.chat.id, "Пожалуйста, выберите язык из списка.")
        translator_menu(message)

def translator_select_to_language(message):
    if message.text == "\U0001F519 Назад":
        translator_menu(message)
        return
    if message.text in LANGUAGES:
        user_data[message.chat.id]["to_lang"] = LANGUAGES[message.text]
        bot.send_message(message.chat.id, "Введите текст для перевода:")
        bot.register_next_step_handler(message, perform_translation)
    else:
        bot.send_message(message.chat.id, "Пожалуйста, выберите язык из списка.")
        translator_select_to_language(message)

def perform_translation(message):
    if not message.text.strip():
        bot.send_message(message.chat.id, "Введите текст для перевода. Попробуйте снова.")
        bot.register_next_step_handler(message, perform_translation)
        return

    try:
        lang_data = user_data.get(message.chat.id, {})
        from_lang = lang_data.get("from_lang", "auto")  # Если не выбрали, то по умолчанию auto
        to_lang = lang_data.get("to_lang", "ru")  # Если не выбрали, то по умолчанию русский

        translated_text = translator.translate(message.text, src=from_lang, dest=to_lang).text
        bot.send_message(message.chat.id, f"✅ Перевод с {from_lang} на {to_lang}:\n{translated_text}")
    except Exception as e:
        bot.send_message(message.chat.id, "⛔ Произошла ошибка при переводе. Попробуйте снова.")
        print(f"Ошибка перевода: {e}")  # Логирование ошибки
    finally:
        # Создаём клавиатуру с кнопкой "Назад"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        back_button = types.KeyboardButton("\U0001F519 Назад")
        markup.add(back_button)
        bot.send_message(message.chat.id, "Вы можете вернуться в главное меню:", reply_markup=markup)

    # Обработка кнопки "Назад"
    @bot.message_handler(func=lambda message: message.text == "\U0001F519 Назад")
    def go_back_to_main_menu(message):
        send_welcome(message)

# Запуск бота
if __name__ == "__main__":
    print("Бот запущен")
    bot.infinity_polling()


