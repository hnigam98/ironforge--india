# IRONFORGE INDIA — Production Backend V10

This package converts the V9 browser-storage prototype into a real Django/PostgreSQL backend foundation.

## What is included

- Django + Django REST Framework
- PostgreSQL database
- Secure password hashing through Django auth
- JWT access/refresh authentication
- Admin/staff authorization
- Athlete profiles
- Coach accounts and coach management (including coach WhatsApp numbers)
- Coach requests
- Workout programs
- Nutrition templates
- Plans/pricing
- Orders
- Razorpay order creation + webhook signature verification
- Site settings
- Django Admin dashboard
- Docker + PostgreSQL setup
- V9 frontend included as `frontend/index.html`

Supabase was not used here because IRONFORGE already has a Django/Python direction. The database/auth/payment responsibilities are kept in a conventional Django backend that can be deployed to a VPS/cloud platform.

## 1. Local setup

Install Python 3.12+ and PostgreSQL, or use Docker.

Copy `.env.example` to `.env` and change the values.

### Docker

```bash
docker compose up --build
```

Then create the first administrator:

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

Open:

- Website: http://localhost:8000/
- Admin: http://localhost:8000/admin/
- API: http://localhost:8000/api/

### Non-Docker

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env   # Windows
# cp .env.example .env   # macOS/Linux

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## 2. Production security

Before deployment:

1. Generate a strong random `SECRET_KEY`.
2. Set `DEBUG=False`.
3. Set real `ALLOWED_HOSTS`.
4. Set exact frontend origins in `CORS_ALLOWED_ORIGINS`.
5. Use HTTPS.
6. Put Razorpay secrets only in environment variables.
7. Do not put `RAZORPAY_KEY_SECRET` in frontend code.
8. Create only the required staff/admin users.
9. Use database backups.
10. Configure your production host/reverse proxy.

## 3. Razorpay

Create Razorpay keys and put them in `.env`:

```text
RAZORPAY_KEY_ID=...
RAZORPAY_KEY_SECRET=...
RAZORPAY_WEBHOOK_SECRET=...
```

The API endpoint:

`POST /api/orders/`

creates a Razorpay order for an active plan.

The webhook endpoint is:

`POST /api/payments/razorpay/webhook/`

Configure Razorpay to send payment events to that endpoint.

The webhook verifies `X-Razorpay-Signature` before changing the order status.

## 4. Admin capabilities

Django Admin provides the secure server-side control panel:

- Users
- Profiles
- Coaches
- Plans
- Programs
- Nutrition
- Coach requests
- Orders
- Site settings

The REST API also exposes protected admin endpoints under `/api/admin/*`.

## 5. Important frontend step

The V9 HTML is included as the visual frontend, but its old localStorage admin controls are still present.

For production, the next frontend integration is to replace localStorage operations with these APIs:

- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `POST /api/auth/refresh/`
- `GET /api/me/`
- `GET/PATCH /api/me/profile/`
- `GET /api/public/coaches/`
- `GET /api/public/plans/`
- `POST /api/coach-requests/`
- `POST /api/orders/`
- `GET /api/orders/`
- admin endpoints under `/api/admin/`

JWT access tokens should be held in secure application state and refreshed using the refresh-token flow. Never expose a Django secret key, database password, Razorpay secret, or service credential in browser JavaScript.

## 6. Architecture

Browser
  -> Django API
      -> PostgreSQL
      -> Django Auth/JWT
      -> Razorpay
      -> Coach/athlete data
      -> Admin control

This means the data is no longer tied to one browser. Multiple devices can access the same account and the admin can manage the same database from anywhere.


## V11 — Coach Portal + private reviews

**Admin:** only Django `is_staff=True` accounts can access `/admin/` or read `/api/private/coach-reviews/`.

**Coach:** separate normal account. Coaches use `/coach-portal.html`, can see/manage only their own sessions, and cannot access the admin portal or reviews.

**Athlete:** can see their own sessions. Once a coach marks a session completed, the athlete can submit one 1–5 star review and optional feedback. Reviews are stored privately and are visible only to admin/staff.

Create the real admin account with `python manage.py createsuperuser`. No shared admin password is included.

## Manual UPI payments (no Razorpay)

IRONFORGE now supports direct UPI payments without a payment gateway.

Flow:
1. Customer chooses a plan.
2. Customer logs in or creates an account.
3. Website shows the configured UPI ID and optional QR code.
4. Customer pays directly in a UPI app and submits the UTR/transaction ID.
5. The order is stored as `created` (pending verification).
6. Admin approves/rejects it from Django Admin or the protected API.
7. Approval marks the order `paid` and activates the plan on the customer's profile.

### Configure your personal UPI details

In Django Admin, open **Site settings** and create/update the `manual_payment` setting with JSON similar to:

```json
{
  "enabled": true,
  "upi_id": "yourname@upi",
  "account_name": "Your Name / IRONFORGE INDIA",
  "qr_image_url": "https://your-domain.com/static/your-upi-qr.png",
  "instructions": "Pay the exact amount and enter the UTR. Access is activated after admin verification."
}
```

Do not put bank passwords, UPI PINs, card numbers, or OTPs in the website.

### Admin approval

- Django Admin: **Orders** → select pending orders → **Approve selected UPI payments** or **Reject selected UPI payments**.
- Protected API endpoints are also available at `/api/admin/orders/<id>/approve/` and `/api/admin/orders/<id>/reject/`.
- Only staff/admin users can approve or reject payments.
- Coaches have no access to payment administration or Django Admin.


## Manual UPI configuration
The included payment configuration is pre-filled for the owner's UPI account:
- UPI ID: `nigamhimanshu80-2@oksbi`
- Account name: `Himanshu Nigam`
- QR image: `frontend/assets/himanshu_upi_qr.jpg`

Customers pay directly by UPI and submit the UTR/transaction ID. Only Django staff/admin users can approve or reject payments. Coaches do not receive admin access.

## V14 Admin Control Center
Open `https://YOUR-DOMAIN/admin-portal/` for the custom mobile-friendly admin panel.

The custom panel uses the real Django/JWT backend and requires an `is_staff` admin account. It is not the old browser-only demo login.

Admin can manage without coding:
- Coaches: add, edit, activate/hide, delete, set login/password, specialty, tags, bio and rate.
- Plans & pricing: add, edit, increase/decrease prices, change features, hide/show, delete.
- Users: enable/disable accounts.
- Workout programs: add/edit/delete.
- Nutrition templates: add/edit/delete.
- Manual UPI payments: inspect UTRs and approve/reject payments.
- Coaching sessions: monitor sessions.
- Private coach reviews: visible only to admin/staff.
- Website content: edit announcement, hero title/description, footer, Google Form URL, and homepage feature cards (add/edit/hide/delete).
- Platform settings: change UPI ID/account name/instructions and Coach Assistant limits.

### Important
Do not use the old demo `admin / ironforge123` credentials. The browser-only admin login has been removed. Create the real admin with:

`python manage.py createsuperuser`

Only Django staff/admin accounts can use `/admin-portal/` and `/admin/`. Coaches remain non-staff and cannot access either admin area.

## V15 usability updates
- Manual UPI checkout no longer requires customer login or account creation.
- Customers only enter Name, Email and UTR / Transaction ID after payment.
- Guest UPI submissions appear in the Admin > Payments section for verification.
- Admin can change their own username, email and password from Admin > Admin Account.
- Coaches and athletes cannot access the admin account endpoint.

## V17 — Coach WhatsApp workflow

- Admin can store a coach WhatsApp number with country code (for example `919876543210`).
- A client can select a live coach; the selected coach is attached to the manual UPI payment.
- After admin approval, the payment record includes a ready-to-send WhatsApp notification for the coach containing client name, email, plan, amount and UTR.
- The Admin Portal provides a **WhatsApp Coach** action for paid orders.
- Clients can open WhatsApp directly from Chat, Audio Call, Video Call, or Schedule Session actions.
- Schedule Session lets the client choose a date/time and opens WhatsApp with a pre-filled booking request.
- This uses WhatsApp click-to-chat and does not require a WhatsApp API account. Fully automatic outbound messages without a click require the official WhatsApp Business API and are not enabled by default.
