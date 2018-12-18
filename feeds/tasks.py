from sentish.celery import app
from .logic import ParseFeeds


@app.task
def parse_feeds():
    ParseFeeds().parse_feeds()
