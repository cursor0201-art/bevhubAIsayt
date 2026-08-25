import os
import sys
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file if present
load_dotenv(BASE_DIR / '.env')

# Add apps/ directory to sys.path to resolve subpackage modules
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

# Security settings (backed by env vars)
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    import warnings
    SECRET_KEY = 'django-insecure-bevhub-local-dev-only-change-in-prod'
    warnings.warn('DJANGO_SECRET_KEY is not set. Using insecure default (local dev only).', stacklevel=2)

DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '*').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party packages
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'drf_spectacular',
    
    # Internal Modules (representing clean layered applications)
    'core',
    'ai',
    'billing',
    'payments',
]

MIDDLEWARE = [
    'core.middleware_debug.ExceptionLoggingMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# ── Database ─────────────────────────────────────────────────────────────────
# Priority 1: DATABASE_URL (standard for Koyeb/Heroku/Render/etc)
_DATABASE_URL = os.environ.get('DATABASE_URL', '')
if _DATABASE_URL:
    import urllib.parse as _urlparse
    _u = _urlparse.urlparse(_DATABASE_URL)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': _u.path.lstrip('/'),
            'USER': _u.username,
            'PASSWORD': _u.password,
            'HOST': _u.hostname,
            'PORT': _u.port or 5432,
            'OPTIONS': {'sslmode': 'require'},
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
            'OPTIONS': {'timeout': 30},
        }
    }

# ── SQLite concurrency hardening (fixes "database is locked") ────────────────
# WAL journal mode allows concurrent readers while a writer is active, and
# busy_timeout makes writers wait instead of failing instantly. This is critical
# because the Django server and background workers share the same database file.
from django.db.backends.signals import connection_created

def _configure_sqlite_pragmas(sender, connection, **kwargs):
    if connection.vendor == 'sqlite':
        with connection.cursor() as cursor:
            cursor.execute('PRAGMA journal_mode=WAL;')
            cursor.execute('PRAGMA synchronous=NORMAL;')
            cursor.execute('PRAGMA busy_timeout=30000;')
            cursor.execute('PRAGMA foreign_keys=ON;')

connection_created.connect(_configure_sqlite_pragmas)
# Priority 2: individual POSTGRES_* vars (legacy support)
POSTGRES_DB = os.environ.get('POSTGRES_DB')
POSTGRES_USER = os.environ.get('POSTGRES_USER')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
POSTGRES_HOST = os.environ.get('POSTGRES_HOST')
POSTGRES_PORT = os.environ.get('POSTGRES_PORT')

if not _DATABASE_URL and all([POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST]):
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': POSTGRES_DB,
        'USER': POSTGRES_USER,
        'PASSWORD': POSTGRES_PASSWORD,
        'HOST': POSTGRES_HOST,
        'PORT': POSTGRES_PORT or '5432',
    }

# Custom User Model
AUTH_USER_MODEL = 'core.User'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# SimpleJWT configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# Swagger/OpenAPI Configuration
SPECTACULAR_SETTINGS = {
    'TITLE': 'BevHub AI API Platform',
    'DESCRIPTION': 'Enterprise SaaS platform API for building businesses using AI agents.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# CORS Configuration
CORS_ALLOW_ALL_ORIGINS = DEBUG  # Only open in dev
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get('DJANGO_CORS_ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
    if origin.strip()
]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'cache-control',
    'pragma',
    'expires',
]

# CSRF — required for Cloudflare Pages frontend domain in production
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS', 'http://localhost:3000').split(',')
    if origin.strip()
]

# Celery Configuration
# Production: set CELERY_BROKER_URL=redis://redis:6379/0 in .env
_redis_url = os.environ.get('CELERY_BROKER_URL', '')

if _redis_url:
    CELERY_BROKER_URL = _redis_url
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', _redis_url)
else:
    # Use SQLAlchemy SQLite transport for local MVP (no pywin32 required)
    CELERY_BROKER_URL = 'sqla+sqlite:///' + str(BASE_DIR / 'celery_broker.sqlite3')
    # Keep task results in a dedicated file so they never contend with the
    # main application database for write locks ("database is locked" fix).
    CELERY_RESULT_BACKEND = 'db+sqlite:///' + str(BASE_DIR / 'celery_results.sqlite3')

# ── Task dispatch mode ───────────────────────────────────────────────────────
# When BEVHUB_USE_CELERY=True a real Celery worker must be running
# (`celery -A config worker -l info --pool=solo`). When False (local dev
# default) tasks execute in a background thread inside Django so generation
# works even without a worker process. Prevents tasks stuck at 0% forever.
BEVHUB_USE_CELERY = os.environ.get('BEVHUB_USE_CELERY', 'False') == 'True'

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_EAGER_PROPAGATES = False

# Custom Test Runner to unify root-level integration tests and app-level unit tests
from django.test.runner import DiscoverRunner

class UnifiedDiscoverRunner(DiscoverRunner):
    def build_suite(self, test_labels=None, **kwargs):
        if not test_labels:
            test_labels = ['core', 'ai', 'billing', 'payments', 'tests']
        return super().build_suite(test_labels, **kwargs)

TEST_RUNNER = 'config.settings.UnifiedDiscoverRunner'

# Stripe Webhook Secret for signature verification
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', '')


