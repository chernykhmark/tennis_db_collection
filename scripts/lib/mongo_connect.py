from bson import ObjectId
from dotenv import load_dotenv
load_dotenv()
import logging
from typing import Dict

log = logging.getLogger(__name__)

from pymongo import MongoClient, UpdateOne
import os


class MongoDB:
    def __init__(self):
        # Данные для подключения
        self.MONGO_HOST = os.getenv('MONGO_HOST')
        self.MONGO_PORT = int(os.getenv('MONGO_PORT'))
        self.MONGO_USER = os.getenv('MONGO_USER')
        self.MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')
        self.MONGO_DB_NAME = os.getenv('MONGO_DB_NAME')
        self.MONGO_DATA_FILE_PATH = os.getenv('MONGO_DATA_FILE_PATH')

        connection_string = f"mongodb://{self.MONGO_USER}:{self.MONGO_PASSWORD}@{self.MONGO_HOST}:{self.MONGO_PORT}/"
        self.client = MongoClient(connection_string)
        self.db = self.client[self.MONGO_DB_NAME]
        print("Успешное подключение к MongoDB")

    def close(self):
        self.client.close()


    def get_scheduled_matches_url_by_ids_dict(self) -> Dict[str, str]:
        #Возвращает словарь {_id: match_url} из коллекции matches
        result_dict = {}
        cursor = self.db.matches.find(
            {"scheduled_html": ""},
            {"_id": 1, "scheduled_url": 1}
        )

        for doc in cursor:
            result_dict[str(doc["_id"])] = doc["scheduled_url"]
        return result_dict











# "new" - новый документ
#
# "processing" - в обработке
#
# "processed" - обработан
#
# "completed" - завершен
#
# "error" - ошибка обработки
#
# "archived" - архивный