from eurosport.driver import driver_get_page_source
from eurosport.update_results import request_and_return_html
from bs4 import BeautifulSoup
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

URL = 'https://www.flashscore.co.uk/match/tennis/haddad-maia-beatriz-lSABz6E8/pigossi-laura-l2FaZpEP/h2h/all-surfaces/?mid=IN3AlWLc'


def compare_html_sources():
    try:
        # Получаем HTML из requests
        html = request_and_return_html(URL)
        if not html:
            logger.error("Failed to get HTML from requests")
            return

        # Получаем HTML из Selenium
        page_source = driver_get_page_source(URL)
        if not page_source:
            logger.error("Failed to get HTML from Selenium")
            return

        # Парсим requests HTML
        soup_request = BeautifulSoup(html, 'html.parser')
        request_result = soup_request.find('div', class_="container__detailInner fullPage")

        # Парсим Selenium HTML
        soup_driver = BeautifulSoup(page_source, 'html.parser')
        driver_result = soup_driver.find('div', class_="container__detailInner fullPage")

        # Сохраняем результаты
        with open('./request.html', 'w', encoding='utf-8') as file:
            if request_result:
                file.write(request_result.prettify())
                logger.info("Request HTML saved successfully")
            else:
                file.write("<!-- Element not found in requests HTML -->")
                logger.warning("Element not found in requests HTML")

        with open('./driver.html', 'w', encoding='utf-8') as file:
            if driver_result:
                file.write(driver_result.prettify())
                logger.info("Driver HTML saved successfully")
            else:
                file.write("<!-- Element not found in driver HTML -->")
                logger.warning("Element not found in driver HTML")

        # Сравниваем результаты
        if request_result and driver_result:
            if request_result.prettify() == driver_result.prettify():
                logger.info("Both sources return identical HTML")
            else:
                logger.info("Sources return different HTML")
        else:
            logger.info("One or both elements not found for comparison")

    except Exception as e:
        logger.error(f"Error during comparison: {e}")


if __name__ == "__main__":
    compare_html_sources()