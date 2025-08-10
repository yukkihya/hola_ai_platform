from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
import sqlite3, os, importlib.util, sys
from app import DB_NAME

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
def restrict_to_admin():
    if not hasattr(current_user, 'role') or current_user.role != 'admin':
        flash("Access denied", "danger")
        return redirect(url_for('main.home'))

@admin_bp.route('/')
@login_required
def dashboard():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT id, username FROM users WHERE role='user'")
    users = cur.fetchall()
    cur.execute("SELECT id, name FROM master_apps")
    apps = cur.fetchall()
    conn.close()
    return render_template('admin/admin_dashboard.html', users=users, apps=apps)

@admin_bp.route('/create_app', methods=['GET', 'POST'])
@login_required
def create_app():
    if request.method == 'POST':
        name = request.form['name']
        slug = request.form['slug']
        description = request.form['description']
        icon = request.form['icon']
        template_file = request.form['template_file']
        backend_module = f"apps.{slug}"
        backend_function = request.form['backend_function']
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO master_apps 
            (name, slug, description, icon, template_file, backend_module, backend_function)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, slug, description, icon, template_file, backend_module, backend_function))
        conn.commit()
        conn.close()
        flash("App created successfully", "success")
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/admin_create_app.html')

@admin_bp.route('/assign_app', methods=['POST'])
@login_required
def assign_app():
    user_id = request.form['user_id']
    app_id = request.form['app_id']
    conn = sqlite3.connect(DB_NAME)
    conn.execute("INSERT OR IGNORE INTO user_app_assignments (user_id, app_id) VALUES (?, ?)",
                 (user_id, app_id))
    conn.commit()
    conn.close()
    flash("Assigned!", "success")
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/upload_app_code', methods=['GET','POST'])
@login_required
def upload_app_code():
    if request.method == 'POST':
        slug = request.form['slug']
        backend_function = request.form['backend_function']
        py_file = request.files['py_file']
        html_file = request.files['html_file']
        py_path = os.path.join(current_app.root_path, 'apps', f"{slug}.py")
        html_path = os.path.join(current_app.root_path, 'templates', 'apps', f"{slug}.html")
        if py_file:
            py_file.save(py_path)
        if html_file:
            html_file.save(html_path)
        backend_module = f"apps.{slug}"
        conn = sqlite3.connect(DB_NAME)
        conn.execute("""
            INSERT INTO master_apps (name, slug, description, icon, template_file, backend_module, backend_function)
            VALUES (?, ?, 'Uploaded hot-deploy', 'fas fa-robot', ?, ?, ?)
            ON CONFLICT(slug) DO UPDATE SET
              template_file=excluded.template_file,
              backend_module=excluded.backend_module,
              backend_function=excluded.backend_function
        """, (slug, f"{slug}.html", backend_module, backend_function))
        conn.commit()
        conn.close()
        # Live load
        spec = importlib.util.spec_from_file_location(backend_module, py_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        sys.modules[backend_module] = mod
        flash("Hot deployed!", "success")
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/admin_upload_app.html')
	