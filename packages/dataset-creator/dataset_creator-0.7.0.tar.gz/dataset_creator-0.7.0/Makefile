clean-test:
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr html/
	rm -rf cover/

test: clean-test
	pytest

coverage: test
	coverage report -m --include=dataset_creator/*
	coverage html

release:
	tox -e check
	rm -rf dist/ build/ *.egg-info
	python -m build
	twine upload dist/*

