import sqlite3
from werkzeug.security import generate_password_hash

username = 'admin'
email = 'admin@ya.ru'
password = 'admin'

conn = sqlite3.connect('database.sqlite3')
cursor = conn.cursor()

hashed = generate_password_hash(password)

cursor.execute("""INSERT INTO Users (username, email, password) VALUES (?, ?, ?)""", (username ,email, hashed))
conn.commit()
conn.close()

print('Пользователь добавлен.')
