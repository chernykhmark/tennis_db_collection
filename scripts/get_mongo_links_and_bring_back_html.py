
from lib.mongo_connect import MongoDB
import logging

log = logging.getLogger(__name__)

if __name__ == "__main__":
    db = MongoDB()
    try:
        json_array = db.process_origin_files_from_directory(log)
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        raise e
    finally:
        db.close()