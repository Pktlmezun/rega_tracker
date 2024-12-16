import time
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.devtools.v85.security import set_ignore_certificate_errors
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from dotenv import load_dotenv
load_dotenv(".env")


def send_telegram_notification(seats):
    bot_token = os.getenv("TG_BOT_TOKEN")
    chat_id = os.getenv("TG_ID")
    message = f"Free seats are now available: {seats}"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={message}"
    requests.get(url)
    print("Send Telegram notification")


# from notification import send_telegram_notification
# Replace these with your login credentials and course code
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
COURSE_CODE = os.getenv("COURSE_CODE")

# Initialize the WebDriver (use Chrome in this case)
# driver = webdriver.Chrome()

# chrome_options = Options()
# chrome_options.add_argument("--headless")  # Run Chrome in headless mode
# chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration (optional)
# chrome_options.add_argument("--window-size=1920,1080")  # Set window size (optional)
# chrome_options.add_argument("--no-sandbox")  # Required for some Linux environments
# chrome_options.add_argument("--disable-dev-shm-usage")  # Handle shared memory issues

# Initialize the WebDriver with headless options
service = Service()  # Replace with your chromedriver path
driver = webdriver.Chrome(service=service)


try:
    # Open the website
    driver.get("https://registrar.nu.edu.kz/user/login")  # Replace with the actual login URL

    # Find and fill the login form
    username_field = driver.find_element(By.ID, "edit-name")  # Replace with the correct ID or selector
    password_field = driver.find_element(By.ID, "edit-pass")  # Replace with the correct ID or selector

    username_field.send_keys(USERNAME)
    password_field.send_keys(PASSWORD)

    # Submit the form
    login_button = driver.find_element(By.ID, "edit-submit")  # Replace with the correct ID or selector
    login_button.click()

    # Wait until logged in and redirected to the dashboard
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "head")))

    # < a href = "/my-registrar/course-registration" > Course
    # registration < / a >

    # Navigate to course registration
    course_registration_link = driver.find_element(By.XPATH,
                                                   "//a[contains(@href, '/my-registrar/course-registration')]")  # Updated selector for course registration
    course_registration_link.click()

    # Wait for the course registration page to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "termPnl-body")))  # Replace with the correct ID
    time.sleep(1)
    print("Successfully logged in")
    # Search for the course

    # while True:
    #     time.sleep(3)
    search_bar = driver.find_element(By.ID, "titleText-inputEl")  # Replace with the correct ID or selector
    time.sleep(1)
    search_bar.clear()
    search_bar.send_keys(COURSE_CODE)
    search_bar.send_keys(Keys.RETURN)

    # Wait for search results to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.CLASS_NAME, "x-grid-cell-inner")))  # Replace with the correct class name or selector
    time.sleep(5)
    # Click the first course in the search results
    first_course = driver.find_element(By.CLASS_NAME,
                                       "x-grid-cell-inner")  # Replace with the correct class name or selector
    first_course.click()
    time.sleep(1)
    # Wait for the course details page to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.XPATH, "//tr/td/span[@style='font-weight:bold;']")))  # Replace with the correct ID or selector

    # course_code = driver.find_element(By.XPATH, "//tr/td/span[@style='font-weight:bold;']")
    # course_code.click()

    rows = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//tr/td/span[@style='font-weight:bold;']"))
    )

    # Iterate over the spans to extract seat numbers
    data = []
    available_seats = []

    i = 0
    j = 0
    found = False

    for row in rows:
        i = i + 1
        if i <= 2:
            continue
        j += 1
        text = row.text.strip()
        if j % 5 == 0:  # Check if the text is purely numeric (e.g., "24")
            available_seats.append(text)
            text = text[:5]
            try:
                if text.split("/")[0] != text.split("/")[1]:
                    print("FREE SEATS")
                    txt = "FREE SEATS " + COURSE_CODE
                    send_telegram_notification(txt)
                    found = True
                else:
                    print(text.split("/")[0], " TO ", text.split("/")[1])
            except IndexError:
                print("INDEX ERROR")
            # print(text, end="\n\n")
        else:
            # print(text, end="  ")
            data.append(text)
    print("WAITING........................")
    # time.sleep(10)
    print("SEARCHING......................")

except TimeoutException:
    print("An element was not found in time. Check your selectors and site loading times.")
finally:
    # Close the browser
    driver.quit()



