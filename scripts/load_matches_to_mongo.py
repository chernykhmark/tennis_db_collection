
from lib.mongo_connect import MongoDB
from eurosport.notifications import BotSender
from datetime import datetime

def make_new_objects_in_mongo():
    db = MongoDB()
    bot = BotSender()
    try:
        # СОЕДЕНИМ ДАННЫЕ С ИСТОЧНИКА В ОДИН БАЗОВЫЙ COLLECTION
        print(f"{datetime.now()} загружаем новые коллекции {'_' * 60}\n")
        db.process_origin_from_directory_to_docs()

        print(f"{datetime.now()} ищем обновления в коллекциях {'_' * 60}\n")
        docs = db.find_new_scheduled_docs()

        print(f"{datetime.now()} создаем новые матчи {'_' * 60}\n")
        db.create_future_matches(docs)

    except Exception as e:
        error_msg = f"[{datetime.now()}] Ошибка в скрипте: {str(e)}"
        bot.send_notification(error_msg, script_name='get_mongo_links_and_bring_back_html.py')
        print(error_msg)
    finally:
        db.close()

if __name__ == "__main__":
    make_new_objects_in_mongo()
