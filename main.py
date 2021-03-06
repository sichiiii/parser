import telebot, os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait  
from selenium.webdriver.chrome.options import Options 
from flask import Flask

bot = telebot.TeleBot('<TOKEN>')

week_name = 0
group_name = '0'

@bot.message_handler(commands=['start'])
def startMessage(message):
    bot.send_message(message.chat.id, 'Hi! Enter group or week')
    bot.register_next_step_handler(message, getMessage)

def getMessage(message):
    global week_name
    global group_name
    if week_name == 0 or group_name == '0':
        try:
            week_name = int(message.text)
            if week_name < 2 or week_name > 8: 
                bot.register_next_step_handler(message, getMessage)
        except Exception:
            group_name = message.text
            bot.register_next_step_handler(message, getMessage)
    if week_name != 0 and group_name != '0':
        getScreen(week_name, group_name, message)
        week_name = 0 
        group_name = 0

def getScreen(week_name, group_name, message):
    try:
        option = webdriver.ChromeOptions()
        option.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        option.add_argument('--headless')
        option.add_argument('--disable-dev-sh-usage')
        option.add_argument('--disable-gpu')
        option.add_argument('--no-sandbox')
        browser = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=option)
        
        link = f'https://www.polessu.by/ruz/term2/?q={group_name}'
        browser.get(link)
        browser.set_window_size(1000,1200)
        browser.find_element_by_xpath('/html/body/section/div/div/div[2]/div/button').click()
        browser.find_element_by_xpath(f'//*[@id="weeks-menu"]/li[{week_name}]/a').click()

        screenshot = browser.save_screenshot("my_screenshot.png")
        browser.quit()
        
        sendPhoto()
    except Exception:
        bot.send_message(message.chat.id, 'Oops! Something went wrong! Try another group or week: /start')
        
def sendPhoto():
    bot.send_photo(message.chat.id, open('my_screenshot.png', 'rb'))
    
server = Flask(__name__)
@server.route("/bot", methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200
@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.polling(none_stop=True)
    return "?", 200
server.run(host="0.0.0.0", port=os.environ.get('PORT', 5000))
