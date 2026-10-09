#!/usr/bin/env python3
"""Create the Django package layout expected by the existing IRONFORGE code.
Run from repository root (the folder containing manage.py). Original root files
are preserved. No secrets are read, printed, generated, or changed.
"""
from pathlib import Path
import shutil
import sys

ROOT = Path.cwd()
required = ["manage.py", "settings.py", "urls.py", "views.py", "models.py",
            "serializers.py", "admin.py", "apps.py", "permissions.py",
            "wsgi.py", "asgi.py", "health.py", "index.html",
            "admin-portal.html", "coach-portal.html"]
missing = [x for x in required if not (ROOT / x).is_file()]
if missing:
    sys.exit("Run from repository root. Missing: " + ", ".join(missing))

def copy_source(src_name, dest):
    src = ROOT / src_name
    if src.is_file():
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        print(f"Copied {src_name} -> {dest.relative_to(ROOT)}")

# Project package referenced by manage.py and settings.py.
project = ROOT / "ironforge"
project.mkdir(exist_ok=True)
(project / "__init__.py").write_text("", encoding="utf-8")
for name in ("settings.py", "wsgi.py", "asgi.py", "health.py"):
    copy_source(name, project / name)

# Application package referenced by INSTALLED_APPS.
api = ROOT / "api"
api.mkdir(exist_ok=True)
for name in ("admin.py", "apps.py", "models.py", "permissions.py",
             "serializers.py", "views.py", "urls.py"):
    copy_source(name, api / name)
(api / "__init__.py").write_text("", encoding="utf-8")

# Move the existing numbered migrations into the Django app migration package.
migrations = api / "migrations"
migrations.mkdir(parents=True, exist_ok=True)
(migrations / "__init__.py").write_text("", encoding="utf-8")
migration_files = sorted(ROOT.glob("[0-9][0-9][0-9][0-9]_*.py"))
if not migration_files:
    print("WARNING: no numbered migration files found at repository root.")
for src in migration_files:
    shutil.copy2(src, migrations / src.name)
    print(f"Copied {src.name} -> api/migrations/{src.name}")

# The existing root urls.py contains API routes; create the separate project URL config.
project_urls = 'from django.contrib import admin\nfrom django.urls import include, path\nfrom django.views.generic import TemplateView\nfrom .health import health\n\nurlpatterns = [\n    path("admin/", admin.site.urls),\n    path("api/", include("api.urls")),\n    path("health/", health),\n    path("admin-portal/", TemplateView.as_view(template_name="admin-portal.html"), name="admin-portal"),\n    path("admin-portal.html", TemplateView.as_view(template_name="admin-portal.html"), name="admin-portal-file"),\n    path("coach-portal.html", TemplateView.as_view(template_name="coach-portal.html"), name="coach-portal"),\n    path("", TemplateView.as_view(template_name="index.html"), name="home"),\n]\n'
(project / "urls.py").write_text(project_urls, encoding="utf-8")
print("Created ironforge/urls.py")

# The settings already use BASE_DIR/frontend for templates and static files.
frontend = ROOT / "frontend"
frontend.mkdir(exist_ok=True)
for name in ("index.html", "admin-portal.html", "coach-portal.html"):
    copy_source(name, frontend / name)

assets = frontend / "assets"
assets.mkdir(parents=True, exist_ok=True)
if (ROOT / "assets").is_dir():
    shutil.copytree(ROOT / "assets", assets, dirs_exist_ok=True)
qr = ROOT / "himanshu_upi_qr.jpg"
if qr.is_file():
    shutil.copy2(qr, assets / "himanshu_upi_qr.jpg")
    print("Copied the existing QR image into frontend/assets/")
else:
    print("WARNING: add the existing QR image manually to frontend/assets/")

print("\nOriginal root-level files were preserved.")
print("Next run: python manage.py check")
print("Then review the complete Git diff before committing or deploying.")
