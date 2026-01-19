from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this in production

# Database config (update with your RDS details later)
def get_db_connection():
    connection = mysql.connector.connect(
        host='your-rds-endpoint.amazonaws.com',  # From RDS later
        user='admin',  # Your RDS username
        password='your_password',  # Your RDS password
        database='dropship_db'
    )
    return connection

# Home/Dashboard
@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Total Inventory Value (simple sum of stock * price)
    cursor.execute("SELECT SUM(stock * price) AS total_inventory FROM inventory")
    total_inventory = cursor.fetchone()['total_inventory'] or 0
    
    # Total Payments (revenue)
    cursor.execute("SELECT SUM(amount) AS total_payments FROM payments")
    total_payments = cursor.fetchone()['total_payments'] or 0
    
    # Total Expenses
    cursor.execute("SELECT SUM(amount) AS total_expenses FROM expenses")
    total_expenses = cursor.fetchone()['total_expenses'] or 0
    
    # Balance (Profit)
    balance = total_payments - total_expenses
    
    cursor.close()
    conn.close()
    
    return render_template('index.html', total_inventory=total_inventory, 
                           total_payments=total_payments, total_expenses=total_expenses, balance=balance)

# Inventory Routes
@app.route('/inventory')
def inventory():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM inventory")
    items = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('inventory.html', items=items)

@app.route('/add_inventory', methods=['POST'])
def add_inventory():
    product = request.form['product']
    stock = int(request.form['stock'])
    price = float(request.form['price'])
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO inventory (product, stock, price) VALUES (%s, %s, %s)", (product, stock, price))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Inventory added!')
    return redirect(url_for('inventory'))

# Similar routes for edit/delete (simplified; add as homework)

# Payments Routes
@app.route('/payments')
def payments():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM payments")
    payments_list = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('payments.html', payments=payments_list)

@app.route('/add_payment', methods=['POST'])
def add_payment():
    description = request.form['description']
    amount = float(request.form['amount'])
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO payments (description, amount) VALUES (%s, %s)", (description, amount))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Payment added!')
    return redirect(url_for('payments'))

# Expenses Routes (similar to payments)
@app.route('/expenses')
def expenses():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM expenses")
    expenses_list = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('expenses.html', expenses=expenses_list)

@app.route('/add_expense', methods=['POST'])
def add_expense():
    description = request.form['description']
    amount = float(request.form['amount'])
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses (description, amount) VALUES (%s, %s)", (description, amount))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Expense added!')
    return redirect(url_for('expenses'))

if __name__ == '__main__':
    app.run(debug=True)
