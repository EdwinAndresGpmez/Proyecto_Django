"""
Django settings for DjangoProyecto project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv  # Para cargar las variables del .env
import mimetypes

# Carga las variables de .env (asegúrate de que .env esté al lado de manage.py)
load_dotenv()

mimetypes.add_type("text/css", ".css", True)

# Construimos la ruta base
BASE_DIR = Path(__file__).resolve().parent.parent

# ===========================
#  Variables de entorno
# ===========================
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')  # Sin fallback, exige definirlo en .env
DEBUG = os.getenv('DJANGO_DEBUG', 'False').lower() == 'true'
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', '').split(',')

# Cookies y sesiones
CSRF_COOKIE_NAME = 'csrftoken'
CSRF_COOKIE_HTTPONLY = True
# Cambia a True si usas HTTPS en producción
CSRF_COOKIE_SECURE = False  
SESSION_COOKIE_AGE = 1800  # 30 minutos
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True

# ===========================
#  Aplicaciones
# ===========================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Tus apps:
    'invitado',
    'entrarSistema',
    'usuario',
    'administrador',
    'programador',

    # Librerías extra
    'widget_tweaks',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'DjangoProyecto.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates/layout')],
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

# Modelo de usuario personalizado
AUTH_USER_MODEL = 'entrarSistema.CrearCuenta'
WSGI_APPLICATION = 'DjangoProyecto.wsgi.application'
LOGIN_URL = '/inicio/'

# ===========================
#  Base de datos
# ===========================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv('POSTGRES_DB', 'citas_bd'),
        "USER": os.getenv('POSTGRES_USER', 'postgres'),
        "PASSWORD": os.getenv('POSTGRES_PASSWORD'),
        "HOST": os.getenv('POSTGRES_HOST', '127.0.0.1'),
        "PORT": os.getenv('POSTGRES_PORT', '5433'),
    }
}

# ===========================
#  Validación de contraseñas
# ===========================
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 3},
    },
    # Añade las que necesites:
    # {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    # {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ===========================
#  Internacionalización
# ===========================
LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True
USE_L10N = True

LANGUAGES = [
    ('es', 'Spanish'),
    # otros idiomas si deseas
]
LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

# ===========================
#  Archivos estáticos
# ===========================
STATIC_URL = '/static/'
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'DjangoProyecto/static'),)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ===========================
#  Caché
# ===========================
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': BASE_DIR / 'cache',
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        },
        'TIMEOUT': 300,
    }
}

# ===========================
#  Configuración de Emails
# ===========================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS')
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

print(f"Valor de EMAIL_HOST_PASSWORD: {repr(EMAIL_HOST_PASSWORD)}")

# ===========================
#  Configuración Twilio
# ===========================
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
