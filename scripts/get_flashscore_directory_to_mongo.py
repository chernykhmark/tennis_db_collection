
from lib.mongo_connect import MongoDB
import logging

log = logging.getLogger(__name__)

if __name__ == "__main__":
    db = MongoDB()
    try:
        # СОЕДЕНИМ ДАННЫЕ С ИСТОЧНИКА В ОДИН БАЗОВЫЙ ОБЪЕК COLLECTION

        db.process_origin_files_from_directory(log)

        # РАЗЛОЖИМ КАЖДЫЙ МАТС В НОВУЮ КОЛЛЕКЦИЮ  MATCHES
        docs = db.get_new_doc('collection', 'finished', log)
        db.create_matches(docs, 'finished')

        docs = db.get_new_doc('collection', 'scheduled', log)
        db.create_matches(docs, 'scheduled')

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        raise e
    finally:
        db.close()



      #