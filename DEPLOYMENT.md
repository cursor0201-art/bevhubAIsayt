# BevHub AI Deployment

## Architecture
Frontend:
Cloudflare Pages

Backend:
Koyeb

Database:
PostgreSQL

## Frontend deployment

- **GitHub repository:** (Your connected GitHub repo)
- **Build command:** `npm run build`
- **Output directory:** `out`
- **Required environment variables:**
  - `NEXT_PUBLIC_API_URL` (Set this to your Koyeb backend URL, e.g., `https://api-bevhub-yourapp.koyeb.app`)

## Backend deployment

- **Koyeb service:** Web Service (GitHub)
- **Build/install command:** `pip install -r requirements.txt` (Koyeb detects Python automatically)
- **Start command:** `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120` (Or Koyeb will read the `Procfile`)
- **Required environment variables:**
  - `DATABASE_URL` (PostgreSQL connection string)
  - `DJANGO_SECRET_KEY` (Generate a secure random string)
  - `DJANGO_DEBUG` (`False`)
  - `DJANGO_ALLOWED_HOSTS` (Your Koyeb URL, e.g., `api-bevhub-yourapp.koyeb.app`)
  - `DJANGO_CORS_ALLOWED_ORIGINS` (Your Cloudflare Pages URL)
  - `DJANGO_CSRF_TRUSTED_ORIGINS` (Your Cloudflare Pages URL)
  - `OPENAI_API_KEY` (and other API keys as needed)
- **PORT:** `8000` (Koyeb usually provides the `PORT` env var automatically, gunicorn binds to it via `$PORT`)
- **Health endpoint:** `GET /health/`

## Database

- **DATABASE_URL:** `postgresql://USER:PASSWORD@HOST:PORT/DBNAME`
- **migrations:** After deployment, run `python manage.py migrate` via Koyeb's console (or SSH).

## CORS / CSRF

Какие production domains необходимо добавить в Koyeb:
- `DJANGO_CORS_ALLOWED_ORIGINS` = `https://your-cloudflare-pages.pages.dev,https://your-custom-domain.com`
- `DJANGO_CSRF_TRUSTED_ORIGINS` = `https://your-cloudflare-pages.pages.dev,https://your-custom-domain.com`

## Deployment order

1. Push repository to GitHub
2. Deploy backend to Koyeb
3. Get backend production URL from Koyeb
4. Configure backend CORS/CSRF variables in Koyeb
5. Configure `NEXT_PUBLIC_API_URL` in Cloudflare Pages
6. Deploy frontend
7. Test frontend (Check browser console for API errors)
8. Test API (`/health/`)
9. Test authentication
10. Test all critical flows

## Troubleshooting

- **CORS:** Ошибка `CORS policy` в консоли браузера означает, что URL фронтенда не добавлен в `DJANGO_CORS_ALLOWED_ORIGINS` на бэкенде.
- **404 API:** Убедитесь, что `NEXT_PUBLIC_API_URL` на фронтенде указывает на правильный URL Koyeb (без `/api` на конце, просто базовый URL).
- **502/503 Koyeb:** Означает, что приложение упало при старте. Проверьте логи Koyeb. Частая причина — неправильный `DATABASE_URL` или отсутствие `PORT`.
- **blank/white screen:** Откройте консоль браузера (F12). Скорее всего, ошибка в JS, неверный формат ответа от API.
- **SPA routing:** Если при обновлении страницы на Cloudflare Pages выдает 404, проверьте настройки routing или убедитесь, что `output: 'export'` и `trailingSlash: true` работают корректно.
- **database connection:** Ошибка `OperationalError`. Проверьте логи Koyeb. PostgreSQL может отклонять соединения без SSL. В `settings.py` добавлено `'sslmode': 'require'`.
- **migrations:** Если API возвращает 500 `relation does not exist`, значит миграции не применены. Выполните `python manage.py migrate` в консоли Koyeb.
- **environment variables:** После добавления/изменения переменных в Koyeb или Cloudflare Pages всегда нужен **Redeploy**.
