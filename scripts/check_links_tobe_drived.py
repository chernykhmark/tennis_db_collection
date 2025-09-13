

from eurosport.driver import get_chrome_driver,get_page_source
from lib.mongo_connect import MongoDB
from datetime import datetime
from tqdm import tqdm
from bs4 import BeautifulSoup



def process_scheduled_html_of_matches():
    # 1. Подключение к MongoDB
    driver = get_chrome_driver()
    db = MongoDB()
    matches_dict = db.get_scheduled_matches_url_by_ids_dict()
    print(f"Получено {len(matches_dict)} документов")
    try:
        for match,link in tqdm(matches_dict.items()):
            try:
                # 2. Переход по ссылке
                page_source = get_page_source(driver,link)
                # 5. Парсинг нужного элемента
                soup = BeautifulSoup(page_source, 'html.parser')
                target_div = soup.find('div', {'id': 'detail', 'class': 'container__detailInner fullPage'})

                if target_div:
                    # 6. Немедленное сохранение в базу
                    db.db['matches'].update_one(
                        {"_id": match},
                        {"$set": {
                            "scheduled_html": str(target_div),
                            "status": "processed",
                            "processed_at": datetime.now()
                        }}
                    )
                    print(f"Обновлен {match}")
                else:
                    print(f"Элемент не найден на странице для игры {match}")

            except Exception as e:

                print(f"Error processing {match}: {e}")
                # Помечаем как ошибка, но продолжаем
                db.db['matches'].update_one(
                    {"_id": match},
                    {"$set": {"status": "error", "error": str(e)}}
                )
        print('sucsessfully done')
    finally:
        # 7. Закрываем соединение
        if driver:
            driver.quit()
            print('driver quit')

        db.close()
        print('db close')

if __name__=="__main__":
    process_scheduled_html_of_matches()