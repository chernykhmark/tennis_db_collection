from tqdm import tqdm
import sqlite3

# Подключение к базе данных
conn = sqlite3.connect('./tennis_data.db')
cursor = conn.cursor()

# Извлекаем все строки из таблицы match_data
cursor.execute("SELECT game_id, sex, round FROM match_data")
rows = cursor.fetchall()

# Проходим по каждой строке, обновляем значения с помощью .strip()
for row in tqdm(rows):
    game_id = row[0]
    sex = row[1].strip()
    round = row[2].strip()

    # Обновляем таблицу с новыми значениями
    cursor.execute("""
        UPDATE match_data
        SET sex = ?, round = ?
        WHERE game_id = ?
    """, (sex, round, game_id))

# Сохраняем изменения
conn.commit()

# Закрываем соединение
conn.close()
