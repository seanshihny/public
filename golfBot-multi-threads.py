from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
import time
import datetime
from multiprocessing import Pool

def run(pid):
    options = Options()
    driver = webdriver.Chrome('/usr/local/bin/chromedriver', options=options)  # Make sure you chromedriver location
    base_url = 'https://stage.foreupsoftware.com/'
    my_email = ''             # Enter your account login
    my_password = ''          # Enter your password
    desired_course = 'red'    # Enter black/red/blue/yellow
    driver.get(base_url + '/index.php/booking/19765/2431#welcome')
    driver.find_element_by_class_name('login').click()
    driver.find_element_by_id('login_email').clear()
    driver.find_element_by_id('login_email').send_keys(my_email)
    driver.find_element_by_id('login_password').clear()
    driver.find_element_by_id('login_password').send_keys(my_password)
    driver.find_element_by_xpath("//div[@id='login']/div/div[3]/div/button").click()

    existing_reservation = False
    wait = WebDriverWait(driver, 5)
    try:
        if wait.until(EC.presence_of_element_located((By.CLASS_NAME,'reservations'))):
            existing_reservation = True
    except TimeoutException as TE:
        print(TE)

    if existing_reservation:
        reservation = driver.find_element_by_xpath("//a[contains(.,'Reservations')]")
        reservation.click()
        print('[p%s]: Start making reservation' % pid)
    else:
        reserveTeeTime = wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Reserve a time now.")))
        reserveTeeTime.click()
    # Select Resident
    driver.find_element_by_xpath("//button[contains(.,'Resident')]").click()
    print('[p%s]: Select Resident: %s' % (pid, desired_course))

    # Select Black/Red course
    selectCourses = wait.until(EC.presence_of_element_located((By.ID, "schedule_select")))
    if desired_course == 'black':
        driver.find_element_by_xpath("//*[@id='schedule_select']/option[1]").click()
    if desired_course == 'red':
        driver.find_element_by_xpath("//*[@id='schedule_select']/option[7]").click()
    if desired_course == 'yellow':
        driver.find_element_by_xpath("//*[@id='schedule_select']/option[8]").click()
    print('[p%s]: Selected course' % pid)
    # click Resident (except for Black course)
    try:
        if driver.find_element_by_xpath("//button[contains(.,'Resident')]"):
            driver.find_element_by_xpath("//button[contains(.,'Resident')]").click()
    except NoSuchElementException:
        print('No need to click Resident for Black course')
    selectPlayers = wait.until(EC.presence_of_element_located((By.LINK_TEXT, "4")))
    selectPlayers.click()
    # Clear Date input field
    for i in range(10):
        driver.find_element_by_id("date-field").send_keys(Keys.BACK_SPACE)
    datetime_7 = datetime.datetime.now() + datetime.timedelta(days=7)
    datetime_str = datetime_7.strftime('%m-%d-%Y')
    driver.find_element_by_id("date-field").send_keys(datetime_str)
    print('[p%s]: Selected date/time: %s' % (pid, datetime_str))

    # Wait here until 7PM exactly
    now = time.localtime()
    while True:
        if now.tm_hour >= 19:
            if now.tm_min >= 0:
                if now.tm_sec >= 0:
                    print('[p%s]: Times up' % pid)
                    break
        else:
            now = time.localtime()

    # Input Date
    print(datetime.datetime.now())
    driver.find_element_by_id("date-field").send_keys(Keys.ENTER)
    print('[p%s]: Entered date/time' % pid)
    print('[p%s]: Wait for available tee times' % pid)
    time.sleep(0.8)
    try:
        # driver.find_element_by_css_selector("div.reserve-time").click()
        driver.find_element_by_xpath("//ul[@id='times']/li[3]").click()
        driver.find_element_by_xpath("//button[contains(.,'Book Time')]").click()
        print('[p%s]: Clicked: book time' % pid)
        print(datetime.datetime.now())
        print('[p%s]: Completed reservation done' % pid)
        if driver.find_elements_by_xpath("//*[contains(text(), 'Congratulations!')]"):
            print('[p%s]: Congratulations !' % pid)
        else:
            print('[p%s]: Bad luck today!' % pid)
    except NoSuchElementException:
        print('[p%s]: No tee time' % pid)
    finally:
        logout = wait.until(EC.presence_of_element_located((By.XPATH,"//a[contains(.,' Logout')]")))
        logout.click()
        print('[p%s]: logout' % pid)
    driver.quit()

if __name__ == "__main__":
    p = Pool(4)              # Enter your desired threads
    p.map(run, [1, 2, 3, 4]) # Match your threads