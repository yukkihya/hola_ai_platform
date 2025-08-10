import sqlite3
from app import DB_NAME, init_db

init_db()

conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()

# Add users
users = [
    ("admin", "admin123", "admin"),
    ("sriram", "sriram", "user"),
    ("chitti", "chitti", "user")
]
try:
    cur.executemany("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", users)
except sqlite3.IntegrityError:
    pass

# Fetch user IDs for apps
cur.execute("SELECT id FROM users WHERE username='admin'")
admin_id = cur.fetchone()[0]

cur.execute("SELECT id FROM users WHERE username='sriram'")
sriram_id = cur.fetchone()[0]

# Add apps for users
apps = [
    (admin_id, "Admin Dashboard", "https://admin.example.com"),
    (sriram_id, "AI Tools", "https://analytics.example.com")
]
#cur.executemany("INSERT INTO apps (user_id, app_name, app_url) VALUES (?, ?, ?)", apps)



# Seed with built-in tools if they don't exist
cur.execute("SELECT COUNT(*) FROM master_apps WHERE slug='rag_chatbot'")
if cur.fetchone()[0] == 0:
    cur.execute("""
        INSERT INTO master_apps
        (name, slug, description, icon, template_file, backend_module, backend_function)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ("RAG Chatbot", "rag_chatbot",
            "A simple retrieval-augmented chatbot",
            "fas fa-comments", "rag_chatbot.html",
            "apps.rag_chatbot", "rag_chatbot_backend"))

cur.execute("SELECT COUNT(*) FROM master_apps WHERE slug='resume_agent'")
if cur.fetchone()[0] == 0:
    cur.execute("""
        INSERT INTO master_apps
        (name, slug, description, icon, template_file, backend_module, backend_function)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ("Resume Agent", "resume_agent",
            "AI-powered resume content generator",
            "fas fa-file-alt", "resume_agent.html",
            "apps.resume_agent", "resume_agent_backend"))
    
cur.execute("SELECT COUNT(*) FROM master_apps WHERE slug='customer_support_agent'")
if cur.fetchone()[0] == 0:
    cur.execute("""
        INSERT INTO master_apps
        (name, slug, description, icon, template_file, backend_module, backend_function)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ("Customer Support Agent", "customer_support_agent",
            "AI multi-agent customer support bot",
            "fas fa-headset", "customer_support_agent.html",
            "apps.customer_support_agent", "support_agent_backend"))
    
conn.commit()
conn.close()