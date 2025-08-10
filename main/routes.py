from flask import Blueprint, render_template, request, abort
from flask_login import login_required, current_user
import sqlite3, importlib
from app import DB_NAME

main = Blueprint('main', __name__)

@main.route('/home')
@login_required
def home():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        SELECT m.name, m.slug, m.description, m.icon
        FROM master_apps m
        JOIN user_app_assignments ua ON ua.app_id = m.id
        WHERE ua.user_id=?
    """, (current_user.id,))
    rows = cur.fetchall()
    conn.close()
    assigned_apps = [{"name": r[0], "slug": r[1], "description": r[2], "icon": r[3]} for r in rows]
    return render_template('home.html', assigned_apps=assigned_apps)

@main.route('/tool/<slug>', methods=['GET', 'POST'])
@login_required
def tool_runner(slug):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        SELECT m.id, m.name, m.slug, m.template_file, m.backend_module, m.backend_function
        FROM master_apps m
        JOIN user_app_assignments ua ON ua.app_id = m.id
        WHERE m.slug=? AND ua.user_id=?
    """, (slug, current_user.id))
    row = cur.fetchone()
    conn.close()
    if not row:
        abort(403)
    _, name, slug, template, backend_module, backend_function = row
    context = {"app_name": name}
    if request.method == 'POST':
        mod = importlib.import_module(backend_module)
        func = getattr(mod, backend_function)
        out = func(request)
        if( out is not None):
            context.update(out)
    return render_template(f"apps/{template}", context=context)
