from flask import Flask, request, jsonify, send_from_directory, session, redirect
from flask_cors import CORS
import os, sqlite3, datetime
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "db", "app.db")

app = Flask(__name__, static_folder="static", static_url_path="/")
# Secret key for session cookies; in production load from env
app.secret_key = os.environ.get("APP_SECRET", "change-this-secret")

# Serve everything same-origin (no cross-site CORS needed), but allow if you must
CORS(app, supports_credentials=True)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with app.app_context():
        conn = get_db()
        cur = conn.cursor()
        cur.executescript(open(os.path.join(BASE_DIR, "db", "schema.sql"), "r", encoding="utf-8").read())
        conn.commit()
        conn.close()

def login_required(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify({"error": "unauthorized"}), 401
        return fn(*args, **kwargs)
    return wrapper

@app.get("/api/health")
def health():
    return {"ok": True, "time": datetime.datetime.utcnow().isoformat() + "Z"}

# ---------- Auth ----------
@app.post("/api/auth/login")
def login():
    data = request.json or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    if not email or not password:
        return jsonify({"error": "missing credentials"}), 400
    conn = get_db()
    user = conn.execute("SELECT id, email, password_hash FROM users WHERE email=?", (email,)).fetchone()
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "invalid credentials"}), 401
    session["user_id"] = int(user["id"])
    session["email"] = user["email"]
    return {"ok": True, "email": user["email"]}

@app.post("/api/auth/logout")
def logout():
    session.clear()
    return {"ok": True}

@app.get("/api/auth/me")
def me():
    if not session.get("user_id"):
        return jsonify({"authenticated": False})
    return {"authenticated": True, "email": session.get("email")}

# ---------- Helpers ----------
def row_to_dict(row):
    return {k: row[k] for k in row.keys()}

# ---------- Services ----------
@app.get("/api/services")
def list_services():
    conn = get_db()
    rows = conn.execute("SELECT * FROM services ORDER BY updated_at DESC").fetchall()
    return jsonify([row_to_dict(r) for r in rows])

@app.post("/api/services")
@login_required
def create_service():
    data = request.json or {}
    title = data.get("title")
    category = data.get("category")
    bullets = data.get("bullets") or []
    if isinstance(bullets, str):
        bullets = [b.strip() for b in bullets.split(",") if b.strip()]
    conn = get_db()
    conn.execute("INSERT INTO services (title, category, bullets) VALUES (?,?,?)",
                 (title, category, json.dumps(bullets)))
    conn.commit()
    return {"ok": True}

@app.patch("/api/services/<int:sid>")
@login_required
def update_service(sid):
    data = request.json or {}
    title = data.get("title")
    category = data.get("category")
    bullets = data.get("bullets")
    if isinstance(bullets, str):
        bullets = [b.strip() for b in bullets.split(",") if b.strip()]
    conn = get_db()
    row = conn.execute("SELECT id FROM services WHERE id=?", (sid,)).fetchone()
    if not row:
        return {"error":"not found"}, 404
    conn.execute("""UPDATE services SET 
                      title=COALESCE(?, title), 
                      category=COALESCE(?, category), 
                      bullets=COALESCE(?, bullets),
                      updated_at=CURRENT_TIMESTAMP
                    WHERE id=?""",
                 (title, category, json.dumps(bullets) if bullets is not None else None, sid))
    conn.commit()
    return {"ok": True}

@app.delete("/api/services/<int:sid>")
@login_required
def delete_service(sid):
    conn = get_db()
    conn.execute("DELETE FROM services WHERE id=?", (sid,))
    conn.commit()
    return {"ok": True}

# ---------- Network ----------
@app.get("/api/network")
def list_network():
    conn = get_db()
    rows = conn.execute("SELECT * FROM network ORDER BY updated_at DESC").fetchall()
    return jsonify([row_to_dict(r) for r in rows])

@app.post("/api/network")
@login_required
def create_network():
    data = request.json or {}
    name = data.get("name")
    city = data.get("city")
    meta = data.get("meta")
    conn = get_db()
    conn.execute("INSERT INTO network (name, city, meta) VALUES (?,?,?)", (name, city, meta))
    conn.commit()
    return {"ok": True}

@app.patch("/api/network/<int:nid>")
@login_required
def update_network(nid):
    data = request.json or {}
    name = data.get("name")
    city = data.get("city")
    meta = data.get("meta")
    conn = get_db()
    row = conn.execute("SELECT id FROM network WHERE id=?", (nid,)).fetchone()
    if not row:
        return {"error":"not found"}, 404
    conn.execute("""UPDATE network SET 
                      name=COALESCE(?, name),
                      city=COALESCE(?, city),
                      meta=COALESCE(?, meta),
                      updated_at=CURRENT_TIMESTAMP
                    WHERE id=?""",
                 (name, city, meta, nid))
    conn.commit()
    return {"ok": True}

@app.delete("/api/network/<int:nid>")
@login_required
def delete_network(nid):
    conn = get_db()
    conn.execute("DELETE FROM network WHERE id=?", (nid,))
    conn.commit()
    return {"ok": True}

# ---------- Testimonials ----------
@app.get("/api/testimonials")
def list_testimonials():
    conn = get_db()
    rows = conn.execute("SELECT * FROM testimonials ORDER BY updated_at DESC").fetchall()
    return jsonify([row_to_dict(r) for r in rows])

@app.post("/api/testimonials")
@login_required
def create_testimonial():
    data = request.json or {}
    quote = data.get("quote")
    author = data.get("author")
    conn = get_db()
    conn.execute("INSERT INTO testimonials (quote, author) VALUES (?,?)", (quote, author))
    conn.commit()
    return {"ok": True}

@app.patch("/api/testimonials/<int:tid>")
@login_required
def update_testimonial(tid):
    data = request.json or {}
    quote = data.get("quote")
    author = data.get("author")
    conn = get_db()
    row = conn.execute("SELECT id FROM testimonials WHERE id=?", (tid,)).fetchone()
    if not row:
        return {"error":"not found"}, 404
    conn.execute("""UPDATE testimonials SET 
                      quote=COALESCE(?, quote),
                      author=COALESCE(?, author),
                      updated_at=CURRENT_TIMESTAMP
                    WHERE id=?""",
                 (quote, author, tid))
    conn.commit()
    return {"ok": True}

@app.delete("/api/testimonials/<int:tid>")
@login_required
def delete_testimonial(tid):
    conn = get_db()
    conn.execute("DELETE FROM testimonials WHERE id=?", (tid,))
    conn.commit()
    return {"ok": True}

# ---------- Leads ----------
@app.post("/api/leads")
def create_lead():
    data = request.json or {}
    name = (data.get("name") or "").strip()
    phone = (data.get("phone") or "").strip()
    need = (data.get("need") or "").strip()
    message = (data.get("message") or "").strip()
    conn = get_db()
    conn.execute("INSERT INTO leads (name, phone, need, message) VALUES (?,?,?,?)",
                 (name, phone, need, message))
    conn.commit()
    return {"ok": True}

@app.get("/api/leads")
@login_required
def list_leads():
    conn = get_db()
    rows = conn.execute("SELECT * FROM leads ORDER BY created_at DESC").fetchall()
    return jsonify([row_to_dict(r) for r in rows])

# ---------- Static routes ----------
@app.route('/')
def home():
    return send_from_directory(app.static_folder, 'index.html')

# Fallback to serve static files (admin and public)
@app.route('/<path:path>')
def static_proxy(path):
    full_path = os.path.join(app.static_folder, path)
    if os.path.isfile(full_path):
        return send_from_directory(app.static_folder, path)
    # Otherwise 404 JSON
    return jsonify({"error":"not found"}), 404

if __name__ == "__main__":
    # Create DB if missing
    if not os.path.exists(DB_PATH):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        with open(os.path.join(BASE_DIR, "db", "schema.sql"), "r", encoding="utf-8") as f:
            schema = f.read()
        conn = sqlite3.connect(DB_PATH)
        conn.executescript(schema)
        conn.commit()
        conn.close()
    app.run(host="0.0.0.0", port=8000, debug=True)
