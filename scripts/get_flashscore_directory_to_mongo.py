
from lib.mongo_connect import MongoDB
from eurosport.notifications import BotSender
from datetime import datetime



if __name__ == "__main__":
    db = MongoDB()
    bot = BotSender()
    try:
        # СОЕДЕНИМ ДАННЫЕ С ИСТОЧНИКА В ОДИН БАЗОВЫЙ ОБЪЕК COLLECTION

        db.process_origin_files_from_directory()

        # РАЗЛОЖИМ КАЖДЫЙ МАТС В НОВУЮ КОЛЛЕКЦИЮ  MATCHES
        docs = db.get_new_doc('collection', 'finished')
        db.create_matches(docs, 'finished')

        docs = db.get_new_doc('collection', 'scheduled')
        db.create_matches(docs, 'scheduled')

    except Exception as e:
        error_msg = f"[{datetime.now()}] Ошибка в скрипте: {str(e)}"
        bot.send_notification(error_msg, script_name='get_mongo_links_and_bring_back_html.py')
        print(error_msg)
    finally:
        db.close()



      #