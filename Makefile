# Environment variables
DOCKER_COMPOSE ?= docker-compose
DOCKER_COMPOSE_FILE ?= docker-compose.yml
WEB_PORT ?= 8020

# Colors
define echo_cyan
  echo "\033[0;36m$(subst ",,$(1))\033[0m"
endef

define echo_green
  echo "\033[0;32m$(subst ",,$(1))\033[0m"
endef

define echo_red
  echo "\033[0;31m$(subst ",,$(1))\033[0m"
endef

define echo_yellow
  echo "\033[0;33m$(subst ",,$(1))\033[0m"
endef

help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z][a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Targets

build: ## Build all or c=<name> containers
	@$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) build $(c)

start: ## Start all or c=<name> containers in background
	@$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) up -d $(c)

stop: ## Stop all or c=<name> containers
	@$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) stop $(c)

restart: stop start ## Restart all or c=<name> containers and start in background

status: ## Show status of containers
	@$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) ps

ps: status ## Alias of status

_django_manage:
	@$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) exec web python manage.py ${COMMAND}

django_migrate:  ## `python manage.py migrate` command inside the container
	$(MAKE) COMMAND="migrate" _django_manage

django_makemigrations: ## `python manage.py makemigrations` command inside the container
	$(MAKE) COMMAND=makemigrations _django_manage

django_showmigrations: ## `python manage.py showmigrations` command inside the container
	$(MAKE) COMMAND=showmigrations _django_manage

django_createsuperuser: ## `python manage.py createsuperuser` command inside the container
	$(MAKE) COMMAND=createsuperuser _django_manage

django_shell: ## `python manage.py shell` command inside the container
	$(MAKE) COMMAND=shell _django_manage

django_shell_plus: ## `python manage.py shell_plus` command inside the container
	$(MAKE) COMMAND="shell_plus" _django_manage

deploy: ## build new Docker.prod image and re-deploy to GCP kubernetes
	@( read -p "Have you bumped BUILD_NUMBER in infra/gcp_kubernetes.yml? [y/N]: " sure && case "$$sure" in [yY]) true;; *) false;; esac )
	gcloud container clusters get-credentials gke-sentish --zone europe-west2-a --project sentish
	docker build -t gcr.io/sentish/sentish-app -f Dockerfile.prod .
	docker push gcr.io/sentish/sentish-app
	# if nothing is changed in k8s config, BUILD_NUMBER in infra/gcp_kubernetes.yml must be bumped
	kubectl apply -f infra/gcp_kubernetes.yml
	# stage kubernetess config with new build number
	git add infra/gcp_kubernetes.yml
	@echo "Please commit build number."
