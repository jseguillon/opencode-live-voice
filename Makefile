.PHONY: install dev run demo test lint typecheck plugin-install plugin-typecheck clean

install:
	python -m pip install -e .

dev:
	python -m pip install -e '.[dev]'

run:
	opencode-live-voice

demo:
	PYTHONPATH=src python scripts/demo.py

test:
	PYTHONPATH=src pytest -q

lint:
	ruff check src tests scripts

typecheck:
	mypy src/opencode_live_voice

plugin-install:
	cd plugin && npm install

plugin-typecheck:
	cd plugin && npm run typecheck

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache dist build plugin/dist plugin/node_modules
