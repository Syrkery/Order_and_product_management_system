Веб-приложение для малого бизнеса, позволяющее управлять товарами, клиентами, заказами и складскими остатками.

## 🔧 Технологии

- Python 3.10+
- Flask (или Django)
- SQLAlchemy (ORM)
- SQLite
- Bootstrap 5
- Flask-Login / Django Auth
- REST API (Flask RESTful / Django REST Framework)
- PythonAnywhere / Render (деплой)

## 🚀 Возможности

- Регистрация и авторизация пользователей
- Управление товарами с изображениями и остатками
- Создание и редактирование заказов
- Автоматическое уменьшение остатков со склада при оформлении заказа
- Работа с клиентами и история их заказов
- Категории товаров
- API для получения данных в формате JSON
- Отчёты и аналитика
- Панель администратора (только для авторизованных)

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
source venv/bin/activate  # или venv\\Scripts\\activate на Windows
pip install -r requirements.txt
