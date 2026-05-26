.PHONY: install test run-watcher

install:
	python3 -m venv venv
	./venv/bin/pip install -r requirements.txt

test:
	export PYTHONPATH=src && ./venv/bin/pytest tests/

run:
	@if [ -z "$(board)" ] || [ -z "$(thread)" ]; then \
		echo "Usage: make run board=b thread=123456"; \
	else \
		export PYTHONPATH=src && ./venv/bin/python src/main.py $(board) $(thread); \
	fi
