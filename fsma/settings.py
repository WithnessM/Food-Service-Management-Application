import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-bead6^4d2t9%!%gv*@d!jr+b56mpi2@9cuwhs2vhwx#z$*^%5+"
)

DEBUG = os.environ.get("DEBUG", "True") == "True"

# Hosts / CSRF
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")
CSRF_TRUSTED_ORIGINS = os.environ.get(
    "CSRF_TRUSTED_ORIGINS", "https://*.up.railway.app"
).split(",")

# Database
if os.environ.get("DATABASE_URL"):  # Railway or any cloud DB
    DATABASES = {
        "default": dj_database_url.config(
            default=os.environ["DATABASE_URL"],
            conn_max_age=600,
            ssl_require=True
        )
    }
else:  # Local dev (Postgres)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "railway",
            "USER": "postgres",
            "PASSWORD": "jQlToDvMhgXMCzEykiqGCXBCarcqoAga",
            "HOST": "localhost",
            "PORT": "5432",
        }
    }

# Static files
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
