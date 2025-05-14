from flask import Flask, render_template, g, request, redirect, url_for, session, flash
import sqlite3
import os
from datetime import datetime
from math import ceil
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
DATABASE = 'database.sqlite3'
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
PER_PAGE = 10


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


@app.template_filter('strptime')
def strptime_filter(s, fmt):
    return datetime.strptime(s, fmt)


def login_required(view):
    from functools import wraps
    @wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            flash('Требуется авторизация.', 'warning')
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view


@app.route('/')
def index():
    db = get_db()
    query = """
        SELECT Products.id, Products.name, Products.price, Products.stock, Products.image, Categories.name AS category
        FROM Products
        LEFT JOIN Categories ON Products.category_id = Categories.id
        WHERE 1=1
    """
    params = []

    search = request.args.get('search', '').strip()
    if search:
        query += ' AND Products.name LIKE ?'
        params.append(f'%{search}%')

    filter_stock = request.args.get('filter_stock')
    if filter_stock == 'low':
        query += ' AND Products.stock < 5'

    category_id = request.args.get('category_id')
    category_name = None
    if category_id:
        query += ' AND Products.category_id = ?'
        params.append(category_id)
        cat = db.execute("""SELECT name FROM Categories WHERE id = ?""", (category_id,)).fetchone()
        if cat:
            category_name = cat['name']

    total_query = """SELECT COUNT(*) FROM (""" + query + """)"""
    total = db.execute(total_query, params).fetchone()[0]

    page = int(request.args.get('page', 1))
    pages = ceil(total / PER_PAGE)
    offset = (page - 1) * PER_PAGE

    query += ' ORDER BY Products.name ASC LIMIT ? OFFSET ?'
    params.extend([PER_PAGE, offset])

    products = db.execute(query, params).fetchall()

    return render_template(
        'index.html',
        products=products,
        search=search,
        filter_stock=filter_stock,
        category_name=category_name,
        page=page,
        pages=pages,
        total=total
    )


@app.route('/categories')
def list_categories():
    db = get_db()
    categories = db.execute("""SELECT id, name FROM Categories ORDER BY name""").fetchall()
    return render_template('categories.html', categories=categories)


@app.route('/product/<int:product_id>')
def view_product(product_id):
    db = get_db()
    product = db.execute("""
        SELECT Products.*, Categories.name AS category
        FROM Products
        LEFT JOIN Categories ON Products.category_id = Categories.id
        WHERE Products.id = ?
    """, (product_id,)).fetchone()
    if product is None:
        flash('Товар не найден.', 'warning')
        return redirect(url_for('index'))
    return render_template('view_product.html', product=product)


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_product():
    db = get_db()
    categories = db.execute("""SELECT id, name FROM Categories ORDER BY name""").fetchall()

    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        stock = request.form['stock']
        category_id = request.form['category'] or None
        image_file = request.files.get('image')
        image_filename = ''

        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
            image_filename = filename

        db = get_db()
        created_at = datetime.now().isoformat()

        db.execute(
            """INSERT INTO Products (name, price, stock, image, category_id, created_at) VALUES (?, ?, ?, ?, ?, ?)""",
            (name, price, stock, image_filename, category_id, created_at))
        db.commit()
        flash('Товар добавлен.', 'success')
        return redirect(url_for('index'))
    return render_template('add_product.html', categories=categories)


@app.route('/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    db = get_db()
    product = db.execute("""SELECT * FROM Products WHERE id = ?""", (product_id,)).fetchone()
    categories = db.execute("""SELECT id, name FROM Categories ORDER BY name""").fetchall()

    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        stock = request.form['stock']
        category_id = request.form['category'] or None
        image_file = request.files.get('image')
        image_filename = product['image']

        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
            image_filename = filename

        updated_at = datetime.now().isoformat()

        db.execute("""
                    UPDATE Products
                    SET name = ?, price = ?, stock = ?, image = ?, category_id = ?, updated_at = ?
                    WHERE id = ?
                """, (name, price, stock, image_filename, category_id, updated_at, product_id))
        db.commit()
        flash('Изменения сохранены.', 'success')
        return redirect(url_for('index'))

    return render_template('edit_product.html', product=product, categories=categories)


@app.route('/delete/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    db = get_db()
    product = db.execute("""SELECT image FROM Products WHERE id = ?""", (product_id,)).fetchone()
    if product and product['image']:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], product['image'])
        if os.path.exists(image_path):
            os.remove(image_path)
    db.execute("""DELETE FROM Products WHERE id = ?""", (product_id,))
    db.commit()
    flash('Товар удалён.', 'info')
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        user = db.execute("""SELECT * FROM Users WHERE email = ?""", (email,)).fetchone()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            flash('Вы вошли в систему.', 'success')
            return redirect(url_for('index'))
        flash('Неверный email или пароль.', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, port=8080, host='127.0.0.1')
