.PHONY: help backend frontend docker-up docker-down test lint typecheck check

help:
	@echo "Available targets:"
	@echo "  make backend   - start FastAPI backend"
	@echo "  make frontend  - start Streamlit frontend"
	@echo "  make docker-up - start the full app with Docker Compose"
	@echo "  make docker-down - stop Docker Compose services"
	@echo "  make test      - run backend tests"
	@echo "  make lint      - run code analysis"
	@echo "  make typecheck - run type checks"
	@echo "  make check     - run tests, code analysis and type checks"

backend:
	uv run uvicorn FamCalender.backend.main:app --reload --port 8000

frontend:
	uv run streamlit run FamCalender/frontend/streamlit.py

docker-up:
	docker compose up --build

docker-down:
	docker compose down

test:
	PYTHONPATH=. uv run --with pytest pytest

lint:
	uv run --with ruff ruff check .

typecheck:
	uv run --with mypy mypy FamCalender/backend FamCalender/frontend/streamlit.py

check: test lint typecheck
