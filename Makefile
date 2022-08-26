default: yapf lint test

lint:
	poetry run pylint django_nats tests

test:
	cd tests && poetry run python manage.py test

coverage:
	poetry run coverage erase
	poetry run coverage run --source='django_nats' tests/manage.py test tests
	poetry run coverage report -m

yapf:
	poetry run yapf -ipr django_nats tests
