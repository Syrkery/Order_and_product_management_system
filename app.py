from flask import Flask, render_template, g
import sqlite3

app = Flask(__name__)
DATABASE = 'database.sqlite3'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    db = get_db()
    products = db.execute("""SELECT id, name, price, stock FROM products""").fetchall()
    return render_template('index.html', products=products)

if __name__ == '__main__':
    app.run(debug=True, port=8080, host='127.0.0.1')
