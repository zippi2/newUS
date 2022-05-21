import config
import telebot
import requests
import sqlite3 as sql
from bs4 import BeautifulSoup
from telebot.apihelper import ApiTelegramException
bot = telebot.TeleBot(config.Token)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Вітаю читачу!\n Для уточнення функціоналу набери /help")
    nameBD='user.db' #робота з БД
    con = sql.connect(nameBD)
    with con:
            cur = con.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS nameBD (`user_id` STRING, `nick` STRING, `first_name` STRING,`last_name` STRING, `chat_id` STRING)")
            cur.execute("SELECT * FROM nameBD WHERE user_id=?",(message.from_user.id,))
            rows = cur.fetchall()
            if not rows:
                with con:
                    cur = con.cursor()
                    #cur.execute("CREATE TABLE IF NOT EXISTS nameBD (`user_id` STRING, `nick` STRING, `first_name` STRING,`last_name` STRING, `chat_id` STRING")
                    user_id = message.from_user.id
                    nick = message.chat.username
                    first_name = message.chat.first_name
                    last_name = message.chat.last_name
                    chat_id = message.chat.id
                    cur.execute(f"INSERT INTO nameBD VALUES ('{user_id}', '{nick}', '{first_name}', '{last_name}', '{chat_id}')")
                    bot.send_message(message.chat.id, text="Ви підписались на розсилку від Горошинки\nДля отримання останніх новин на тисніть на 👉👉👉 /lnews\nТакож ви отримуватиме інформацію про оновлення")
            else:
                bot.send_message(message.chat.id, text="Для отримання останніх новин на тисніть на 👉👉👉 /lnews\nТакож ви підписались на автоматичне інфомування ")

@bot.message_handler(commands=['help'])
def start(message):
    bot.send_message(message.chat.id, "Тобі це справд цікаво???\n Ти вже знайомий(а) з командами  /start та /help\nПрисутні ще:\n  /lnews - отримати останні новини\n  /sendlnews - розіслати всім користувачам останні новини\n  /sendmessage - розіслати сім користувачам індивідуальне повідомлення")

@bot.message_handler(commands=['sendlnews'])
def start(message):
    nameBD='user.db' #робота з БД
    con = sql.connect(nameBD)
    url = 'https://litwebforum.kh.ua/'
    r = requests.get(url)
    data = r.text 
    soup = BeautifulSoup(data, 'lxml')
            #print(soup)
    global href
    href = soup.find('div', class_='read-title').find('a').get('href') # Посилання на статтю
    global info
    info = soup.find('div', class_='read-title').text #текст статті
    info = info.replace('\n', '')
    text = f'[{info}]({href})'
    with con:
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS nameBD (`user_id` STRING, `nick` STRING, `first_name` STRING,`last_name` STRING, `chat_id` STRING)")
        cur.execute("SELECT user_id FROM nameBD")
        rows = cur.fetchall()
        i=0
        ##print(rows[1][0])
        # list = [[1,2][3.4][2,4][]]
        #print(type(rows[1]))
        #bot.send_message(rows[1], text="давно не бачились")
        while i<len(rows):

            try:
                bot.send_message(rows[i][0], 'Ви могли пропустити нашу останнбю статтю '+str(text), parse_mode='markdown')
            except ApiTelegramException as e:
                if e.description == "Forbidden: bot was blocked by the user":
                    print("Увага користувач з id {} заборонив надсилати йому повідрмлення  ".format(rows[i][0]))
                else:
                    print('Невідома проблема1 зверніться в підтримку')
            i=i+1
        bot.send_message(message.chat.id, "Ви розіслали повідмлення про оновлення всім користувачам")

@bot.message_handler(commands=['sendmessage'])
def start(message):
    bot.send_message(message.chat.id, "Про що ти хочеш розповісти своїм читачам?")
    bot.register_next_step_handler(message, getmessage)

def getmessage(message):
    message = message.text
    nameBD='user.db' #робота з БД
    con = sql.connect(nameBD)
    with con:
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS nameBD (`user_id` STRING, `nick` STRING, `first_name` STRING,`last_name` STRING, `chat_id` STRING)")
        cur.execute("SELECT user_id FROM nameBD")
        rows = cur.fetchall()
        i=0
        #print(len(rows))
        #print(rows[1][0])
        #print(type(rows[1]))
        #bot.send_message(rows[1], text="давно не бачились")
        while i<len(rows):
            try:
                bot.send_message(rows[i][0], message)
            except ApiTelegramException as e:
                if e.description == "Forbidden: bot was blocked by the user":
                    print("Увага користувач з id {} заборонив надсилати йому повідрмлення  ".format(message.chat.id))
                else:
                   
                    print('Невідома проблема2 зверніться в підтримку')
            i=i+1
        bot.send_message(message.chat.id, "Ви розіслали повідмлення про оновлення всім користувачам")
      

@bot.message_handler(commands=['lnews'])
def getlastnews(message):
    url = 'https://litwebforum.kh.ua/'
    r = requests.get(url)
    data = r.text 
    soup = BeautifulSoup(data, 'lxml')
    #print(soup)
    global href
    href = soup.find('div', class_='read-title').find('a').get('href') # Посилання на статтю
    global info
    info = soup.find('div', class_='read-title').text #текст статті
    info = info.replace('\n', '')
    text = f'[{info}]({href})'
    bot.send_message(message.chat.id, text, parse_mode='markdown')
    #bot.send_message(message.chat.id, href)
    

if __name__ == '__main__':
     bot.infinity_polling()


