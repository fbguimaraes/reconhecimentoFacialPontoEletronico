"""
Configuração de produção para Django.
Para usar: set DJANGO_SETTINGS_MODULE=config.settings_production
"""

from .settings import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Hosts permitidos (ADICIONE OS IPs/DOMÍNIOS DO SEU SERVIDOR)
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '192.168.1.100',  # Exemplo: IP do servidor na rede local
    # 'seudominio.com',  # Adicione seu domínio se houver
]

# Gere uma chave secreta única para produção
# Execute: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
SECRET_KEY = 'GERE_UMA_CHAVE_SECRETA_UNICA_AQUI'

# Segurança
SECURE_SSL_REDIRECT = False  # Mude para True se usar HTTPS
SESSION_COOKIE_SECURE = False  # Mude para True se usar HTTPS
CSRF_COOKIE_SECURE = False  # Mude para True se usar HTTPS
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# CORS - Permitir acesso da aplicação Tkinter
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://192.168.1.100:8000",  # Ajuste conforme necessário
]

CORS_ALLOW_ALL_ORIGINS = False  # Produção = False

# Database (PostgreSQL recomendado para produção)
# Descomente e configure se usar PostgreSQL:
"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'reconhecimento_facial',
        'USER': 'postgres',
        'PASSWORD': 'SUA_SENHA_SEGURA',
        'HOST': 'localhost',
        'PORT': '5432',
        'CONN_MAX_AGE': 600,  # Connection pooling
    }
}
"""

# Cache com Redis (descomente se usar Redis)
"""
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
"""

# Logging para produção
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django_errors.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'employees': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Criar diretório de logs se não existir
import os
logs_dir = BASE_DIR / 'logs'
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Static files (para servir com Nginx/Apache em produção)
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_ROOT = BASE_DIR / 'media'

# Email (configurar para notificações)
"""
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'seu-email@gmail.com'
EMAIL_HOST_PASSWORD = 'sua-senha-app'
DEFAULT_FROM_EMAIL = 'sistema@empresa.com'
ADMINS = [('Admin', 'admin@empresa.com')]
"""

print("✓ Configurações de PRODUÇÃO carregadas")
print(f"  DEBUG: {DEBUG}")
print(f"  ALLOWED_HOSTS: {ALLOWED_HOSTS}")
