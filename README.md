# 💰 Personal Finance Advisor Bot

An intelligent, full-stack personal finance tracker and conversational advisor. Features natural language financial assistance powered by **Google Gemini AI**, real-time budget management, expense tracking, savings goals, and secure JWT authentication with optional Google OAuth.

---

## ✨ Features

- **🤖 Hybrid Conversational AI Assistant**:
  - Direct quick commands for rapid tracking without clunky forms.
  - Gemini 2.0 Flash integration that answers personal finance questions based on your live financial summary.
- **📊 Real-time Dashboard & Analytics**:
  - Monthly income vs. expense tracking and net savings rate.
  - Category-wise spending breakdowns with dynamic visual progress.
- **🎯 Savings Goals**:
  - Create custom savings targets (e.g., "Emergency Fund", "New Laptop").
  - Track deposits and target completion progress.
- **🏷️ Smart Category Budgeting**:
  - Pre-seeded default categories (Food, Rent, Transport, Healthcare, Shopping, Utilities, etc.).
  - Set monthly category spending limits and monitor threshold consumption.
- **🔐 Secure Authentication**:
  - Standard Email & Password registration with Werkzeug salted password hashing.
  - Stateless JSON Web Token (JWT) session handling.
  - Google OAuth 2.0 single sign-on integration.
- **🇮🇳 Localized**:
  - Configured with Indian Rupee (₹ INR) numbering formatting.

---

## 🛠️ Tech Stack

| Component | Technology | Description |
|---|---|---|
| **Frontend** | React 18 + Vite | Fast, responsive Single Page Application (SPA) |
| **Styling** | Modern Vanilla CSS | Glassmorphism, dark mode, responsive layout |
| **Backend** | Python 3 + Flask | RESTful API backend |
| **Database** | SQLite / PostgreSQL | Managed with Flask-SQLAlchemy ORM |
| **Auth** | Flask-JWT-Extended + Authlib | JWT tokens & Google OpenID Connect |
| **AI Engine** | Google Gemini 2.0 Flash | Generative financial advisory via REST API |
| **Production WSGI** | Gunicorn | Production-ready HTTP server |

---

## 📁 Project Structure

```text
personal-finance-advisor-bot/
├── backend/
│   ├── requirements.txt      # Python dependencies (Flask, SQLAlchemy, Gunicorn, etc.)
│   └── run.py                # Main backend API, bot logic, models, and routes
├── frontend/
│   ├── index.html            # Vite HTML template
│   ├── package.json          # Node dependencies and scripts
│   ├── vite.config.js        # Vite configuration
│   └── src/
│       ├── App.jsx           # Main React component (chat UI, dashboard, login)
│       ├── index.css         # Styling system & dark theme
│       └── main.jsx          # React DOM entrypoint
├── .env.example              # Environment variables template
├── .gitignore                # Git exclusions (credentials, node_modules, DBs)
├── render.yaml               # 1-Click Render Blueprint configuration
└── README.md                 # Project documentation
```

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- **Python 3.10+**
- **Node.js 18+** & `npm`
- **Google Gemini API Key** (Free from [Google AI Studio](https://aistudio.google.com))

---

### 1. Backend Setup

```bash
# Navigate to the backend directory
cd backend

# Create and activate a Python virtual environment
# Windows:
python -m venv venv
venv\Scripts\activate

# macOS / Linux:
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Return to root and configure environment variables
cd ..
cp .env.example .env
```

Open `.env` in your editor and configure your secrets:
```env
DATABASE_URL=sqlite:///finance.db
SECRET_KEY=your-super-secret-key-change-this
GEMINI_API_KEY=your_gemini_api_key_here
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:5000
```

Start the Flask backend server:
```bash
cd backend
python run.py
```
> The API will start at `http://localhost:5000`.

---

### 2. Frontend Setup

In a separate terminal window:

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```
> The web application will be live at `http://localhost:5173`.

---

## 💬 Bot Commands & Usage

In the chat interface, you can type natural questions or use direct command shortcuts:

| Command | Syntax | Example | Description |
|---|---|---|---|
| **Add Income** | `income <amount> [source]` | `income 50000 salary` | Logs a new income entry |
| **Add Expense** | `expense <amount> <category> [note]` | `expense 250 food lunch` | Logs an expense under a category |
| **Set Budget** | `budget <category> <limit>` | `budget food 5000` | Sets monthly spending limit for a category |
| **Create Goal** | `goal <name> <target>` | `goal Laptop 60000` | Initializes a new savings target |
| **Deposit to Goal** | `save <name> <amount>` | `save Laptop 2000` | Adds money toward an existing savings goal |
| **Summary** | `summary` or `status` | `summary` | Displays income, expenses, and savings rate |
| **AI Advisor** | *Any natural question* | `Where can I cut expenses?` | Consults Gemini using your real-time financials |

---

## 🔑 Environment Variables Reference

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | No | `sqlite:///finance.db` | PostgreSQL or SQLite connection URI |
| `SECRET_KEY` | **Yes** | `dev-change-me` | Secret key used for JWT signature & sessions |
| `GEMINI_API_KEY` | **Yes** | — | Google Gemini API key for AI financial suggestions |
| `GEMINI_MODEL` | No | `gemini-2.0-flash` | Gemini model name |
| `FRONTEND_URL` | **Yes** | `http://localhost:5173` | Allowed CORS origin and OAuth redirect target |
| `BACKEND_URL` | No | `http://localhost:5000` | Base URL of the backend service |
| `GOOGLE_CLIENT_ID` | Optional | — | Google OAuth 2.0 Client ID |
| `GOOGLE_CLIENT_SECRET` | Optional | — | Google OAuth 2.0 Client Secret |
| `GOOGLE_REDIRECT_URI` | Optional | `http://localhost:5000/api/auth/google/callback` | OAuth redirect URI |

---

## 🌐 Deploying for Free to Render & Supabase

### 1. Database (Supabase PostgreSQL - Permanent Free Tier)
1. Create a free database at **[Supabase](https://supabase.com)**.
2. In **Project Settings** $\rightarrow$ **Database**, copy the **Session Pooler URI**:
   ```text
   postgresql://postgres.[REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres
   ```

### 2. Deploy to Render via Blueprint (1-Click)
1. Push this repository to your **GitHub** account.
2. Go to **[Render Dashboard](https://dashboard.render.com)** $\rightarrow$ Click **New +** $\rightarrow$ **Blueprint**.
3. Connect your GitHub repository. Render reads [`render.yaml`](file:///c:/Users/omghu/Downloads/personal-finance-advisor-bot/render.yaml) and provisions:
   - **Backend Web Service**: Python Flask running on Gunicorn.
   - **Frontend Static Site**: React Vite application.
4. Input your `DATABASE_URL` and `GEMINI_API_KEY` when prompted.
5. In your frontend static site settings, set:
   - `VITE_API_URL` = `https://<your-backend-service>.onrender.com`
6. In your backend web service environment settings, set:
   - `FRONTEND_URL` = `https://<your-frontend-site>.onrender.com`

---

## 🔒 Optional: Google OAuth Setup

1. Go to **[Google Cloud Console](https://console.cloud.google.com/)** $\rightarrow$ **APIs & Services** $\rightarrow$ **Credentials**.
2. Create an **OAuth 2.0 Client ID** (Web Application).
3. Add **Authorized JavaScript Origins**:
   - `http://localhost:5173` (Development)
   - `https://<your-frontend-site>.onrender.com` (Production)
4. Add **Authorized Redirect URIs**:
   - `http://localhost:5000/api/auth/google/callback` (Development)
   - `https://<your-backend-service>.onrender.com/api/auth/google/callback` (Production)
5. Add `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` to your environment variables.

---

## 📄 License

This project is licensed under the MIT License.
