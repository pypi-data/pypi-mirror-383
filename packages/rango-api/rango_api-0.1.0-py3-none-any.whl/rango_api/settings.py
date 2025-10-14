#rango/settings.py

INSTALLED_APPS = []

DATABASE_URL = "sqlite://db.sqlite3"

TORTOISE_ORM = {
    "connections": {"default": DATABASE_URL},
    "apps": {
        "models": {
            "models": ["aerich.models"] + INSTALLED_APPS,
            "default_connection": "default",
        },
    },
}
