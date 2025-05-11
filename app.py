from flask import Flask, render_template, g, request, redirect, url_for
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
DATABASE = 'database.sqlite3'
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


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
    products = db.execute("""SELECT id, name, price, stock, image FROM Products""").fetchall()
    return render_template('index.html', products=products)


@app.route('/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        stock = request.form['stock']
        image_file = request.files.get('image')
        image_filename = ''

        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
            image_filename = filename

        db = get_db()
        db.execute("""INSERT INTO Products (name, price, stock, image) VALUES (?, ?, ?, ?)""", (name, price, stock, image_filename))
        db.commit()
        return redirect(url_for('index'))
    return render_template('add_product.html')


@app.route('/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    db = get_db()
    product = db.execute('SELECT image FROM Products WHERE id = ?', (product_id,)).fetchone()
    if product and product['image']:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], product['image'])
        if os.path.exists(image_path):
            os.remove(image_path)
    db.execute('DELETE FROM Products WHERE id = ?', (product_id,))
    db.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=8080, host='127.0.0.1')
