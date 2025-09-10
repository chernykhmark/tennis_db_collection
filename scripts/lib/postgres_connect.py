
from dotenv import load_dotenv
load_dotenv()
import os
import psycopg2
from psycopg2.extras import RealDictCursor


class PostgresDB:
    def __init__(self):
        # Данные для подключения из .env
        self.PG_HOST = os.getenv('PG_HOST')
        self.PG_PORT = os.getenv('PG_PORT')
        self.PG_DATABASE = os.getenv('PG_DATABASE')
        self.PG_USER = os.getenv('PG_USER')
        self.PG_PASSWORD = os.getenv('PG_PASSWORD')

        self.connection = None
        self.connect()

    def connect(self):
        """Установка соединения с PostgreSQL"""
        try:
            self.connection = psycopg2.connect(
                host=self.PG_HOST,
                port=self.PG_PORT,
                database=self.PG_DATABASE,
                user=self.PG_USER,
                password=self.PG_PASSWORD,
                cursor_factory=RealDictCursor  # Для получения результатов в виде словаря
            )
            print("Успешное подключение к PostgreSQL")
        except Exception as e:
            print(f"Ошибка подключения к PostgreSQL: {e}")
            raise

    def execute_query(self, query, params=None):
        """Выполнение SQL запроса"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                if cursor.description:  # Если есть результаты
                    return cursor.fetchall()
                self.connection.commit()
                return None
        except Exception as e:
            self.connection.rollback()
            print(f"Ошибка выполнения запроса: {e}")
            raise

    def close(self):
        """Закрытие соединения"""
        if self.connection:
            self.connection.close()
            print("Соединение с PostgreSQL закрыто")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Пример использования
if __name__ == "__main__":
    db = PostgresDB()
    try:
        # Пример запроса
        result = db.execute_query("SELECT version();")
        print("Версия PostgreSQL:", result[0]['version'])
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        db.close()