# Sanjeevani Seva — Fullstack (Flask + SQLite)

A complete setup with:
- Public website (animated), served from `static/`
- Admin dashboard (`/admin/login.html` → `/admin/dashboard.html`) with login + CRUD
- REST API (Flask) backed by SQLite
- Contact form saves leads into the database

## Quick start
1. Install Python 3.10+
2. Create a virtual env (optional) and install deps:
   ```bash
   pip install -r requirements.txt
   ```
3. (Optional) set a secret:
   ```bash
   set APP_SECRET=change-this-secret    # Windows
   export APP_SECRET=change-this-secret # macOS/Linux
   ```
4. Run the server:
   ```bash
   python app.py
   ```
5. Open: http://localhost:8000/

### Admin credentials
- Email: `admin@sanjeevani.seva`
- Password: `Password@123`

## API overview
- `GET /api/services` (public), `POST/PATCH/DELETE /api/services/*` (admin)
- `GET /api/network` (public), `POST/PATCH/DELETE /api/network/*` (admin)
- `GET /api/testimonials` (public), `POST/PATCH/DELETE /api/testimonials/*` (admin)
- `POST /api/leads` (public), `GET /api/leads` (admin)
- `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/me`

## Database
SQLite file at `db/app.db` (pre‑seeded). Schema in `db/schema.sql`.

## Deploying
- Small VPS or Render/railway with `gunicorn` and `nginx` works well.
- For HTTPS and domains, use a reverse proxy (Caddy or Nginx).
- Keep `APP_SECRET` safe, and rotate the admin password in DB (use a bcrypt hash in `users`).
