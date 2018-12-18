from sentish.celery import app
from .logic import ParseContent


@app.task
def parse_content():
    ParseContent().parse_publishers()
