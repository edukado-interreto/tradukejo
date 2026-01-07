dc := docker compose
dj := docker compose exec django ./manage.py
user_id := $(shell id -u)
group_id := $(shell id -g)

all: run
build: reqs build_django

run:
	USER_ID=$(user_id) GROUP_ID=$(group_id) $(dc) up mariadb django

reqs:
	uv export --all-groups --no-hashes --all-packages > requirements.txt

build_django:
	$(dc) build django

shell:
	$(dj) shell_plus

superuser:
	$(dj) createsuperuser

migrations:
	$(dj) makemigrations

migrate:
	$(dj) migrate
