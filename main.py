import selenium.webdriver
import mailfunc
import selenium
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
from flask import Flask
from flask import request

app = Flask(__name__)

def setup():
    # get usernames and passwords
    email = request.args.get('email')
    email_pss = request.args.get('email_pss')
    neu_usr = request.args.get('neu_usr')
    neu_pss = request.args.get('neu_pss')
    # email = input('What is your gmail? ')
    # email_pss = input('What is your gmail password? ')
    # neu_usr = input('What is your Northeastern SSO username? ')
    # neu_pss = input('What is your Northeastern SSO password? ')

    # set up mail
    global mail
    to_mail = f'{neu_usr}@northeastern.edu'
    mail = mailfunc.Mail(email, email_pss, to_mail)
    global msg
    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = to_mail
    msg['Subject'] = 'Waitlist Update'

    # open the link to my registration
    link = 'https://nubanner.neu.edu/ssomanager/c/SSB?pkg=bwskfshd.P_CrseSchdDetl'
    global driver
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = selenium.webdriver.Chrome(options)
    driver.get(link)

    # fill in username and password and submit
    driver.find_element(value='username').send_keys(neu_usr)
    driver.find_element(value='password').send_keys(neu_pss)
    driver.find_element(By.NAME, value='_eventId_proceed').click()

    # chill until we have gotten to the next part of SSO then switch to new frame
    btn_frame = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'duo_iframe')))
    driver.switch_to.frame(btn_frame)

    # now chill until button is clickable, then click it
    attempts = 0
    while attempts < 3:
        try:
            WebDriverWait(driver,
                        10).until(EC.element_to_be_clickable(
                            (By.XPATH, '//button[contains(., "Push")]'))).click()
        except:
            attempts += 1

    # NOW chill until we are on the next page then select 'Fall 2024 Semester' and submit
    driver.switch_to.default_content()
    slct = Select(
        WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.NAME, 'term_in'))))
    slct.select_by_value('202510')
    driver.find_element(By.XPATH, '//input[@value = "Submit"]').click()


# ok, so now we get the value that is my position on the waitlist
def get_pos():
    global driver
    driver.refresh()
    return int(
        driver.find_element(
            By.XPATH, '//tr[th[contains(., "Waitlist Position")]]/td').text)

@app.route('/main')
def main():
    setup()
    global mail
    global msg

    cur_pos = 100
    while cur_pos != 1:
        pos = get_pos()
        if pos < cur_pos:
            msg.set_payload(MIMEText(f'Waitlist position is now {pos}'))
            mail.send_email(msg)
            cur_pos = pos

        time.sleep(600)
    
@app.route('/')
def index():
    return '''<form action="/main" method="get">
                <input type="text" name="email" placeholder="gmail">
                <input type="text" name="email_pss" placeholder="gmail password">
                <input type="text" name="neu_usr" placeholder="NEU SSO login">
                <input type="text" name="neu_pss" placeholder = "NEU SSO password">
                <input type="submit" value="Start">
              </form>'''


if __name__ == '__main__':
    app.run(debug=True)