import sqlite3 

# открываем файл с базой данных
con = sqlite3.connect('marvel.db')

# создаём таблицу 
with con:
    con.execute("""
        CREATE TABLE marvel (
            ID INTEGER PRIMARY KEY,
            name TEXT,
            superpower TEXT,
            status TEXT);""")

# Удаляем таблицу
#with con:
    #con.execute("DROP TABLE marvel")

# подготавливаем запрос
sql = 'INSERT INTO marvel (ID, name, superpower, status) values(?, ?, ?, ?)'

# указываем данные для запроса
data = [
    (1, 'Халк', 'Суперсила', 'За добро'),
    (2, 'Тор', 'Молот', 'За добро'),
]

# добавляем с помощью множественного запроса все данные сразу
with con:
    con.executemany(sql, data)

# Обновляем статус Халка
with con:
    con.execute("UPDATE marvel SET status = 'За зло' WHERE name = ?",('Халк',))

# Удаляем запись с Тором
with con:
    con.execute("DELETE FROM marvel WHERE name = ?",('Тор',))