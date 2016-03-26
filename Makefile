.PHONY: clean

init:
	pip install -r testing-requirements.txt

test: clean
	py.test -s --verbose -p no:cacheprovider tests

style:
	flake8 struct_api

coverage:
	py.test --verbose --cov-report term-missing --cov=struct_api -p no:cacheprovider tests

ci: init style test

publish:
	python setup.py register
	python setup.py sdist upload
	rm -fr build dist .egg struct_api.egg-info

docs-init:
	pip install -r docs/requirements.txt

clean:
	rm -rf struct_api/*.pyc
	rm -rf struct_api/__pycache__
	rm -rf tests/__pycache__

docs:
	cd docs && make html
	@echo "\033[95m\n\nBuild successful! View the docs homepage at docs/_build/html/index.html.\n\033[0m"
