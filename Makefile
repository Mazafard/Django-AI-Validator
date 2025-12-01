install:
	pip3 install -e .
	pip3 install -r requirements-dev.txt

test:
	python3 -m pytest

coverage:
	python3 -m pytest
	@echo "HTML report generated in htmlcov/index.html"

build: clean
	python3 -m build

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
