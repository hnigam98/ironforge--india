# IRONFORGE — GitHub + Render Deployment

This repository is prepared for deployment from GitHub to a Docker-based web service.

## 1. GitHub

Create a new GitHub repository, then upload the contents of this folder (the files inside it, not the parent folder).

Do not upload `.env` or production secrets.

## 2. PostgreSQL

Create a PostgreSQL database on your production provider. Keep the database credentials private.

Set these environment variables on the web service:

- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_HOST`
- `POSTGRES_PORT=5432`

## 3. Render Web Service

Create a new Render Web Service from the GitHub repository.

The repository already contains:
- `Dockerfile`
- `entrypoint.sh`
- `render.yaml`
- `requirements.txt`
- Django project
- migrations
- frontend

The container startup automatically runs:

```text
python manage.py migrate --noinput
python manage.py collectstatic --noinput
gunicorn ironforge.wsgi:application
```

## 4. Required environment values

Set:

```text
DEBUG=False
SECRET_KEY=<generated/private value>
ALLOWED_HOSTS=<your-render-domain>
CORS_ALLOWED_ORIGINS=https://<your-render-domain>
POSTGRES_DB=<private>
POSTGRES_USER=<private>
POSTGRES_PASSWORD=<private>
POSTGRES_HOST=<private>
POSTGRES_PORT=5432
```

If you later put the frontend on a separate domain, add that exact HTTPS origin to `CORS_ALLOWED_ORIGINS`.

## 5. First admin

After deployment, open a Render shell and run:

```bash
python manage.py createsuperuser
```

Then use:

```text
https://YOUR-DOMAIN/admin/
https://YOUR-DOMAIN/admin-portal/
```

## 6. Manual UPI

The project contains the owner's configured UPI information and QR asset. Verify it in the admin/site settings before accepting real payments.

## 7. Coach WhatsApp workflow

For each coach, store the WhatsApp number with country code and digits only, for example:

```text
919876543210
```

The system can generate WhatsApp click-to-chat links for:
- paid coach assignment/notification
- client chat
- audio/video contact
- session booking

## 8. Production checks

Before accepting real customers:

- test registration/login
- test admin login
- add a coach and WhatsApp number
- add/verify plans
- submit a manual UPI payment
- approve it in admin
- verify WhatsApp link/message
- book a coaching session
- verify coach receives the client/session information
- test mobile and desktop
- configure backups

Never put database passwords, Django secret keys, UPI PINs, OTPs, or private payment credentials in GitHub or frontend JavaScript.
