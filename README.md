# Sentish

> *Sentish*  (`ˈsɛntɪʃ`)
>
> A name for a slow song in Balkan, usually with a sentimental or a love theme.

## Notes

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
