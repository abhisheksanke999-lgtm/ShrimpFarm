# AquaControl — FastAPI + PostgreSQL (Neon) + HTML/CSS/Bootstrap/JS

## New stack
- **Frontend:** HTML + CSS + Bootstrap 5 + JavaScript (same UI as before)
- **Backend:** FastAPI
- **Database:** PostgreSQL on [Neon](https://neon.tech)

Old PHP/XAMPP files are obsolete; the app now runs through FastAPI with the HTML frontend under `frontend/`.

## 1. Create a Neon database
1. Sign up at https://console.neon.tech
2. Create a project
3. Copy the connection string (URI), e.g.  
   `postgresql://user:pass@ep-xxx.region.aws.neon.tech/neondb?sslmode=require`

## 2. Configure backend
```bash
cd backend
copy .env.example .env
```
Edit `backend/.env` and paste your Neon `DATABASE_URL`.

## 3. Install & run
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open: **http://127.0.0.1:8000/**

Sample account (auto-created on first start):
- Email: `admin@shrimpfarm.com`
- Password: `admin123`

## Features kept the same
- Login / Register (email OTP verification) / Logout
- Per-user data isolation (`user_id`)
- Ponds, Daily logs, Feed, Expenses, Harvest, Reports, Settings
- Harvest marks pond as Harvested
- Same CSS theme and sidebar layout
- Mobile: hamburger menu opens the sidebar

## Email OTP (register)
Configure Gmail SMTP in `backend/.env` (same pattern as RentYaar):

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com
OTP_EXPIRY_SECONDS=300
```

If `SMTP_HOST` is empty, the OTP is printed in the server console for local testing.

Flow: **Register** → email OTP → **Verify** (`/pages/verify-otp.html`) → dashboard.
## API docs
- Swagger UI: http://127.0.0.1:8000/docs

## Project layout
```
Aquacontrol/
  backend/              FastAPI app
  frontend/
    index.html          Login page
    pages/*.html        App pages
    js/                 Shared frontend JS
    css/                Same styles as before
```
