from tqdm import tqdm
import sqlite3

from database import Database
# Подключение к базе данных

from update_results import request_and_parse

db = Database()


raws = db.get_current_rows(sql_query="""
        SELECT link
        FROM combine_data
        WHERE sex = '-' AND round = '-'
""")

raws_list = [raw[0] for raw in raws]
#print(raws_list)

for link in raws_list:
    soup = request_and_parse(link)

    #Получаем ПОЛ и РАУНД
    soup_header = soup.find('div', {'data-testid': "organism-match-header"})
    # Проверяем, найден ли элемент
    if soup_header:
        # Ищем вложенный div по классу и извлекаем текст, если найден
        try:
            response_text_div = soup_header.find('div', class_="caps-s7-rs uppercase text-br-2-70")
            sex_round = response_text_div.get_text()
        except:
            response_text_div = soup_header.find('div', class_="caption-2 md:caption:3 lg:caption-1 text-neutral-05")
            sex_round = response_text_div.get_text()

        sex = sex_round.split('|')[0].strip()
        rounds = sex_round.split('|')[1].strip()
        print(f'{sex} and {rounds}')
        db.update_data_by_sql_query(
            """
                UPDATE combine_data
                SET sex = ?, round = ?
                WHERE link = ?
            """,
            (sex, rounds, link)
        )
    else:
        sex = ''
        rounds = ''
        print('no text!')

db.close()

#
# # Извлекаем все строки из таблицы match_data
# cursor.execute("SELECT game_id, sex, round FROM match_data")
# rows = cursor.fetchall()
#
# # Проходим по каждой строке, обновляем значения с помощью .strip()
# for row in tqdm(rows):
#     game_id = row[0]
#     sex = row[1].strip()
#     round = row[2].strip()
#
#     # Обновляем таблицу с новыми значениями
#     cursor.execute("""
#         UPDATE match_data
#         SET sex = ?, round = ?
#         WHERE game_id = ?
#     """, (sex, round, game_id))
#
# # Сохраняем изменения
# conn.commit()
#
# # Закрываем соединение
# conn.close()
