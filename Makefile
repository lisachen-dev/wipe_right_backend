# Formatting and Linting
format-all:
	ruff format .
	ruff check . --fix

lint-all:
	ruff check .

# Execution
run:
	uvicorn app.main:app --reload
