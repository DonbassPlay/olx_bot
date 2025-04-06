import requests
import telegram
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from flask import Flask, request
import os
from threading import Thread

# Указываем токен от BotFather
bot_token = '7805081446:AAHe2t--zURAnjoSXs3TGwTq0XYE1B_kiX0'
chat_id = '2035796372'  # Ваш chat_id

# Инициализация Flask
app = Flask(__name__)

# Инициализация бота и диспетчера
bot = telegram.Bot(token=bot_token)

# Обработчик команды /start
def start(update: Update, context: CallbackContext):
    print("Command /start received")
    update.message.reply_text("Привет! Я буду присылать тебе новые объявления iPhone с OLX!")

# Webhook для получения обновлений от Telegram
@app.route(f'/{bot_token}', methods=['POST'])
def webhook():
    print("Webhook received")
    try:
        update = Update.de_json(request.get_json(), bot)
        print("Update:", update)  # Добавим вывод данных для проверки
        dp.process_update(update)
        print("Update processed successfully")
    except Exception as e:
        print(f"Error processing update: {e}")
    return '', 200

# Главная функция для парсинга в фоновом режиме
@app.route('/')
def home():
    return 'Бот работает!'

# Настроим Updater и Dispatcher
def start_bot():
    global dp
    updater = Updater(bot_token, use_context=True)
    dp = updater.dispatcher

    # Обработчик команды /start
    dp.add_handler(CommandHandler("start", start))

    # Устанавливаем вебхук через Telegram API
    response = requests.get(f'https://api.telegram.org/bot{bot_token}/setWebhook?url=https://olx-bot-n7vf.onrender.com/{bot_token}')
    print(f"Webhook set response: {response.text}")  # Логируем ответ от Telegram API

    # Установим вебхук
    bot.set_webhook(url=f'https://olx-bot-n7vf.onrender.com/{bot_token}')

    # Получаем порт из окружения Render (если он есть), если нет - используем 80
    port = os.environ.get('PORT', 80)

    # Запуск бота
    updater.start_webhook(listen="0.0.0.0",
                          port=port,
                          url_path=bot_token,
                          webhook_url=f'https://olx-bot-n7vf.onrender.com/{bot_token}')

if __name__ == '__main__':
    # Запуск бота в фоновом потоке
    bot_thread = Thread(target=start_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Запуск Flask-сервера
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 80)))  # Используем порт из окружения
