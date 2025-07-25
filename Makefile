# Formatting and Linting
format-all:
	black . && ruff check . --fix

lint-all:
	ruff check .

safe-fix:
	ruff check . --fix

# Execution
run:
	uvicorn app.main:app --reload