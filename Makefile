.PHONY: auth_makemigrations,auth_migrate

auth_makemigrations:
	docker compose run -ti --rm auth python auth/manage.py makemigrations

auth_migrate:
	docker compose run -ti --rm auth python auth/manage.py migrate


.PHONY: tracker_makemigrations,tracker_migrate

tracker_makemigrations:
	docker compose run -ti --rm tracker python task_tracker/manage.py makemigrations

tracker_migrate:
	docker compose run -ti --rm tracker python task_tracker/manage.py migrate


format:
	ruff format .
	isort .
