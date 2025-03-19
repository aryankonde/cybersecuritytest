from flask import Flask, request, render_template
import sqlite3
import os

app = Flask(__name__)
app.config['DEBUG'] = False  # Secure: Debug mode disabled

# Use environment variable for database path (Secure)
DATABASE = os.getenv('DATABASE_PATH', 'secure_database.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Enable name-based access to columns
    return conn

# Initialize the database
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return render_template('index.html', users=users)

@app.route('/add', methods=['POST'])
def add_user():
    username = request.form['username']
    email = request.form['email']
    conn = get_db_connection()
    cursor = conn.cursor()
    # Use parameterized queries to prevent SQL Injection
    cursor.execute("INSERT INTO users (username, email) VALUES (?, ?)", (username, email))
    conn.commit()
    conn.close()
    return 'User added successfully!'

@app.route('/search')
def search():
    query = request.args.get('q', '')
    conn = get_db_connection()
    cursor = conn.cursor()
    # Use parameterized queries to prevent SQL Injection
    cursor.execute("SELECT * FROM users WHERE username LIKE ?", (f'%{query}%',))
    users = cursor.fetchall()
    conn.close()
    return render_template('search.html', users=users)

if __name__ == '__main__':
    init_db()
    app.run()
