# Sentish

> *Sentish*  `ˈsɛntɪʃ`
>
> A common name for a slow song in the South Slavic languages, usually with a sentimental or a love theme.

An MVP that parses content from an online publication, fetches the sentiment of the articles and displays results in a simple web app.

## Notes

### Development environment with Docker

1. Create a new file `.env` based on `.env.template`. Fill in the empty values.

2. Install docker and docker-compose.

3. From root of the project run:

    ```
    make up
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
