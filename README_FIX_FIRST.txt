IRONFORGE INDIA — Django structure repair

The repository's root-level Django files do not currently match the package paths
expected by manage.py and settings.py. This script creates the expected
ironforge/ project package, api/ application package, api/migrations/ package,
and frontend/ copies of the existing website/admin/coach HTML files.

SAFE USE
1. Download and extract this ZIP.
2. Download/clone your GitHub repository locally.
3. Put repair_ironforge_structure.py beside manage.py.
4. Make a backup or use a separate Git branch.
5. Run: python repair_ironforge_structure.py
6. Review the changes and run: python manage.py check

The script preserves root-level source files and does not access or change secrets.
It copies current root files over matching destination files if those folders
already exist, so back up existing ironforge/, api/, or frontend/ folders first.

This has not been tested against your local checkout or production database.
Do not commit DATABASE_URL or other credentials. Share only sanitized errors.
