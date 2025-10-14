clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr html/
	rm -rf cover/

test: clean-test
	pytest --verbosity=2

coverage: test
	coverage run --source=seqrecord_expanded setup.py test
	coverage report -m
	coverage html

release:
	tox -e check
	rm -rf dist/ build/ *.egg-info
	python -m build
	twine upload dist/*
