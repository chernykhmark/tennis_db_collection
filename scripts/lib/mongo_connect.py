from dotenv import load_dotenv
load_dotenv()
from logging import Logger
from pymongo import MongoClient
import os
import json
from pathlib import Path
from datetime import datetime
import uuid


class Mongo:
    def __init__(self):
        # Данные для подключения
        self.MONGO_HOST = os.getenv('MONGO_HOST')
        self.MONGO_PORT = int(os.getenv('MONGO_PORT', '27017'))
        self.MONGO_USER = os.getenv('MONGO_USER')
        self.MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')
        self.MONGO_DB_NAME = os.getenv('MONGO_DB_NAME')
        self.MONGO_DATA_FILE_PATH = os.getenv('MONGO_DATA_FILE_PATH')

        connection_string = f"mongodb://{self.MONGO_USER}:{self.MONGO_PASSWORD}@{self.MONGO_HOST}:{self.MONGO_PORT}/"
        self.client = MongoClient(connection_string)
        self.db = self.client[self.MONGO_DB_NAME]
        print("Успешное подключение к MongoDB")

    def process_files(self, directory_path=None, logger=None):
        if directory_path is None:
            directory_path = self.MONGO_DATA_FILE_PATH

        documents = {}

        # Ищем все файлы в директории
        for file_name in os.listdir(directory_path):
            file_path = os.path.join(directory_path, file_name)
            if os.path.isfile(file_path):
                if logger:
                    logger.info(f'processing {file_name}')

                # Разбираем имя файла
                parts = file_name.split('_')
                if len(parts) < 4:
                    continue  # Пропускаем файлы не соответствующие шаблону

                type_as = parts[0]  # "finished" или "scheduled"
                data_type = parts[1]  # "html" или "json"
                date_str = parts[2]  # "2025-09-10"
                time_str = parts[3].split('.')[0]  # "13-19-55"

                # Формируем ключ документа (type_as + timestamp)
                doc_key = f"{type_as}_{date_str}_{time_str}"
                updated_ts = datetime.strptime(f"{date_str}_{time_str}", "%Y-%m-%d_%H-%M-%S")

                # Читаем содержимое файла
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if data_type == 'json':
                            content = json.loads(content)
                except Exception as e:
                    if logger:
                        logger.error(f"Error reading file {file_name}: {e}")
                    continue

                # Создаем или обновляем документ
                if doc_key not in documents:
                    documents[doc_key] = {
                        "_id": str(uuid.uuid4()),  # Уникальный ID
                        "created_ts": datetime.utcnow(),
                        "updated_ts": updated_ts,
                        "type_as": type_as,
                        "status": "new",
                        "content": {
                            "json": None,
                            "html": None,
                            "other": None
                        }
                    }

                # Записываем данные в соответствующий блок
                if data_type == 'html':
                    documents[doc_key]["content"]["html"] = content
                elif data_type == 'json':
                    documents[doc_key]["content"]["json"] = content

        # Сохраняем все документы
        for doc_key, doc in documents.items():
            self.db.collection.insert_one(doc)
            if logger:
                logger.info(f'document with key {doc_key} saved')

    def close(self):
        self.client.close()


if __name__ == "__main__":
    db = Mongo()
    try:
        db.process_files(logger=Logger(__name__))
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        raise e
    finally:
        db.close()