PYTHON_VERSION = `head -1 .python-version`
ENVIRONMENT = staging


.PHONY: venv shell requirements run version

venv:
	poetry env use ${PYTHON_VERSION}
	poetry shell

shell:
	# ref: https://stackoverflow.com/a/70604378
	ENVIRONMENT=${ENVIRONMENT} poetry run ipython -i asgi.py

requirements: venv
	poetry export -f requirements.txt --output requirements.txt --without-urls --only=main
	poetry export -f requirements.txt --output development.txt --without-urls --only=dev,test,lint

run:
	@if [ "${ENVIRONMENT}" = "production" ]; then\
		ENVIRONMENT=${ENVIRONMENT} poetry run fastapi run --host 0.0.0.0 --port 8000 --workers 4 asgi.py;\
	else\
		ENVIRONMENT=${ENVIRONMENT} poetry run fastapi dev --host 0.0.0.0 --port 8000 asgi.py --reload;\
	fi

# reference :: https://github.com/commitizen-tools/commitizen
version:
	cz bump --changelog --check-consistency
