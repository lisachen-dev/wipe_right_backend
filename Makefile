# Formatting and Linting
format-all:
	uv run ruff format .
	uv run ruff check . --fix

lint-all:
	uv run ruff check .

# Execution
run:
	uv run uvicorn app.main:app --reload
