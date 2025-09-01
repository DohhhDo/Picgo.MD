# Define a variable for Python and notebook files.
PYTHON_FILES=.

#* Lint
.PHONY: lint
lint:
	black $(PYTHON_FILES) --check
	isort --check-only ./
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
