.PHONY: clean clean-test clean-pyc clean-build docs help


clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts


clean-build: ## remove build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf .eggs/
	find . -name '*.egg-info' -exec rm -rf {} +
	find . -name '*.egg' -exec rm -f {} +


clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +


clean-test: ## remove test and coverage artifacts
	rm -rf .tox/
	rm -f .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache


dist: clean ## builds source and wheel package
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist


lint: ## check style with flake8
	flake8 wcap


install: clean ## install the package to the active Python's site-packages
	python setup.py install


# Call example: make release version=0.2.0
release: dist
	git tag -a $(version) -m 'Create version $(version)'
	git push --tags
	twine upload dist/*


test:
	wcap --dimensions 1500x1100 --wait 5 https://ukealong.com/key/c/ img/c.png
	wcap --dimensions 1500x1100 https://ukealong.com/key/d/ img/d.png
	wcap https://ukealong.com/key/e/ img/e.png


typecheck:
	mypy --ignore-missing-imports wcap