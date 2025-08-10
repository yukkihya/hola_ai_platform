from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user
import sqlite3
from app import DB_NAME
print(">>> Inside Auth routes")
auth = Blueprint('auth', __name__)#, url_prefix='/auth')
main = Blueprint('main', __name__)
admin = Blueprint('admin_bp', __name__)
class UserObj:
    def __init__(self, id, username, password, role):
        self.id = id
        self.username = username
        self.password = password
        self.role = role
        self.active = True
    def is_authenticated(self):
        return True
    def is_active(self):
        return self.active  # must return True/False

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print( f"username {username}")
        print( f"password {password}")
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT id, username, password, role FROM users WHERE username=?", (username,))
        row = cur.fetchone()
        conn.close()
        print( f"row {row}")
        if row and password == row[2] : #check_password_hash(row[2], password):
            user = UserObj(id=row[0], username=row[1], password=row[2], role=row[3])
            login_user(user)
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('main.home'))
        else:
            flash("Invalid credentials", "danger")
    return render_template('login.html')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        #password = generate_password_hash(password)
        conn = sqlite3.connect(DB_NAME)
        try:
            conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, 'user')", (username, password))
            conn.commit()
            flash("Account created! Please login.")
            return redirect(url_for('auth.login'))
        except sqlite3.IntegrityError:
            flash("Username already exists", "danger")
        finally:
            conn.close()
    return render_template('signup.html')

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))