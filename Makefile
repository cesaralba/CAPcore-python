test:
	pytest tests

coverage:
	coverage run --branch -m pytest tests
	coverage report -m

prospectorChanges:
	prospector $(git diff --name-only)
