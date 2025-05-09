from flask import Flask, render_template, g, request, redirect, url_for
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

@app.route('/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        stock = request.form['stock']
        db = get_db()
        db.execute("""INSERT INTO products (name, price, stock) VALUES (?, ?, ?)""", (name, price, stock))
        db.commit()
        return redirect(url_for('index'))
    return render_template('add_product.html')

if __name__ == '__main__':
    app.run(debug=True, port=8080, host='127.0.0.1')
