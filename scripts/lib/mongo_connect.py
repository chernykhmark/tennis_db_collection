from typing import Dict

from bson import ObjectId
from dotenv import load_dotenv
load_dotenv()
import logging

log = logging.getLogger(__name__)

from pymongo import MongoClient, UpdateOne
import os
import json
from datetime import datetime
import uuid
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


class MongoDB:
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

    def close(self):
        self.client.close()


    def process_origin_files_from_directory(self,log):

        directory_path = self.MONGO_DATA_FILE_PATH

        documents = {}

        # Ищем все файлы в директории
        for file_name in os.listdir(directory_path):
            file_path = os.path.join(directory_path, file_name)
            if os.path.isfile(file_path):
                log.info(f'processing {file_name}')

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
                created_ts = datetime.strptime(f"{date_str}_{time_str}", "%Y-%m-%d_%H-%M-%S")

                # Читаем содержимое файла
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if data_type == 'json':
                            content = json.loads(content)
                except Exception as e:

                    log.error(f"Error reading file {file_name}: {e}")
                    continue

                # Создаем или обновляем документ
                if doc_key not in documents:
                    documents[doc_key] = {
                        "_id": str(uuid.uuid4()),  # Уникальный ID
                        "updated_ts": datetime.utcnow(),
                        "created_ts": created_ts,
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
            self.db.collection.update_one(
                {"created_ts": doc["created_ts"], "type_as": doc["type_as"]},
                {"$setOnInsert": doc},  # Вставляем только если не существует
                upsert=True
            )
            log.info(f'document with key {doc_key} saved')




        # 2. Обновляем статус исходного документа
    def update_status(self,source_collection,document_id,status='processed'):

        self.db[source_collection].update_one(
            {"_id": document_id},
            {
                "$set": {
                    "status": status,
                    "updated_ts": datetime.utcnow()
                }
            }
        )

    def get_new_doc(self, source_collection, type:str, log): #target_collection, external_processor, next_processor):
        """Периодическая обработка документов со статусом 'new'"""
        try:
            # Находим все документы со статусом "new"
            new_documents = self.db[source_collection].find(
                {"$and": [{"status": "new"}, {"type_as": type}]}
            ).sort("created_ts", 1)  # Сортируем по дате создания

            docs = {}
            for document in new_documents:
                docs[document["_id"]] = document.get("content", {}).get("json")
                self.update_status(source_collection, document["_id"])
                log.info(f'collection status is processed')
            return docs

        except Exception as e:
            log.info(f'finished_docs for {datetime.now()} with e: {e}')
            pass


    def create_matches(self, data_dict: Dict, status: str):
        """
        Преобразует словарь с турнирами и создает документы матчей
        Args:
            data_dict: {parent_id: {tournament_name: [urls]}}
            status: статус для всех создаваемых матчей
            collection: коллекция MongoDB для вставки
        """
        matches_to_insert = []
        try:
            for parent_id, tournaments in data_dict.items():
                for tournament_name, urls in tournaments.items():
                    for url in urls:
                        match_doc = {
                            "parent_id": parent_id,
                            "tournament_name": tournament_name,
                            "match_id": "",
                            "match_url": url,
                            "html": "",
                            "created_at": datetime.utcnow(),
                            "type_as": status
                        }
                        matches_to_insert.append(match_doc)

            if matches_to_insert:
                self.db.matches.insert_many(matches_to_insert, ordered=False)

        except Exception as e:
            print(f"Ошибка в процессе обработки: {e}")
            return 0

    def get_matches_url_by_ids_dict(self) -> Dict[str, str]:
        """
        Возвращает словарь {_id: match_url} из коллекции matches
        """
        result_dict = {}

        cursor = self.db.matches.find(
            {"html": ""},
            {"_id": 1, "match_url": 1}
        )


        for doc in cursor:
            result_dict[str(doc["_id"])] = doc["match_url"]

        return result_dict

    def update_matches_html(self, html_data_dict: Dict[str, str]):
        """
        Обновляет поле match_html для документов в коллекции matches
        по совпадению _id с ключами словаря

        Args:
            html_data_dict: {_id: html_content}
        """
        bulk_operations = []

        for doc_id, html_content in html_data_dict.items():
            # Создаем операцию обновления для каждого совпадения
            bulk_operations.append(
                UpdateOne(
                    {"_id": ObjectId(doc_id)},  # ищем по _id
                    {"$set": {"html": html_content}},  # обновляем поле
                    upsert=False  # только обновление, не вставка
                )
            )

        # Выполняем bulk операцию
        if bulk_operations:
            self.db.matches.bulk_write(bulk_operations, ordered=False)
            log.info(f'батч с html_content записан')

    def create_target_document(self, source_document_id, processed_data, original_data, target_collection):
        """Создание нового документа в целевой коллекции"""
        try:
            new_document = {
                "_id": str(uuid.uuid4()),
                "source_document_ref": source_document_id,  # Внешний ключ
                "created_ts": datetime.utcnow(),
                "updated_ts": datetime.utcnow(),
                "processed_data": processed_data,
                "original_data": original_data,
                "processing_status": "completed"
            }

            result = self.db[target_collection].insert_one(new_document)
            return result.inserted_id

        except Exception as e:
            print(f"Ошибка создания целевого документа: {e}")
