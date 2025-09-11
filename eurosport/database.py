from dotenv import load_dotenv
load_dotenv()
import os
import pandas as pd
import sqlite3
from datetime import datetime,timedelta
from update_results import get_results
from telegram import Bot
import asyncio
import time as t



class Database:
    def __init__(self, db_name='./tennis_data.db'):
        # Создание или подключение к базе данных
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        # Создание таблицы, если она не существует
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS combine_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            tour TEXT,
            sex TEXT,
            round TEXT,
            game_id TEXT,
            adv_player_name TEXT,
            compare_score INTEGER,
            player_one TEXT,
            player_one_rank INTEGER,
            h2h_player_one_wins INTEGER,
            prev_match_player_one_wins INTEGER,
            prev_match_player_one_sevens_count INTEGER,
            player_two TEXT,
            player_two_rank INTEGER,
            h2h_player_two_wins INTEGER,
            prev_match_player_two_wins INTEGER,
            prev_match_player_two_sevens_count INTEGER,
            link TEXT,
            time TEXT,
            result_winner TEXT DEFAULT ''
        )''')
        # self.cursor.execute('''CREATE TABLE IF NOT EXISTS srv_wf_settings (
        #                         id INTEGER PRIMARY KEY AUTOINCREMENT,
        #                         workflow_key TEXT NOT NULL UNIQUE,
        #                         workflow_settings TEXT NOT NULL
        # )''')
        self.connection.commit()

    # def check_workflow_key_from_service_table(self, workflow_key):
    #     self.cursor.execute(
    #         '''
    #         created_at
    #         '''
    #
    #     )
    #
    # def save_workflow_key_to_service_table(self):



    def check_game_id_exists(self, game_id):
        # Проверка, существует ли game_id в базе данных
        self.cursor.execute("SELECT 1 FROM combine_data WHERE game_id = ?", (game_id,))
        return self.cursor.fetchone() is not None

    def add_data(self, datarow):
        # Добавление новой строки в базу данных
        self.cursor.execute('''INSERT INTO combine_data (
            date, tour, sex, round, game_id, adv_player_name, compare_score,
            player_one, player_one_rank, h2h_player_one_wins,
            prev_match_player_one_wins, prev_match_player_one_sevens_count,
            player_two, player_two_rank, h2h_player_two_wins,
            prev_match_player_two_wins, prev_match_player_two_sevens_count,
            link, time
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
            datarow['date'], datarow['tour'], datarow['sex'],datarow['round'], datarow['game_id'], datarow['adv_player_name'], datarow['compare_score'],
            datarow['player_one'], datarow['player_one_rank'], datarow['h2h_player_one_wins'],
            datarow['prev_match_player_one_wins'], datarow['prev_match_player_one_sevens_count'],
            datarow['player_two'], datarow['player_two_rank'], datarow['h2h_player_two_wins'],
            datarow['prev_match_player_two_wins'], datarow['prev_match_player_two_sevens_count'],
            datarow['link'], datarow['time']
        ))
        self.connection.commit()
        print(f"Данные успешно добавлены для game_id '{datarow['game_id']}'.")

       # Отправка сообщения после добавления данных
        self.send_message(datarow)

    def send_message(self, datarow):
        import asyncio
        from telegram import Bot

        async def send_matches(bot: Bot, datarow):
            percent = ''
            date, time, tour, sex, round, player_one, player_two, adv_player_name, compare_score = (
                datarow['date'], datarow['time'], datarow['tour'], datarow['sex'], datarow['round'],
                datarow['player_one'], datarow['player_two'],
                datarow['adv_player_name'], datarow['compare_score']
            )
            if compare_score == 0:
                percent = 'Шансы равны'
            elif compare_score == 1:
                percent = '25%'
            elif compare_score == 2:
                percent = '50%'
            elif compare_score == 3:
                percent = '75%'
            elif compare_score == 4:
                percent = '100%'

            if player_two == 'BYE' or player_one == 'BYE':
                percent = 'Прямой выход'

            message = (
                f"Дата: {date}\n"
                f"Время: {time}\n"
                f"Турнир: {tour}\n"
                f"{sex} - {round}\n\n"
                f"{player_one} - {player_two}\n\n"
                f"Победитель: {adv_player_name}\n"
                f"Преимущество: {percent}"
            )
            await bot.send_message(chat_id='1030144895', text=message)
            await bot.send_message(chat_id='494421588', text=message)

        async def main():
            bot = Bot(token='7216731297:AAE-boZvsnfoiw-lwO9ntgSJz-qJYHRQ6lU')
            await send_matches(bot, datarow)

        asyncio.run(main())

    def update_winner(self, game_id, winner):
        # Обновление поля result_winner для указанного game_id
        self.cursor.execute("UPDATE combine_data SET result_winner = ? WHERE game_id = ?", (winner, game_id))
        self.connection.commit()

    def get_all_rows(self):
        self.cursor.execute("SELECT * FROM combine_data")
        return self.cursor.fetchall()

    def get_current_rows(self, sql_query="SELECT * FROM combine_data"):
        self.cursor.execute(sql_query)
        return self.cursor.fetchall()

    def update_winne_from_yesterday(self):
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

        # Получаем все строки с датой вчерашнего дня, включая compare_score
        self.cursor.execute("""
            SELECT game_id, link, adv_player_name, player_one, player_two, result_winner, compare_score
            FROM combine_data
            WHERE date = ? AND (result_winner IS NULL OR result_winner = '') """, (yesterday,))
        rows = self.cursor.fetchall()

        if len(rows) != 0:
            # Инициализация словаря только для значений от 1 до 4
            results_by_compare_score = {i: {'total_matches': 0, 'correct_predictions': 0} for i in range(1, 5)}

            # Обрабатываем строки и обновляем result_winner
            for row in rows:
                t.sleep(3)
                game_id, link, adv_player_name, player_one, player_two, result_winner, compare_score = row

                # Исключаем строки с 'BYE' и 'Не определен'
                if 'BYE' in (player_one, player_two):
                    winner = player_one if player_two == 'BYE' else player_two
                    self.update_winner(game_id, winner)
                    print(f"Автоматически обновлено result_winner для game_id '{game_id}' с 'BYE' - {winner}")
                    continue

                if adv_player_name == 'Не определен':
                    winner = get_results(link)
                    self.update_winner(game_id, winner)
                    print(f"Обновлено result_winner для game_id '{game_id}' с 'Не определен' - {winner}")
                    continue

                # Выполняем HTTP-запрос к link
                winner = get_results(link)

                # Обновляем result_winner в базе данных
                self.update_winner(game_id, winner)
                print(f"Обновлено result_winner для game_id '{game_id}' - {winner}")

                # Рассчитываем значения только для случаев с compare_score от 1 до 4
                if compare_score in results_by_compare_score:
                    results_by_compare_score[compare_score]['total_matches'] += 1
                    if winner and winner == adv_player_name:
                        results_by_compare_score[compare_score]['correct_predictions'] += 1

            # Маппинг значений compare_score на более удобные строки
            compare_score_labels = {
                1: "25%",
                2: "50%",
                3: "75%",
                4: "100%"
            }

            # Генерируем сообщение по каждому значению compare_score
            messages = []
            for compare_score, data in results_by_compare_score.items():
                total_matches = data['total_matches']
                correct_predictions = data['correct_predictions']

                if total_matches > 0:
                    accuracy_percentage = round((correct_predictions / total_matches) * 100)
                    compare_score_label = compare_score_labels.get(compare_score)
                    messages.append(f"{compare_score_label} - событий: {total_matches} точность: {accuracy_percentage}%")
                else:
                    compare_score_label = compare_score_labels.get(compare_score)
                    messages.append(f"Для {compare_score_label}: матчей нет")

            # Собираем полное сообщение
            final_message = f"Итоги {yesterday}\n" + "\n".join(messages)
            asyncio.run(self.send_results(final_message))

        else:
            print('Нет строк для обработки')

    async def send_results(self, message):
        # Инициализация бота и отправка сообщения
        bot = Bot(token=os.getenv('ATP_BOT_TOKEN'))
        try:
            await bot.send_message(chat_id=os.getenv('TG_USER_ADMIN'), text=message)
            await bot.send_message(chat_id=os.getenv('TG_USER'), text=message)
            print("Сообщение отправлено в Telegram")
        except Exception as e:
            print(f"Ошибка при отправке сообщения в Telegram: {e}")

    def update_link_by_game_id(self, game_id, new_link):
        # Обновление значения поля link для указанного game_id
        self.cursor.execute("UPDATE combine_data SET link = ? WHERE game_id = ?", (new_link, game_id))
        self.connection.commit()
        print(f"Обновлено значение link для game_id '{game_id}' на '{new_link}'.")


    def update_data_by_sql_query(self, sql_query,params):
        try:
            self.cursor.execute(sql_query, params or ())
            self.connection.commit()
            print("Query executed successfully")
        except Exception as e:
            print(f"Error executing query: {e}")
            self.connection.rollback()  # Откатываем изменения при ошибке

    def drop_result_winner(self):
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        today = datetime.now().strftime('%Y-%m-%d')
        print(yesterday)
        self.cursor.execute("UPDATE combine_data SET result_winner = ? WHERE date = ?", ('',yesterday))
        self.connection.commit()
        print(f"Сброшены победители")

    def delete_last_row(self):
        # Найти id последней строки
        self.cursor.execute("SELECT id FROM combine_data ORDER BY id DESC LIMIT 1")
        last_row_id = self.cursor.fetchone()

        if last_row_id:
            # Удалить строку с найденным id
            self.cursor.execute("DELETE FROM match_data WHERE id = ?", (last_row_id[0],))
            self.connection.commit()
            print(f"Последняя строка с id '{last_row_id[0]}' была удалена.")
        else:
            print("Нет строк для удаления.")


    def update_all_null_winners(self):
        today = pd.Timestamp.now().strftime('%Y-%m-%d')
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        self.cursor.execute("""
            SELECT game_id, link
            FROM combine_data
            WHERE (date != ? OR date != ?) AND (result_winner IS NULL OR result_winner = '') """,(today,tomorrow,))
        rows = self.cursor.fetchall()

        if len(rows) != 0:

            for row in rows:
                t.sleep(1)
                game_id, link = row
                # Выполняем HTTP-запрос к link
                winner = get_results(link)
                if winner:
                # Обновляем result_winner в базе данных
                    self.update_winner(game_id, winner)
                    print(f"Обновлено result_winner для game_id: {game_id} - {winner}")

        else:
            print('Нет строк для обработки')

    def close(self):
        self.connection.close()
