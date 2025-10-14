clean:
	rm -rf dist

build: clean
	uv build

upload: build
	uv version --bump major
	export PYPI_TOKEN=$(cat .env | grep PYPI_TOKEN | cut -d '=' -f 2)
	uv publish -u __token__ -p $(PYPI_TOKEN)