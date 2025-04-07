import requests
from bs4 import BeautifulSoup
import telegram
import time
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler
from threading import Thread
import os
import asyncio

# Указываем токен от BotFather
bot_token = '7805081446:AAHe2t--zURAnjoSXs3TGwTq0XYE1B_kiX0'
chat_id = '2035796372'  # Ваш chat_id

# Инициализация Flask
app = Flask(__name__)

# Глобальные переменные для bot и application
bot = None
application = None

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
        global bot
        for ad in new_ads:
            bot.send_message(chat_id=chat_id, text=ad)
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")

# Обработчик команды /start
async def start(update: Update, context):
    print("Command /start received")
    await update.message.reply_text("Привет! Я буду присылать тебе новые объявления iPhone с OLX!")

# Функция для парсинга в фоновом режиме
def parse_and_send_ads():
    while True:
        new_ads = get_new_iphone_ads()
        if new_ads:
            send_to_telegram(new_ads)
        time.sleep(120)  # Пауза 2 минуты

# Webhook для получения обновлений от Telegram
@app.route(f'/{bot_token}', methods=['POST'])
async def webhook():
    print("Webhook received")
    try:
        global bot, application
        
        # Инициализация bot и application в webhook
        if not bot:
            bot = telegram.Bot(token=bot_token)
        if not application:
            application = Application.builder().token(bot_token).build()

        update = Update.de_json(request.get_json(), bot)  # Используем глобальную переменную bot
        await application.process_update(update)  # Асинхронно обрабатываем обновление
        print("Update processed successfully")
    except Exception as e:
        print(f"Error processing update: {e}")
    return '', 200

# Главная функция для парсинга в фоновом режиме
@app.route('/')
def home():
    return 'Бот работает!'

def set_telegram_webhook():
    try:
        # Устанавливаем вебхук для бота автоматически
        webhook_url = f'https://olx-bot-n7vf.onrender.com/{bot_token}'
        response = requests.get(f'https://api.telegram.org/bot{bot_token}/setWebhook?url={webhook_url}')
        
        # Логируем ответ от Telegram API
        if response.status_code == 200:
            print(f"Webhook set successfully: {response.text}")
        else:
            print(f"Failed to set webhook: {response.text}")
    except Exception as e:
        print(f"Error setting webhook: {e}")

def start_bot():
    global bot, application  # Определяем bot и application как глобальные переменные

    # Инициализация бота и приложения
    bot = telegram.Bot(token=bot_token)
    application = Application.builder().token(bot_token).build()

    # Обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # Установим вебхук для Telegram
    set_telegram_webhook()

    # Получаем порт из окружения Render (если он есть), если нет - используем 80
    port = os.environ.get('PORT', 80)

    # Запуск бота
    application.run_webhook(listen="0.0.0.0",
                            port=port,
                            url_path=bot_token,
                            webhook_url=f'https://olx-bot-n7vf.onrender.com/{bot_token}')

if __name__ == '__main__':
    # Запуск парсинга в фоновом потоке
    parse_thread = Thread(target=parse_and_send_ads)
    parse_thread.daemon = True
    parse_thread.start()
    
    # Запуск Flask-сервера и бота
    start_bot()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 80)))  # Используем порт из окружения
