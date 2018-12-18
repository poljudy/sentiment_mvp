import environ
import os
from celery import Celery
from django.conf import settings


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sentish.settings")

ENV = environ.Env()
os.environ.setdefault(
    "DJANGO_CONFIGURATION", ENV.str("DJANGO_CONFIGURATION", "ProdConfig")
)

import configurations  # noqa

configurations.setup()

app = Celery("sentish")
app.config_from_object("django.conf:settings")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


app.conf.beat_schedule = {
    "parse-all-feeds": {"task": "feeds.tasks.parse_feeds", "schedule": 60},
    "parse-all-content": {"task": "content.tasks.parse_content", "schedule": 60 * 3},
}
