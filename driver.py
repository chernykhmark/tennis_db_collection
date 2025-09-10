import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import pytz
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
import undetected_chromedriver as uc
from datetime import datetime, timedelta
from tqdm import tqdm
from selenium.common.exceptions import TimeoutException

def print_current_datetime():
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    print(current_time)


def get_chrome_driver():
    options = uc.ChromeOptions()
    ua = UserAgent()
    user_agent = ua.random
    options.add_argument(f'--user-agent={user_agent}')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--headless=new')
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


def driver_get_page_source(URL):
    driver = get_chrome_driver()
    #driver.get(URL)

    driver.set_page_load_timeout(30)  # 30 секунд максимум

    try:
        driver.get(URL)
    except TimeoutException:

        driver.quit()
        return TimeoutException
    try:
        handle_cookie_popup(driver)
        print('driver handle')
    except:
        pass
    smooth_scroll(driver)
    print_current_datetime()
    print('driver works')
    time.sleep(1)

    page_source = driver.page_source
    driver.quit()
    if not driver:
        print('driver quit')

    return page_source

def driver_get_tommorow_page_source(URL):
    driver = get_chrome_driver()
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
        main_filter_div = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="molecule-score-center-main-filter"]')
        slide_with_next_date = main_filter_div.find_element(By.CSS_SELECTOR, f'div[data-slide-id="{tomorrow_date}"]')
        button = slide_with_next_date.find_element(By.CSS_SELECTOR, 'button[data-testid="button-slide-content"]')
        button.click()
        print("Кнопка была успешно нажата.")
        smooth_scroll(driver)
        print_current_datetime()
        time.sleep(3)
    except Exception as e:
        print(f"Произошла ошибка: {e}")


    page_source = driver.page_source
    driver.quit()
    if not driver:
        print('driver quit')

    return page_source


def load_scheduled_dict(driver):
    main_div = driver.find_element(By.CSS_SELECTOR, 'div[id="fsbody"]')
    filters_group = main_div.find_element(By.CSS_SELECTOR, 'div[class="filters__group"]')

    # Добавьте точку в начале XPath для поиска только внутри filters_group
    scheduled_tab = filters_group.find_element(By.XPATH, ".//div[text()='Scheduled']")
    scheduled_tab.click()
    print("Кнопка Scheduled нажата.")
    time.sleep(5)
    tennis_games_div = main_div.find_element(By.CSS_SELECTOR, 'div[class="sportName tennis"]')

    games_dict = {}
    all_elements = tennis_games_div.find_elements(By.XPATH, './div')
    current_key = None
    href_list = []
    for element in tqdm(all_elements):
        if 'headerLeague__wrapper' in element.get_attribute('class'):
            # Сохраняем предыдущую группу
            if current_key is not None:
                games_dict[current_key] = href_list
            # Начинаем новую группу
            current_key = element.text
            href_list = []
        elif element.get_attribute('data-event-row') == 'true':
            # Ищем ссылку внутри элемента
            try:
                link = element.find_element(By.TAG_NAME, 'a')
                href = link.get_attribute('href')
                href_list.append(href)
            except:
                continue

    # Добавляем последнюю группу
    if current_key is not None:
        games_dict[current_key] = href_list

    # Сохранение
    import json
    with open(f'data/scheduled_json_{datetime.now()}.json', 'w', encoding='utf-8') as f:
        json.dump(games_dict, f, ensure_ascii=False, indent=2)

    print("Словарь сохранен в scheduled_dict.json")

    page_source = driver.page_source
    with open(f'data/scheduled_html_{datetime.now()}.html', 'w') as file:
        file.write(page_source)

def load_finished_dict(driver):
    main_div = driver.find_element(By.CSS_SELECTOR, 'div[id="fsbody"]')
    filters_group = main_div.find_element(By.CSS_SELECTOR, 'div[class="filters__group"]')

    # Добавьте точку в начале XPath для поиска только внутри filters_group
    scheduled_tab = filters_group.find_element(By.XPATH, ".//div[text()='Finished']")
    scheduled_tab.click()
    print("Кнопка Finished была нажата.")
    time.sleep(5)
    tennis_games_div = main_div.find_element(By.CSS_SELECTOR, 'div[class="sportName tennis"]')

    games_dict = {}
    all_elements = tennis_games_div.find_elements(By.XPATH, './div')
    current_key = None
    href_list = []
    for element in tqdm(all_elements):
        if 'headerLeague__wrapper' in element.get_attribute('class'):
            # Сохраняем предыдущую группу
            if current_key is not None:
                games_dict[current_key] = href_list
            # Начинаем новую группу
            current_key = element.text
            href_list = []
        elif element.get_attribute('data-event-row') == 'true':
            # Ищем ссылку внутри элемента
            try:
                link = element.find_element(By.TAG_NAME, 'a')
                href = link.get_attribute('href')
                href_list.append(href)
            except:
                continue

    # Добавляем последнюю группу
    if current_key is not None:
        games_dict[current_key] = href_list

    # Сохранение
    import json
    with open(f'data/finished_json_{datetime.now()}.json', 'w', encoding='utf-8') as f:
        json.dump(games_dict, f, ensure_ascii=False, indent=2)

    print("Словарь сохранен в finished_dict.json")

    page_source = driver.page_source
    with open(f'data/finished_html_{datetime.now()}.html', 'w') as file:
        file.write(page_source)





def driver_get_flashscore(URL):
    driver = get_chrome_driver()
    driver.get(URL)

    # try:
    #     handle_cookie_popup(driver)
    # except:
    #     print('no pop-up fot handle')

    smooth_scroll(driver)
    print('driver smooth_scroll')
    time.sleep(1)

    print('start load_scheduled_dict')
    try:
        load_scheduled_dict(driver)
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    time.sleep(5)

    print('start load_finished_dict')
    try:
        load_finished_dict(driver)
    except Exception as e:
        print(f"Произошла ошибка: {e}")

    finally:
        driver.quit()
        print('driver quit')
        print_current_datetime()

