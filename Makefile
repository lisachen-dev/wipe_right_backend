format-all:
	@echo "[LINT/FORMAT IN PROGRESS] Running Ruff format and lint fix..."
	uv run ruff format .
	uv run ruff check . --select I --fix
	@echo "[FORMAT COMPLETE]"

lint-all:
	@echo "[LINT IN PROGRESS]"
	uv run ruff check .
	@echo "[LINT COMPLETE]"

# Execution
run:
	uv run uvicorn app.main:app --reload
