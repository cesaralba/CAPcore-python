test:
	pytest tests

coverage:
	coverage run --branch -m pytest tests
	coverage report -m

prospectorChanges:
	git diff --name-only | prospector
