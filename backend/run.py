import os, re, json, datetime as dt, requests
from flask import Flask, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
E = os.environ.get
FRONT = E("FRONTEND_URL", "http://localhost:5173").rstrip("/")
db_url = E("DATABASE_URL")
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app = Flask(__name__)
app.config.update(SECRET_KEY=E("SECRET_KEY", "dev-change-me"), JWT_SECRET_KEY=E("SECRET_KEY", "dev-change-me"),
                  SQLALCHEMY_DATABASE_URI=db_url or "sqlite:///finance.db")
CORS(app, origins=list(dict.fromkeys([FRONT, f"{FRONT}/", "http://localhost:5173", "http://localhost:5173/"])))
db = SQLAlchemy(app); JWTManager(app)
google = OAuth(app).register("google", client_id=E("GOOGLE_CLIENT_ID"), client_secret=E("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration", client_kwargs={"scope": "openid email profile"})

class Base(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=dt.datetime.utcnow)
    def d(self):
        out = {}
        for c in self.__table__.columns:
            if c.name == "password_hash": continue
            v = getattr(self, c.name); out[c.name] = v.isoformat() if hasattr(v, "isoformat") else v
        return out
UID = lambda: db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), index=True, nullable=False)
class User(Base):
    google_id = db.Column(db.String(64), unique=True); name = db.Column(db.String(120))
    email = db.Column(db.String(200), unique=True, nullable=False); profile_picture = db.Column(db.String(500))
    password_hash = db.Column(db.String(300)); updated_at = db.Column(db.DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)
class Income(Base):
    user_id = UID(); source = db.Column(db.String(60), nullable=False); amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, default=dt.date.today); description = db.Column(db.String(300))
class Category(Base):
    user_id = UID(); name = db.Column(db.String(60), nullable=False); color = db.Column(db.String(9), default="#64748b")
class Expense(Base):
    user_id = UID(); category_id = db.Column(db.Integer, db.ForeignKey("category.id"), index=True)
    amount = db.Column(db.Float, nullable=False); date = db.Column(db.Date, default=dt.date.today)
    description = db.Column(db.String(300)); payment_method = db.Column(db.String(30), default="Cash")
class Budget(Base):
    user_id = UID(); category_id = db.Column(db.Integer, db.ForeignKey("category.id"))
    month = db.Column(db.Integer); year = db.Column(db.Integer); limit = db.Column(db.Float, nullable=False)
class SavingsGoal(Base):
    user_id = UID(); name = db.Column(db.String(100), nullable=False); target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0); target_date = db.Column(db.Date)
    updated_at = db.Column(db.DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)

CATS = [("Food","#f97316"),("Rent","#6366f1"),("Transport","#0ea5e9"),("Education","#8b5cf6"),("Healthcare","#ef4444"),
        ("Entertainment","#ec4899"),("Shopping","#f59e0b"),("Utilities","#14b8a6"),("Bills","#64748b"),("Other","#94a3b8")]
me = lambda: db.session.get(User, int(get_jwt_identity()))
tok = lambda u: create_access_token(identity=str(u.id), expires_delta=dt.timedelta(days=7))
def new_user(u):
    db.session.add(u); db.session.flush()
    db.session.add_all(Category(user_id=u.id, name=n, color=c) for n, c in CATS); db.session.commit(); return u

@app.post("/api/auth/register")
def register():
    j = request.json or {}; em = (j.get("email") or "").strip().lower(); pw = j.get("password") or ""
    if not re.match(r"[^@\s]+@[^@\s]+\.[^@\s]+$", em) or len(pw) < 8: return jsonify(error="Valid email and a password of 8+ characters required"), 400
    if User.query.filter_by(email=em).first(): return jsonify(error="Email already registered"), 409
    u = new_user(User(name=j.get("name") or em.split("@")[0], email=em, password_hash=generate_password_hash(pw)))
    return jsonify(token=tok(u), user=u.d()), 201
@app.post("/api/auth/login")
def login():
    j = request.json or {}; u = User.query.filter_by(email=(j.get("email") or "").strip().lower()).first()
    if not u or not u.password_hash or not check_password_hash(u.password_hash, j.get("password") or ""): return jsonify(error="Invalid email or password"), 401
    return jsonify(token=tok(u), user=u.d())
@app.get("/api/auth/me")
@jwt_required()
def whoami(): return jsonify(me().d())
@app.post("/api/auth/logout")
@jwt_required()
def logout(): return jsonify(ok=True)  # JWT is discarded client-side
@app.get("/api/auth/google")
def g_start(): return google.authorize_redirect(E("GOOGLE_REDIRECT_URI"))
@app.get("/api/auth/google/callback")
def g_cb():
    try: info = google.authorize_access_token().get("userinfo")
    except Exception: return redirect(FRONT + "/?error=google")
    if not info or not info.get("email_verified"): return redirect(FRONT + "/?error=google")
    u = User.query.filter_by(google_id=info["sub"]).first() or User.query.filter_by(email=info["email"].lower()).first()
    if not u: u = new_user(User(google_id=info["sub"], email=info["email"].lower(), name=info.get("name"), profile_picture=info.get("picture")))
    else: u.google_id, u.profile_picture = info["sub"], info.get("picture"); db.session.commit()
    return redirect(f"{FRONT}/?token={tok(u)}")

# ---- generic per-user CRUD ----
R = {"income": (Income, ["source","amount","date","description"]), "expenses": (Expense, ["category_id","amount","date","description","payment_method"]),
     "budgets": (Budget, ["category_id","month","year","limit"]), "savings-goals": (SavingsGoal, ["name","target_amount","current_amount","target_date"]),
     "categories": (Category, ["name","color"])}
def val(k, v):
    if k in ("amount","limit","target_amount","current_amount"):
        v = float(v)
        if v < 0: raise ValueError(k)
    if k in ("date","target_date"): v = dt.date.fromisoformat(v) if v else None
    return v
def fill(o, j, fields):
    try:
        for k in fields:
            if k in j: setattr(o, k, val(k, j[k]))
    except (ValueError, TypeError): return False
    return True
@app.get("/api/<res>")
@jwt_required()
def lst(res):
    if res not in R: return jsonify(error="Not found"), 404
    M = R[res][0]; q = M.query.filter_by(user_id=me().id)
    if hasattr(M, "date"): q = q.order_by(M.date.desc())
    return jsonify([o.d() for o in q.all()])
@app.post("/api/<res>")
@jwt_required()
def add(res):
    if res not in R: return jsonify(error="Not found"), 404
    M, f = R[res]; o = M(user_id=me().id)
    if not fill(o, request.json or {}, f): return jsonify(error="Invalid input"), 400
    db.session.add(o)
    try: db.session.commit()
    except Exception: db.session.rollback(); return jsonify(error="Missing or invalid fields"), 400
    return jsonify(o.d()), 201
@app.route("/api/<res>/<int:i>", methods=["PUT", "DELETE"])
@jwt_required()
def one(res, i):
    if res not in R: return jsonify(error="Not found"), 404
    M, f = R[res]; o = M.query.filter_by(id=i, user_id=me().id).first()
    if not o: return jsonify(error="Not found"), 404
    if request.method == "DELETE": db.session.delete(o); db.session.commit(); return "", 204
    if not fill(o, request.json or {}, f): return jsonify(error="Invalid input"), 400
    db.session.commit(); return jsonify(o.d())

# ---- analytics ----
def summary(uid):
    t = dt.date.today(); cn = {c.id: c.name for c in Category.query.filter_by(user_id=uid)}
    inc = sum(i.amount for i in Income.query.filter_by(user_id=uid))
    ex = Expense.query.filter_by(user_id=uid).all(); tot = sum(e.amount for e in ex); by = {}
    for e in ex:
        if e.date.year == t.year and e.date.month == t.month: by[cn.get(e.category_id, "Other")] = by.get(cn.get(e.category_id, "Other"), 0) + e.amount
    bud = [{"category": cn.get(b.category_id, "Overall"), "limit": b.limit, "spent": by.get(cn.get(b.category_id), sum(by.values()) if b.category_id is None else 0)}
           for b in Budget.query.filter_by(user_id=uid, month=t.month, year=t.year)]
    goals = [g.d() for g in SavingsGoal.query.filter_by(user_id=uid)]
    return {"total_income": inc, "total_expenses": tot, "savings": inc - tot, "savings_rate_pct": round((inc - tot) / inc * 100, 1) if inc else 0,
            "this_month_by_category": by, "budgets": bud, "goals": goals}
@app.get("/api/dashboard/summary")
@jwt_required()
def dash(): return jsonify(summary(me().id))

# ---- bot ----
def cat_of(uid, n):
    return Category.query.filter(Category.user_id == uid, db.func.lower(Category.name) == n.lower()).first() or Category.query.filter_by(user_id=uid, name="Other").first()
def command(u, t):
    m = re.match(r"income\s+([\d.]+)\s*(\w+)?", t, re.I)
    if m: db.session.add(Income(user_id=u.id, amount=float(m[1]), source=(m[2] or "Other").title())); db.session.commit(); return f"Added income ₹{float(m[1]):,.0f}."
    m = re.match(r"expense\s+([\d.]+)\s+(\w+)\s*(.*)", t, re.I)
    if m:
        c = cat_of(u.id, m[2]); db.session.add(Expense(user_id=u.id, amount=float(m[1]), category_id=c.id, description=m[3])); db.session.commit()
        return f"Logged ₹{float(m[1]):,.0f} under {c.name}."
    m = re.match(r"budget\s+(\w+)\s+([\d.]+)", t, re.I)
    if m:
        c, n = cat_of(u.id, m[1]), dt.date.today(); db.session.add(Budget(user_id=u.id, category_id=c.id, month=n.month, year=n.year, limit=float(m[2]))); db.session.commit()
        return f"Budget for {c.name} set to ₹{float(m[2]):,.0f} this month."
    m = re.match(r"goal\s+(.+?)\s+([\d.]+)$", t, re.I)
    if m: db.session.add(SavingsGoal(user_id=u.id, name=m[1], target_amount=float(m[2]))); db.session.commit(); return f"Goal '{m[1]}' created (₹{float(m[2]):,.0f})."
    m = re.match(r"save\s+(.+?)\s+([\d.]+)$", t, re.I)
    if m:
        g = SavingsGoal.query.filter(SavingsGoal.user_id == u.id, db.func.lower(SavingsGoal.name) == m[1].lower()).first()
        if not g: return "I couldn't find that goal."
        g.current_amount += float(m[2]); db.session.commit(); return f"Added ₹{float(m[2]):,.0f} to {g.name}: ₹{g.current_amount:,.0f}/₹{g.target_amount:,.0f}."
    if t.lower() in ("summary", "status"):
        s = summary(u.id); return f"Income ₹{s['total_income']:,.0f} · Expenses ₹{s['total_expenses']:,.0f} · Savings ₹{s['savings']:,.0f} ({s['savings_rate_pct']}%)."
def ask_ai(u, t):
    k = E("GEMINI_API_KEY")
    if not k: return "Gemini isn't configured yet. Set GEMINI_API_KEY in .env."
    p = f"You are a friendly personal finance advisor (currency INR). User data: {json.dumps(summary(u.id), default=str)}\nQuestion: {t}\nBe concise and specific. End with: 'Informational only, not financial advice.'"
    try:
        r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{E('GEMINI_MODEL','gemini-2.0-flash')}:generateContent",
                          headers={"x-goog-api-key": k}, json={"contents": [{"parts": [{"text": p}]}]}, timeout=30); r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception: return "The AI service is unavailable right now. Please try again shortly."
@app.post("/api/bot/message")
@jwt_required()
def bot():
    u, t = me(), ((request.json or {}).get("text") or "").strip()
    if not t: return jsonify(error="Empty message"), 400
    return jsonify(reply=command(u, t) or ask_ai(u, t))

@app.get("/")
@app.get("/health")
def health():
    return jsonify(status="healthy", message="Finance Advisor Bot API is running")

@app.errorhandler(Exception)
def oops(e):
    code = getattr(e, "code", 500); return jsonify(error=e.description if code < 500 and hasattr(e, "description") else "Server error"), code

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    port = int(E("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=E("FLASK_DEBUG") == "1")
