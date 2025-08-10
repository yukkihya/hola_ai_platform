import os
import sqlite3
from flask import Flask, redirect, url_for
from flask_login import LoginManager, UserMixin

DB_NAME = "database.db"
SECRET_KEY  = "dev_secret"
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user'
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS master_apps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        slug TEXT UNIQUE NOT NULL,
        description TEXT,
        icon TEXT,
        template_file TEXT NOT NULL,
        backend_module TEXT NOT NULL,
        backend_function TEXT NOT NULL
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_app_assignments (
        user_id INTEGER NOT NULL,
        app_id INTEGER NOT NULL,
        PRIMARY KEY (user_id, app_id),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (app_id) REFERENCES master_apps(id) ON DELETE CASCADE
    )""")

    conn.commit()
    conn.close()

def create_app():
    app = Flask(__name__)
    app.secret_key = SECRET_KEY #os.environ.get("SECRET_KEY", "dev_secret")
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))  # or return a homepage
    # Init DB
    init_db()
    from auth.routes import auth
    from main.routes import main
    from admin.routes import admin_bp
    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(admin_bp)
    
    # Flask Login
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    

    class User(UserMixin):
        def __init__(self, id, username, password, role):
            self.id = id
            self.username = username
            self.password = password
            self.role = role
    
    @login_manager.user_loader
    def load_user(user_id):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT id, username, password, role FROM users WHERE id=?", (user_id,))
        row = cur.fetchone()
        conn.close()
        if row:
            return User(id=row[0], username=row[1], password=row[2], role=row[3])
        return None

    

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)