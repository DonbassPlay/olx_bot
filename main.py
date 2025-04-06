import requests
from bs4 import BeautifulSoup
import telegram
from flask import Flask
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import threading
import time

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
    update.message.reply_text("Привет! Я буду присылать тебе новые объявления iPhone с OLX!")

# Главная функция, которая будет запускать бота в фоновом режиме
@app.route('/')
def home():
    return 'Бот работает!'

# Запуск бота и Flask
def start_bot():
    # Настроим Updater и Dispatcher
    updater = Updater(bot_token, use_context=True)
    dp = updater.dispatcher
    
    # Обработчик команды /start
    dp.add_handler(CommandHandler("start", start))
    
    # Запуск бота
    updater.start_polling()

    # Запуск парсинга каждые 2 минуты
    while True:
        new_ads = get_new_iphone_ads()
        if new_ads:
            send_to_telegram(new_ads)
        time.sleep(120)  # Пауза 2 минуты

if __name__ == '__main__':
    # Запуск бота в фоновом потоке
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Запуск Flask-сервера
    app.run(host='0.0.0.0', port=80)
