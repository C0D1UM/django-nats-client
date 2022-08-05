default: yapf lint test

lint:
	poetry run pylint django_nats test_django_nats

.test-pg:
	cd test_django_nats && poetry run coverage run manage.py test

.coverage-erase:
	cd test_django_nats && poetry run coverage erase

.coverage-report:
	cd test_django_nats && poetry run coverage report -m

test: .coverage-erase .test .coverage-report

yapf:
	poetry run yapf -ipr django_nats test_django_nats
