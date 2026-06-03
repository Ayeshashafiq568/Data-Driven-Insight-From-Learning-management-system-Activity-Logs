import logging
import os
import warnings
from pathlib import Path
import dj_database_url
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)
warnings.simplefilter('default', UserWarning)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-m&!z*)#e%r7s@m0*k0*&s)v(3r_f(95j8r!x-6p^$n5%g7z%*1')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# In production, set ALLOWED_HOSTS from environment.
# Vercel sets VERCEL_URL and VERCEL in its runtime environment.
allowed_hosts_env = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1')
ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_env.split(',') if host.strip()]
vercel_url = os.environ.get('VERCEL_URL')
if vercel_url and vercel_url not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(vercel_url)
if os.environ.get('VERCEL') and '.vercel.app' not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append('.vercel.app')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'analytics',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'lms_insights.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'lms_insights.wsgi.application'

# Database
# https://docs.djangoproject.com/en/stable/ref/settings/#databases
# Use Supabase PostgreSQL in production, SQLite locally
postgres_url_non_pooling = os.environ.get('POSTGRES_URL_NON_POOLING')
postgres_url = os.environ.get('POSTGRES_URL')

# Normalize Supabase-style connection URLs for psycopg2/dj-database-url.
def normalize_database_url(database_url: str | None, *, env_name: str | None = None) -> str | None:
    if not database_url:
        return None
    normalized = database_url.strip()
    if '://' not in normalized:
        return normalized

    scheme, rest = normalized.split('://', 1)
    scheme_lower = scheme.lower()
    if scheme_lower in {'supabase', 'supa', 'postgres'}:
        normalized = f'postgresql://{rest}'
        if scheme_lower in {'supabase', 'supa'}:
            warning_message = (
                f"Normalized {env_name or 'database'} URL scheme '{scheme_lower}' to 'postgresql://' "
                "for psycopg2/dj-database-url compatibility."
            )
            warnings.warn(warning_message, stacklevel=2)
            logger.warning(warning_message)
    return normalized

# Export normalized DB URLs back into the environment so other libraries
# (or vendor code) that read `os.environ` get the corrected scheme.
def _export_normalized_db_env_vars() -> None:
    for key in ('POSTGRES_URL_NON_POOLING', 'POSTGRES_URL', 'DATABASE_URL'):
        raw = os.environ.get(key)
        if not raw:
            continue
        try:
            normalized = normalize_database_url(raw, env_name=key)
        except Exception:
            # If normalization somehow fails, skip exporting to avoid hiding original errors
            continue
        if normalized and normalized != raw:
            msg = f"Normalized environment {key} to psycopg2-compatible URL."
            warnings.warn(msg, stacklevel=2)
            logger.warning(msg)
            os.environ[key] = normalized

# Run early normalization so any vendor code reading env vars sees corrected URLs.
_export_normalized_db_env_vars()

# Validate database URL and provide a clear warning/error message.
def get_database_config(env_url: str | None, env_name: str) -> dict:
    normalized = normalize_database_url(env_url, env_name=env_name)
    if not normalized:
        raise ImproperlyConfigured(
            f"{env_name} is set but empty or invalid. Please provide a valid PostgreSQL database URL."
        )
    try:
        return dj_database_url.config(
            default=normalized,
            conn_max_age=600,
            conn_health_checks=True,
        )
    except Exception as exc:
        message = (
            f"Unable to parse {env_name} value. "
            "Make sure it is a valid PostgreSQL-style connection string. "
            f"Original error: {exc}"
        )
        if DEBUG:
            warnings.warn(message)
        raise ImproperlyConfigured(message) from exc

if postgres_url_non_pooling:
    # Prefer non-pooling URL for Django (pooling is for serverless)
    logger.info("Using POSTGRES_URL_NON_POOLING for database configuration.")
    DATABASES = {
        'default': get_database_config(postgres_url_non_pooling, 'POSTGRES_URL_NON_POOLING')
    }
elif postgres_url:
    # Fallback to pooling URL if available
    logger.info("Using POSTGRES_URL for database configuration.")
    DATABASES = {
        'default': get_database_config(postgres_url, 'POSTGRES_URL')
    }
elif os.environ.get('DATABASE_URL'):
    # Alternative: Generic DATABASE_URL support
    logger.info("Using DATABASE_URL for database configuration.")
    DATABASES = {
        'default': get_database_config(os.environ.get('DATABASE_URL'), 'DATABASE_URL')
    }
else:
    # Development: SQLite
    logger.info("No PostgreSQL URL found; defaulting to local SQLite database.")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
# https://docs.djangoproject.com/en/stable/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/stable/topics/i18n/
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/stable/howto/static-files/
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'analytics', 'static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Ensure staticfiles directory exists for collectstatic / WhiteNoise
if not os.path.isdir(STATIC_ROOT):
    os.makedirs(STATIC_ROOT, exist_ok=True)

# WhiteNoise settings for serving static files efficiently
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Ensure staticfiles directory exists for collectstatic / WhiteNoise
if not os.path.isdir(STATIC_ROOT):
    os.makedirs(STATIC_ROOT, exist_ok=True)

# Media files (for CSV uploads)
MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Ensure media directory exists
if not os.path.isdir(MEDIA_ROOT):
    os.makedirs(MEDIA_ROOT, exist_ok=True)

# Default primary key field type
# https://docs.djangoproject.com/en/stable/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'analytics.User'

# Authentication redirects
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'
LOGIN_URL = 'login'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '[%(levelname)s] %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
