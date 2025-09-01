install:
	pip install -e .
	pip install -r requirements-dev.txt

test:
	python manage.py test sandbox_app

coverage:
	coverage run --source=src/django_ai_validator sandbox/manage.py test sandbox_app
	coverage report
	coverage html
	@echo "HTML report generated in htmlcov/index.html"

build: clean
	python -m build

clean:
	rm -rf dist/ build/ *.egg-info/

publish-test: build
	twine upload --repository testpypi dist/*

publish: build
	twine upload dist/*

tag-version:
	@if [ -z "$(v)" ]; then echo "Usage: make tag-version v=X.Y.Z"; exit 1; fi
	git tag -a v$(v) -m "Release v$(v)"
	git push origin v$(v)
