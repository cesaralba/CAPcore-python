test:
	pytest tests

coverage:
	coverage run -m pytest tests
	coverage report -m
