import environ
from configurations import Configuration


# Django-Environ instance that will parse the enviroment variables
ENV = environ.Env()

BASE_DIR = environ.Path(__file__) - 2
ENV.read_env(str(BASE_DIR.path(ENV.str("ENV_PATH", ".env"))))


class BaseConfig(Configuration):
    """Base Django Configuration class with values repeated among all the environments."""

    DEBUG = False

    ALLOWED_HOSTS = []

    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = ENV.str("SECRET_KEY")

    STATICFILES_DIRS = [str(BASE_DIR.path("static/"))]
    # absolute path to the directory where collectstatic will collect static files for deployment
    STATIC_ROOT = str(BASE_DIR.path("staticfiles/"))
    # URL to use when referring to static files located in STATIC_ROOT
    STATIC_URL = "/static/"
    # file storage engine to use when collecting static files with the collectstatic management command
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

    # Application definition

    INSTALLED_APPS = [
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        # 3rd party
        # project
        "content",
        "feeds",
    ]

    MIDDLEWARE = [
        "django.middleware.security.SecurityMiddleware",
        "whitenoise.middleware.WhiteNoiseMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ]

    ROOT_URLCONF = "sentish.urls"

    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [str(BASE_DIR.path("templates/"))],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ]
            },
        }
    ]

    WSGI_APPLICATION = "sentish.wsgi.application"

    # Database
    # https://docs.djangoproject.com/en/2.1/ref/settings/#databases

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": str(BASE_DIR.path("db.sqlite3")),
        }
    }

    # Password validation
    # https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

    AUTH_PASSWORD_VALIDATORS = [
        {
            "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
        },
        {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
        {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
        {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
    ]

    # Internationalization
    # https://docs.djangoproject.com/en/2.1/topics/i18n/
    LANGUAGE_CODE = "en-us"
    TIME_ZONE = "UTC"
    USE_I18N = True
    USE_L10N = True
    USE_TZ = True

    # IBM watson settings
    WATSON_API_VERSION = "2018-11-16"
    WATSON_URL = (
        "https://gateway-lon.watsonplatform.net/natural-language-understanding/api"
    )


class PostgresDBConfig:
    """Postgres DB connection defined."""

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": ENV.str("POSTGRES_DB"),
            "USER": ENV.str("POSTGRES_USER"),
            "PASSWORD": ENV.str("POSTGRES_PASSWORD"),
            "HOST": ENV.str("POSTGRES_HOST", "localhost"),
            "PORT": ENV.str("POSTGRES_PORT", "5432"),
        }
    }


class CeleryConfig:
    """Celery Task Queue configs."""

    # URL formated as `redis://:password@hostname:port/db_number`
    BROKER_URL = ENV.str("CELERY_REDIS_URL", "redis://redis:6379/0")
    CELERY_BROKER_URL = BROKER_URL
    CELERY_RESULT_BACKEND = BROKER_URL
    CELERY_ACCEPT_CONTENT = ["application/json"]
    CELERY_TASK_SERIALIZER = "json"
    CELERY_RESULT_SERIALIZER = "json"


class DevConfig(PostgresDBConfig, CeleryConfig, BaseConfig):
    """Django Configuration class with specifics for the local environment."""

    DEBUG = True
    ALLOWED_HOSTS = ["*"]

    RUNSERVERPLUS_SERVER_ADDRESS_PORT = "8020"

    INSTALLED_APPS_TOP = ["whitenoise.runserver_nostatic"]
    INSTALLED_APPS_BOTTOM = ["django_extensions", "debug_toolbar"]
    INSTALLED_APPS = (
        INSTALLED_APPS_TOP + BaseConfig.INSTALLED_APPS + INSTALLED_APPS_BOTTOM
    )

    MIDDLEWARE = BaseConfig.MIDDLEWARE + [
        "debug_toolbar.middleware.DebugToolbarMiddleware"
    ]

    def show_debug_toolbar(request):
        """Hack to display debug toolbar when running in Docker."""
        return True

    DEBUG_TOOLBAR_CONFIG = {"SHOW_TOOLBAR_CALLBACK": show_debug_toolbar}


class ProdConfig(PostgresDBConfig, CeleryConfig, BaseConfig):
    """Django Configuration class with specifics for the production environment."""

    # This is safe for a kubernetes installation
    ALLOWED_HOSTS = ["*"]

    STATIC_ROOT = "staticfiles/"
    STATIC_URL = ENV.str("STATIC_URL", "/static/")

    if ENV.str("BUGSNAG_API_KEY", None):
        BUGSNAG = {"api_key": ENV.str("BUGSNAG_API_KEY"), "project_root": BASE_DIR}

        MIDDLEWARE = [
            "bugsnag.django.middleware.BugsnagMiddleware"
        ] + BaseConfig.MIDDLEWARE


class TestConfig(PostgresDBConfig, BaseConfig):
    """Django Configuration class with specifics for the test suite environment."""

    @classmethod
    def post_setup(cls):
        super(TestConfig, cls).post_setup()

        # run test suite with dockerized postgres, but from local machine
        DATABASES["default"]["HOST"] = "localhost"


class CITestConfig(PostgresDBConfig, BaseConfig):
    """Django Configuration class with specifics for the test suite environment
    when run on Circle CI.
    """

    pass
