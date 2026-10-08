# IRONFORGE INDIA — Deployment Ready Package

## Verified in this build
- Django/Python source syntax checked successfully.
- Inline JavaScript in index, admin portal, and coach portal checked successfully with Node syntax validation.
- Migration numbering is sequential: 0001, 0002, 0003, 0004.
- Coach WhatsApp number is stored in the database.
- Paid order stores the selected coach.
- Admin payment approval returns a WhatsApp click-to-chat URL for the selected coach.
- Client coach actions use WhatsApp click-to-chat.
- Session booking requires a verified paid coaching plan with the selected coach.
- Docker entrypoint automatically runs database migrations and collectstatic before Gunicorn starts.

## Required external production steps
These cannot be completed inside this offline build environment because they require your hosting/database accounts and production secrets:
1. Create the production PostgreSQL database.
2. Set SECRET_KEY, database credentials, ALLOWED_HOSTS and CORS_ALLOWED_ORIGINS.
3. Deploy this package to your chosen cloud host.
4. Create the Django superuser.
5. Open the admin portal and add your coaches, including their WhatsApp numbers.
6. Verify the manual UPI settings and QR.
7. Test payment approval and WhatsApp notification on an Android phone.

Do not put database passwords, Django SECRET_KEY, UPI PIN, OTP, or private payment credentials in frontend code.
