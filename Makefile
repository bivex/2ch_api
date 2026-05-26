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
		export PYTHONPATH=src && ./venv/bin/python3 src/main.py watch $(board) $(thread); \
	fi

top:
	@if [ -z "$(board)" ]; then \
		echo "Usage: make top board=po limit=5 sort=posts"; \
	else \
		export PYTHONPATH=src && ./venv/bin/python3 src/main.py top $(board) --limit $(or $(limit),10) --sort $(or $(sort),posts); \
	fi
