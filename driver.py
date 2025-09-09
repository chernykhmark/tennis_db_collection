import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import pytz
import time
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
import undetected_chromedriver as uc
from datetime import datetime, timedelta
import subprocess

def print_current_datetime():
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    print(current_time)

def update_chrome_driver():
    result = subprocess.run(["/home/lev/tennis/chrome_update/chrome_update.sh"], capture_output=True, text=True)

    # Вывод результата выполнения скрипта
    print("Вывод:", result.stdout)
    print("Ошибки:", result.stderr)

def get_chrome_driver():
    options = uc.ChromeOptions()
    ua = UserAgent()
    user_agent = ua.random
    options.add_argument(f'--user-agent={user_agent}')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')

    # Для отладки сначала без headless
    options.add_argument('--headless=new')
    #options.add_argument("--disable-application-cache")
    #options.add_argument("--disable-cache")
    #driver = uc.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver = uc.Chrome(options=options,use_subprocess=True, version_main=140)
    print_current_datetime()
    print(f'START WITH user_agent : {user_agent}')
    return driver

def handle_cookie_popup(driver):
    try:
        button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
        if button:
            button.click()
    except ValueError as e:
        pass


def smooth_scroll(driver, scroll_down=True, scroll_up=True, num_iterations=2):
    def scroll_page(direction):
        if direction == 'down':
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        elif direction == 'up':
            driver.execute_script("window.scrollTo(0, 0);")
    for _ in range(num_iterations):
        if scroll_down:
            scroll_page('down')
            time.sleep(1)
        if scroll_up:
            scroll_page('up')


def driver_get_page_source(driver,URL):
    driver.get(URL)
    try:
        handle_cookie_popup(driver)
        print('driver handle')
    except:
        pass
    smooth_scroll(driver)
    print_current_datetime()
    print('driver works')
    time.sleep(1)
    try:
        li_element = driver.find_element(By.CSS_SELECTOR, 'li.splide__slide.cursor-pointer.is-active.is-visible')
        dt = driver.execute_script("return arguments[0].querySelector('div').getAttribute('data-slide-id');", li_element)
    except:
        dt = datetime.now().strftime("%Y-%m-%d")
    page_source = driver.page_source
    return page_source, dt

def driver_get_tommorow_page_source(driver,URL):
    driver.get(URL)
    try:
        handle_cookie_popup(driver)
        print('driver handle')
    except:
        pass
    print('driver go tomorrow works')
    day = datetime.now(pytz.timezone('Europe/Moscow'))  # укажи свой часовой пояс
    tomorrow = day + timedelta(days=1)
    tomorrow_date = tomorrow.strftime('%Y-%m-%d')
    print(f'tomorrow_date is {tomorrow_date}')

    try:
        # Находим блок div с data-testid="molecule-score-center-main-filter"
        main_filter_div = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="molecule-score-center-main-filter"]')


        slide_with_next_date = main_filter_div.find_element(By.CSS_SELECTOR, f'div[data-slide-id="{tomorrow_date}"]')
                # Внутри находим div с id="splide01-track"
#        splide_track = main_filter_div.find_element(By.ID, "splide01-track")

        # Внутри находим кнопку с data-testid="button-slide-content" и кликаем на нее
        button = slide_with_next_date.find_element(By.CSS_SELECTOR, 'button[data-testid="button-slide-content"]')
        button.click()
        print("Кнопка была успешно нажата.")
        smooth_scroll(driver)
        print_current_datetime()
        time.sleep(3)
#        li_element = driver.find_element(By.CSS_SELECTOR, 'li.splide__slide.cursor-pointer.is-visible.is-active')
        #dt = tomorrow_date # driver.execute_script("return arguments[0].querySelector('div').getAttribute('data-slide-id');", li_element)
    except Exception as e:
        print(f"Произошла ошибка: {e}")


    page_source = driver.page_source
    return page_source
