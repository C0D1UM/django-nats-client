default: yapf lint test

lint:
	poetry run pylint nats_client tests

test:
	cd tests && poetry run python manage.py test

coverage:
	poetry run coverage erase
	poetry run coverage run --source='nats_client' tests/manage.py test tests
	poetry run coverage report -m

yapf:
	poetry run yapf -ipr nats_client tests
