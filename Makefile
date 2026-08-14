.PHONY: install uninstall test lint release clean

PREFIX ?= /usr/local
VERSION := $(shell python3 -c "from touchflow import __version__; print(__version__)")

install:
	bash scripts/install.sh

uninstall:
	systemctl --user disable --now touchflow-daemon.service 2>/dev/null || true
	pip3 uninstall -y touchflow-keyboard 2>/dev/null || true

test:
	python3 -m pytest tests/ -v

lint:
	ruff check touchflow touchflow_settings

release:
	bash scripts/build-release.sh

clean:
	rm -rf dist build *.egg-info .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

.PHONY: help
help:
	@echo "TouchFlow Keyboard $(VERSION)"
	@echo "  make install   - Install for current user"
	@echo "  make release   - Build release packages"
	@echo "  make test      - Run tests"
	@echo "  make lint      - Run linter"
