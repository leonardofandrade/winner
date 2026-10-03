from .base import *  # noqa: F401, F403

DEBUG = False

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")  # noqa: F405

STATIC_ROOT = BASE_DIR / "staticfiles"  # noqa: F405

CONN_MAX_AGE = 60
# O bot não passa pelo ciclo de request. Sem isso, uma conexão ociosa
# derrubada pelo MySQL só aparece como "Server has gone away".
CONN_HEALTH_CHECKS = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {"format": "%(asctime)s %(levelname)s %(name)s %(message)s"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "default"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
}
