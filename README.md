Веб-приложение для малого бизнеса, позволяющее управлять товарами, клиентами, заказами и складскими остатками.

## 🔧 Технологии

- Python 3.10+
- Flask
- SQLAlchemy
- SQLite
- Bootstrap 5
- Flask-Login
- PythonAnywhere

## 🚀 Возможности

- Авторизация пользователей
- Управление товарами с изображениями и остатками
- Создание и редактирование заказов
- Автоматическое уменьшение остатков со склада при оформлении заказа
- Работа с клиентами и история их заказов
- Категории товаров
- Отчёты и аналитика

## 📂 Структура базы данных

- `Users`: id, username, email, password_hash
- `Products`: id, name, description, price, image_path, stock, category_id
- `Categories`: id, name
- `Clients`: id, name, phone, email
- `Orders`: id, client_id, date_created, status
- `OrderItems`: id, order_id, product_id, quantity

## 📦 Установка

```bash
git clone https://github.com/yourusername/order-management-app.git
cd order-management-app
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
