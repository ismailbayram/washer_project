.sh
#!/usr/bin/env bash

file="washer_project/settings_test.py"
if [ -f "$file" ]; then
    echo "settings_test exists..."
else
    cat > $file <<EOF
DEBUG = True

LOGIN_URL = 'rest_framework:login'
LOGOUT_URL = 'rest_framework:logout'

CACHE_BACKEND_URL = 'redis://127.0.0.1:6379/0'

CELERY_BROKER_URL = 'redis://127.0.0.1:6379/1'

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": CACHE_BACKEND_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

EOF

fi

pytest --durations=10
