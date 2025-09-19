import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "insecure-key")
DEBUG = os.getenv("DEBUG", "False") == "True"

# ALLOWED HOSTS
ALLOWED_HOSTS = [
    "web-production-fd93.up.railway.app",  # your Railway domain
    "bjsolutions.com.ng",  # your frontend domain
]

# CSRF & Proxy settings for Railway
CSRF_TRUSTED_ORIGINS = [
    "https://web-production-fd93.up.railway.app",
    "https://bjsolutions.com.ng",
]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Optionally for testing if HTTPS issues persist
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Custom user model
AUTH_USER_MODEL = "accounts.CustomUser"

# Installed apps
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "accounts",
    "products",
    "commissions",
    "storages",  # ✅ required for Cloudflare R2
    "whitenoise.runserver_nostatic",
]

# Middleware
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# DRF & JWT
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    )
}

# CORS allowed origins
CORS_ALLOWED_ORIGINS = [
    "https://bjsolutions.com.ng",
    "https://web-production-fd93.up.railway.app",
]

# URLs & templates
ROOT_URLCONF = "bjsolutions.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "bjsolutions.wsgi.application"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("PGDATABASE"),
        "USER": os.getenv("PGUSER"),
        "PASSWORD": os.getenv("PGPASSWORD"),
        "HOST": os.getenv("PGHOST"),
        "PORT": os.getenv("PGPORT"),
    }
}

# Password validators
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ✅ Cloudflare R2 settings
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "bb0d5d951a19e02ed2159a617f8434a3")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "2b36c6621107726abe3656d0bc23eb1e2cc36aa359857b15d43dae419a660c50")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME", "bjsolutions")
AWS_S3_ENDPOINT_URL = os.getenv(
    "AWS_S3_ENDPOINT_URL",
    "https://133b31f32b36e2f6a915f530d16870d8.r2.cloudflarestorage.com"
)

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "storages.backends.s3boto3.S3StaticStorage",
    },
}

STATIC_URL = f"{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/"

# Media files (still local unless you want them in R2 too)
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Default PK
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
