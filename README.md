# Sentish

[![CircleCI](https://circleci.com/gh/mislavcimpersak/sentish/tree/master.svg?style=svg)](https://circleci.com/gh/mislavcimpersak/sentish/tree/master)

> *Sentish*  `ˈsɛntɪʃ`
>
> A common name for a slow song in the South Slavic languages, usually with a sentimental or a love theme.

An MVP that parses content from an online publication, fetches the sentiment of the articles and displays results in a simple web app.

## Rationale

App periodically fetches newest articles from an online publication (Forbes). For it, it uses [Forbes realt-time RSS feed](https://www.forbes.com/real-time/feed2/).

Second periodical task fetches the content of the articles, cleans it and uses [IBM Watson's NLU](https://www.ibm.com/watson/services/natural-language-understanding/) to get a sentiment score.

All processed articles with their accompanying scores are available [online](https://sentish.solvomon.com/).

## Notes

### Development environment with Docker

1. Create a new file `.env` based on `.env.template`. Fill in the empty values.

2. Install docker and docker-compose.

3. From root of the project run:

    ```
    make start
    ```

    This command will build Django application Docker image and run Django app on localhost on port 8020.

4. Open Django application in browser:

    ```
    http://127.0.0.1:8020
    ```

### Pre-commit Hooks

Project uses [pre-commit](https://github.com/pre-commit/pre-commit) hooks. To use them for your local development install them with the following command:

```
pre-commit install
```

Code formating is done with [Black](https://github.com/ambv/black) and an additional [requirement files check](https://github.com/pre-commit/pre-commit-hooks) is run.

### Django Configuration

[Django-Configurations](https://github.com/jazzband/django-configurations) is a total overkill for this project, but is a smart thing to use in a project from the beginning if it ever grows.

### `.env` file

Project uses [Django-environ](https://github.com/joke2k/django-environ/). That way all required environment variables for the project are available in `.env` file.
`.env.template` file exists to show which env vars are required to exist in the real `.env`.

Example of local `.env` file that is needed to get the project running with Docker is as follows:

```bash
DJANGO_SETTINGS_MODULE=sentish.settings
DJANGO_CONFIGURATION=DevConfig
SECRET_KEY=123456_dummy_654321

POSTGRES_HOST=postgres
POSTGRES_DB=sentish
POSTGRES_USER=sentish
POSTGRES_PASSWORD=sentish

CELERY_REDIS_URL=redis://redis:6379/0

WATSON_IAM_APIKEY=enter_your_api_key
```

### Celery Beat

[Celery Beat](http://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html) is used to periodically fetch fresh articles and get their sentiment score.

Redis is used as the broker since it's much easier to set it up on GCP than a full-blown RabbitMQ.

### Deployment

Deployed on GCP.

You need to have the following tools installed:

    - Google Cloud SDK - https://cloud.google.com/sdk/
    - Terraform - https://www.terraform.io/downloads.html
    - Kubectl - https://kubernetes.io/docs/tasks/tools/install-kubectl/

#### Infra

From GCP Console `gcp_credentials.json` file needs to be obtained before using `terraform`.

Once credentials are obtained, from `/infra` repo, `terraform` commands can be run.

Run

```bash
terraform apply
```

to set the infra or modify it.

#### (Re)deplyoment

Main app and celery worker/beat are deplyed in a kubernetes cluster.
For a quick deplyoment, a shortcut make target was created:

```bash
make deploy
```

For production `.env.prod` must exist when building the image. Create it from `.env.template` and populate it with production values.
