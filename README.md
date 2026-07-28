# AquaControl — FastAPI + PostgreSQL (Neon) + HTML/CSS/Bootstrap/JS

## New stack
- **Frontend:** HTML + CSS + Bootstrap 5 + JavaScript (same UI as before)
- **Backend:** FastAPI
- **Database:** PostgreSQL on [Neon](https://neon.tech)

Old PHP/XAMPP files are still in the repo under `pages/*.php` and `api/*.php` but the app now runs through FastAPI.

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

Open: **http://127.0.0.1:8000/pages/login.html**

Sample account (auto-created on first start):
- Email: `admin@shrimpfarm.com`
- Password: `admin123`

## Features kept the same
- Login / Register / Logout
- Per-user data isolation (`user_id`)
- Ponds, Daily logs, Feed, Expenses, Harvest, Reports, Settings
- Harvest marks pond as Harvested
- Same CSS theme and sidebar layout
- Mobile: hamburger menu opens the sidebar

## API docs
- Swagger UI: http://127.0.0.1:8000/docs

## Project layout
```
Aquacontrol/
  backend/          FastAPI app
  pages/*.html      Frontend pages
  js/               Shared frontend JS
  css/              Same styles as before
```
