.PHONY: help backend frontend test

help:
	@echo "Available targets:"
	@echo "  make backend   - start FastAPI backend"
	@echo "  make frontend  - start Streamlit frontend"
	@echo "  make test      - run backend tests"

backend:
	uv run uvicorn FamCalender.backend.main:app --reload --port 8000

frontend:
	uv run streamlit run FamCalender/frontend/streamlit.py

test:
	PYTHONPATH=. uv run --with pytest pytest
