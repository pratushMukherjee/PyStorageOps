.PHONY: install test lint run clean build docker-up docker-down benchmark

install:
	python -m pip install -r requirements.txt
	python -m pip install -e ".[dev]"

test:
	python -m pytest tests/ -v --cov=src --cov-report=term-missing

lint:
	python -m ruff check src/ tests/

run:
	python -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --reload

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf build/ dist/ *.egg-info .pytest_cache htmlcov .coverage

build-c:
	$(MAKE) -C c_extensions

benchmark:
	bash scripts/benchmark.sh

docker-up:
	docker-compose up -d --build

docker-down:
	docker-compose down
