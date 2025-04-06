import requests
from bs4 import BeautifulSoup
import telegram
import time

# Указываем токен от BotFather
bot_token = '7805081446:AAHe2t--zURAnjoSXs3TGwTq0XYE1B_kiX0'
chat_id = 'ТВОЙ_CHAT_ID'  # Замените на свой chat_id

# Функция для парсинга OLX
def get_new_iphone_ads():
    url = 'https://www.olx.pl/elektronika/telefony/iphone/'
    response = requests.get(url)
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

# Отправляем сообщения в Telegram
def send_to_telegram(new_ads):
    bot = telegram.Bot(token=bot_token)
    for ad in new_ads:
        bot.send_message(chat_id=chat_id, text=ad)

# Главная функция
def main():
    while True:
        new_ads = get_new_iphone_ads()
        if new_ads:
            send_to_telegram(new_ads)
        time.sleep(120)  # Пауза 2 минуты

if __name__ == '__main__':
    main()
    