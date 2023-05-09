import sqlite3
from selenium import webdriver
from selenium.webdriver import Keys
import threading
from config import token
from selenium.webdriver.common.by import By
from datetime import datetime
import telebot
from PIL import Image
from time import sleep
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from io import BytesIO
import time


SCREENSHOTS_DIR = 'screenshots'
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.maximize_window()
bot = telebot.TeleBot(token)
con = sqlite3.connect('base.db', check_same_thread=False)
cursor = con.cursor()
# Создание таблицы в базе данных для хранения данных
cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, secondname TEXT,email TEXT,phone TEXT,birthdate TEXT,time TEXT')


#скриншот окна
def save_screenshot(user_id):

    # Получаем размеры экрана браузера
    screen_width = driver.execute_script("return window.innerWidth")
    screen_height = driver.execute_script("return window.innerHeight")

    # Создаем скриншот страницы
    screenshot = driver.get_screenshot_as_png()

    # Преобразуем скриншот в объект изображения Pillow
    image = Image.open(BytesIO(screenshot))

    # Обрезаем изображение до размеров экрана браузера
    image = image.crop((0, 0, screen_width, screen_height))

    # Генерируем имя файла с учетом текущей даты и времени и ID пользователя
    filename = datetime.now().strftime('%Y-%m-%d_%H-%M_') + str(user_id) + '.jpg'

    # Сохраняем изображение в папке проекта
    image.save('screenshots/' + filename, 'JPEG')

    driver.quit()

  
#Функция для добавления данных в бд
def add_user_to_bd(name, lastname, email, phone, birthdate):
    cursor = con.cursor()
  
    times = int(time.time())
    cursor.execute(f"INSERT INTO users (name, secondname, email, phone, birthdate, time) VALUES (?, ?, ?, ?, ?, ?)",
                   (name, lastname, email, phone, birthdate,times))
    con.commit()
    
    

    


# Функция для получения пользователей, которые отправили данные в последние 10 минут
def get_users_from_last_10_minutes():
    cursor = con.cursor()
    times = int(time.time())-600
    cursor.execute("SELECT id, name, secondname, email, phone, birthdate FROM users WHERE time > ?", (times,))
    
    results = cursor.fetchall()
    con.commit()
    return results

def feel_data_views(users):
    try:

        for user in users:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
            driver.maximize_window()
            sleep(2)
            driver.get("https://b24-iu5stq.bitrix24.site/backend_test/")
            sleep(5)
            driver.find_element(By.XPATH,'/html/body/main/div/section/div/div/div/div/div/div/div/div/div[2]/form/div[2]/div[1]/div/div/div/input').click()
            sleep(2)
            driver.find_element(By.XPATH,'/html/body/main/div/section/div/div/div/div/div/div/div/div/div[2]/form/div[2]/div[1]/div/div/div/input').send_keys(user[1])
            sleep(2)
            driver.find_element(By.XPATH,'/html/body/main/div/section/div/div/div/div/div/div/div/div/div[2]/form/div[2]/div[2]/div/div/div/input').click()
            sleep(2)
            driver.find_element(By.XPATH,'/html/body/main/div/section/div/div/div/div/div/div/div/div/div[2]/form/div[2]/div[2]/div/div/div/input').send_keys(user[2])
            driver.find_element(By.XPATH,'/html/body/main/div/section/div/div/div/div/div/div/div/div/div[2]/form/div[3]/div/button').click()
            sleep(2)
            driver.find_element(By.XPATH,'/html/body/main/div/section/div/div/div/div/div/div/div/div/div[2]/form/div[2]/div[1]/div/div/div/input').click()
            sleep(2)
            driver.find_element(By.XPATH,'/html/body/main/div/section/div/div/div/div/div/div/div/div/div[2]/form/div[2]/div[1]/div/div/div/input').send_keys(user[3])
            sleep(2)
            driver.find_element(By.XPATH,'/html/body/main/div/section/div/div/div/div/div/div/div/div/div[2]/form/div[2]/div[2]/div/div/div/input').click()
            sleep(2)
            driver.find_element(By.XPATH,'/html/body/main/div/section/div/div/div/div/div/div/div/div/div[2]/form/div[2]/div[2]/div/div/div/input').send_keys(user[4])
            sleep(2)
            driver.find_element(By.XPATH,'/html/body/main/div/section/div/div/div/div/div/div/div/div/div[2]/form/div[3]/div[2]/button').click()
            sleep(2)
            date_input = driver.find_element(By.XPATH,'/html/body/main/div/section/div/div/div/div/div/div/div/div/div[2]/form/div[2]/div/div/div/div/div[1]/input')



            driver.execute_script("arguments[0].setAttribute('value', arguments[1])", date_input, user[5])


            sleep(2)

            driver.find_element(By.XPATH,'/html/body/main/div/section/div/div/div/div/div/div/div/div/div[2]/form/div[4]/div[2]/button').click()
            sleep(5)
            save_screenshot(str(user[0]))
            sleep(2)
            
            
    except Exception as e:
        return f'Error {e}'

        



@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     'Пришлите ваши данные имя,фамилия,email,номер телефона,дата рождения как в примере:\n'
                     'Иван Иванов ivan@mail.ru +7928..... 26.05.2000')


@bot.message_handler(content_types=['text'])
def text(message):
    users = message.text.split()
    
    if len(users)==5:
        try:
            add_user_to_bd(users[0], users[1], users[2], users[3], users[4])
        except Exception as e:
            print(f'Error {e}')
    else:
        bot.send_message(message.chat.id,'Неверный формат данных')
    


def poll_bot():
    bot.polling()

def process_users():
   
    while True:
        users_list = get_users_from_last_10_minutes()
        print(users_list)
        if users_list:
            feel_data_views(users_list)
        time.sleep(600)


if __name__ == '__main__':
    bot_thread = threading.Thread(target=poll_bot)
    bot_thread.start()

    process_thread = threading.Thread(target=process_users)
    process_thread.start()
