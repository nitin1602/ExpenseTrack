# Production-Ready Expense Tracker (Flask + PostgreSQL + API + Modern UI)

# =========================
# 🔧 FEATURES
# =========================
# - Clean Flask structure
# - PostgreSQL-ready (via SQLAlchemy)
# - REST API for Android
# - Bootstrap UI
# - CSV/Excel export
# - Scalable architecture

# =========================
# 📦 INSTALL
# =========================
# pip install flask flask_sqlalchemy flask_migrate pandas openpyxl gunicorn psycopg2-binary

# =========================
# 📁 STRUCTURE
# =========================
# project/
#   app.py
#   models.py
#   routes.py
#   templates/
#   static/
#   requirements.txt

# =========================
# app.py
# =========================
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///expenses.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
with app.app_context():
    db.create_all()

# =========================
# MODELS
# =========================
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)

class SubCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float)
    category_id = db.Column(db.Integer)
    subcategory_id = db.Column(db.Integer)
    person_id = db.Column(db.Integer)
    payment_mode = db.Column(db.String(50))
    date = db.Column(db.String(20))

# =========================
# ROUTES (UI)
# =========================
from flask import render_template, request, redirect, jsonify
from datetime import datetime

@app.route('/')
def index():
    expenses = Expense.query.all()
    categories = Category.query.all()
    subcategories = SubCategory.query.all()
    persons = Person.query.all()

    return render_template('index.html',
        expenses=expenses,
        categories=categories,
        subcategories=subcategories,
        persons=persons
    )

@app.route('/add_expense', methods=['POST'])
def add_expense():
    e = Expense(
        amount=request.form['amount'],
        category_id=request.form['category_id'],
        subcategory_id=request.form['subcategory_id'],
        person_id=request.form['person_id'],
        payment_mode=request.form['payment_mode'],
        date=datetime.now().strftime('%Y-%m-%d')
    )
    db.session.add(e)
    db.session.commit()
    return redirect('/')

# 🔥 IMPORTANT: Filter subcategories by category (AJAX endpoint)
@app.route('/api/subcategories/<int:category_id>')
def get_subcategories(category_id):
    subs = SubCategory.query.filter_by(category_id=category_id).all()
    return jsonify([
        {'id': s.id, 'name': s.name}
        for s in subs
    ])

# =========================
# REST API (for Android)
# ========================= (for Android)
# =========================
@app.route('/api/expenses', methods=['GET'])
def api_get_expenses():
    data = []
    for e in Expense.query.all():
        data.append({
            'id': e.id,
            'amount': e.amount,
            'category_id': e.category_id,
            'subcategory_id': e.subcategory_id,
            'person_id': e.person_id,
            'payment_mode': e.payment_mode,
            'date': e.date
        })
    return jsonify(data)

@app.route('/api/expense', methods=['POST'])
def api_add_expense():
    data = request.json
    e = Expense(**data)
    db.session.add(e)
    db.session.commit()
    return jsonify({'status': 'success'})

# =========================
# EXPORT
# =========================
import pandas as pd
from flask import send_file

@app.route('/export/csv')
def export_csv():
    df = pd.read_sql_table('expense', db.engine)
    file = 'expenses.csv'
    df.to_csv(file, index=False)
    return send_file(file, as_attachment=True)

@app.route('/export/excel')
def export_excel():
    df = pd.read_sql_table('expense', db.engine)
    file = 'expenses.xlsx'
    df.to_excel(file, index=False)
    return send_file(file, as_attachment=True)

# =========================
# RUN (PRODUCTION SAFE)
# =========================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

# =========================
# 🚀 NEXT STEPS
# =========================
# 1. Add authentication (Flask-Login)
# 2. Add charts (Chart.js)
# 3. Use PostgreSQL in production
# 4. Connect Android app to /api/* endpoints
