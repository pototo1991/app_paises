import os
import dj_database_url
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET_KEY y DEBUG controlados por variables de entorno para mayor seguridad en producción
SECRET_KEY = os.getenv(
    "SECRET_KEY", "your-secret-key"
)  # Reemplaza "your-secret-key" con una real para desarrollo
DEBUG = os.getenv("DEBUG", "False") == "True"

# Hosts permitidos
# Hosts permitidos
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "app_paises,onrender.com").split(",")


# Aplicaciones instaladas
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "myapp",
    "whitenoise.runserver_nostatic",  # Agrega whitenoise aquí
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Middleware de whitenoise para archivos estáticos
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "app_paises.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "app_paises.wsgi.application"

# Configuración de la base de datos usando dj_database_url
DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'db.sqlite3'}")
    )
}

# Validación de contraseñas
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internacionalización
LANGUAGE_CODE = "es-es"
TIME_ZONE = "America/Santiago"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Archivos estáticos
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "myapp/static"]
STATIC_ROOT = (
    BASE_DIR / "staticfiles"
)  # Directorio donde Render almacenará los archivos estáticos

# Configuración adicional para servir archivos estáticos en producción con Whitenoise
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Configuración de ID de campo primario
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
