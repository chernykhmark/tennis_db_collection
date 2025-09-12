
from lib.mongo_connect import MongoDB
import logging
from tqdm import tqdm
from eurosport.update_results import request_and_return_html
from eurosport.notifications import BotSender
from datetime import datetime


if __name__ == "__main__":
    db = MongoDB()
    bot = BotSender()
    try:
        result_dict = db.get_matches_url_by_ids_dict()
        if len(result_dict) > 100:
            items = list(result_dict.items())

            # Разбиваем на батчи по 25 элементов
            batch_size = 25
            batches = [items[i:i + batch_size] for i in range(0, len(items), batch_size)]

            # Обрабатываем каждый батч
            for i, batch in tqdm(enumerate(batches, 1)):
                batch_dict = dict(batch)
                print(f"Обрабатываем батч {i}/{len(batches)} ({len(batch_dict)} элементов)")

                # Вызываем функцию обработки для текущего батча
                html_data_dict = {}
                for key,value in tqdm(batch_dict.items()):
                   html_data_dict[key] = request_and_return_html(value)

                db.update_matches_html(html_data_dict)
                print(f'Батч № {i} отправлен в базу')
        else:
            html_data_dict = {}
            for key, value in tqdm(result_dict.items()):
                html_data_dict[key] = request_and_return_html(value)

            db.update_matches_html(html_data_dict)
            print(f'Батч до 100 элементов отправлен в базу')

    except Exception as e:
        error_msg = f"[{datetime.now()}] Ошибка в скрипте: {str(e)}"
        bot.send_notification(error_msg, script_name='get_mongo_links_and_bring_back_html.py')
        print(error_msg)
    finally:
        db.close()