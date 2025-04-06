import requests
from bs4 import BeautifulSoup
import telegram
import time
from flask import Flask
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, JobQueue
from threading import Thread

# Указываем токен от BotFather
bot_token = '7805081446:AAHe2t--zURAnjoSXs3TGwTq0XYE1B_kiX0'
chat_id = '2035796372'  # Ваш chat_id

# Инициализация Flask
app = Flask(__name__)

# Функция для парсинга OLX
def get_new_iphone_ads():
    try:
        url = 'https://www.olx.pl/elektronika/telefony/iphone/'
        response = requests.get(url)
        response.raise_for_status()  # Проверяем, что запрос успешен
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Найти все элементы с объявлениями (можно уточнить селекторы)
        ads = soup.find_all('div', {'class': 'offer-wrapper'})
        
        # Собираем ссылки и заголовки объявлений
        new_ads = []
        for ad in ads:
            title = ad.find('strong').get_text() if ad.find('strong') else 'Без названия'
            link = ad.find('a')['href']
            new_ads.append(f'{title}\n{link}')
        
        return new_ads
    except Exception as e:
        print(f"Ошибка при парсинге: {e}")
        return []

# Отправляем сообщения в Telegram
def send_to_telegram(new_ads):
    try:
        bot = telegram.Bot(token=bot_token)
        for ad in new_ads:
            bot.send_message(chat_id=chat_id, text=ad)
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")

# Обработчик команды /start
def start(update: Update, context: CallbackContext):
    print("Command /start received")  # Логирование получения команды /start
    update.message.reply_text("Привет! Я буду присылать тебе новые объявления iPhone с OLX!")

# Функция для парсинга в фоновом режиме
def parse_and_send_ads(context: CallbackContext):
    new_ads = get_new_iphone_ads()
    if new_ads:
        send_to_telegram(new_ads)

# Главная функция для запуска бота
def start_bot():
    # Настроим Updater и Dispatcher
    updater = Updater(bot_token, use_context=True)
    dp = updater.dispatcher
    
    # Обработчик команды /start
    dp.add_handler(CommandHandler("start", start))

    # Настройка JobQueue для регулярного запуска парсинга
    job_queue = updater.job_queue
    job_queue.run_repeating(parse_and_send_ads, interval=120, first=0)  # Повторение каждые 2 минуты

    # Запуск бота
    updater.start_polling()

# Главная функция, которая будет запускать Flask-сервер
@app.route('/')
def home():
    return 'Бот работает!'

if __name__ == '__main__':
    # Запуск Flask в отдельном потоке
    flask_thread = Thread(target=lambda: app.run(host='0.0.0.0', port=80))
    flask_thread.daemon = True
    flask_thread.start()

    # Запуск бота
    start_bot()
