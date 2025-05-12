import sqlite3
from werkzeug.security import generate_password_hash

email = 'admin@example.com'
password = '12345'  # задай любой

conn = sqlite3.connect('database.sqlite3')
cursor = conn.cursor()

hashed = generate_password_hash(password)

cursor.execute('INSERT INTO Users (email, password) VALUES (?, ?)', (email, hashed))
conn.commit()
conn.close()

print('Пользователь добавлен.')
