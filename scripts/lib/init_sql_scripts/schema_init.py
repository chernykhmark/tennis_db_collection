import os
import logging
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()
DDL_PATH = os.getenv('DDL_PATH')

from scripts.lib.postgres_connect import PostgresDB

log = logging.getLogger(__name__)

class SchemaDdl:

    # ИНИЦИАЛИЗАЦИЯ

    def __init__(self, pg: PostgresDB, log) -> None:
        self._db = pg
        self.log = log

    # ФУНКЦИЯ ПО СОЗДАНИЮ СХЕМЫ В КОТОРУЮ МЫ ПЕРЕДАЕМ ПУТЬ К ДИРЕКТОРИИ

    def init_schema(self, path_to_scripts: str) -> None:
        # МЫ БЕРЕМ ВСЕ ФАЙЛЫ В ДИРЕКТОРИИ и СОРТИРУЕМ В АЛФАВИТНОМ ПОРЯДКЕ (ТАК КАК МЫ В ТАКОМ ПОРЯДКЕ ПИСАЛИ ИХ ДЛЯ СОЗДАНИЯ СХЕМЫ)

        files = os.listdir(path_to_scripts)
        file_paths = [Path(path_to_scripts, f) for f in files]
        file_paths.sort(key=lambda x: x.name)

        self.log.info(f"Found {len(file_paths)} files to apply changes.")

        # ЧИТАЕМ СКРИПТ ИЗ КАЖДОГО ФАЙЛА

        i = 1
        for fp in file_paths:
            self.log.info(f"Iteration {i}. Applying file {fp.name}")
            script = fp.read_text()

            # СОЕДИНЯЕМСЯ С НУЖНОЙ БАЗОЙ, ПОДКЛЮЧАЕМСЯ К БАЗЕ И ВЫПОЛНЯЕМ ТАМ ВСЕ СКРИПТЫ

            with self._db.connection as conn:
                with conn.cursor() as cur:
                    cur.execute(script)

            self.log.info(f"Iteration {i}. File {fp.name} executed successfully.")
            i += 1



if __name__=="__main__":
    try:
        pg = PostgresDB()
        sql_loader = SchemaDdl(pg, log)
        sql_loader.init_schema(DDL_PATH)
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        pg.close()