MODULE_NAME=pystructs

.PHONY: clean

init:
	pip install -r testing-requirements.txt

test: clean
	py.test -s --verbose -p no:cacheprovider tests

style:
	flake8 $(MODULE_NAME)

coverage:
	py.test --verbose --cov-report term-missing --cov=$(MODULE_NAME) -p no:cacheprovider tests

ci: init style test

publish:
	python setup.py register
	python setup.py sdist upload
	rm -fr build dist .egg $(MODULE_NAME).egg-info

docs-init:
	pip install -r docs/requirements.txt

clean:
	rm -rf $(MODULE_NAME)/*.pyc
	rm -rf $(MODULE_NAME)/__pycache__
	rm -rf tests/__pycache__

docs:
	cd docs && make html
	@echo "\033[95m\n\nBuild successful! View the docs homepage at docs/_build/html/index.html.\n\033[0m"
