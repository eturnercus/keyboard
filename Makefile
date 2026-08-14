.PHONY: install uninstall test lint release clean flatpak snap deb appimage appimage-cpp

PREFIX ?= /usr/local
VERSION := $(shell python3 -c "from touchflow import __version__; print(__version__)")

install:
	bash scripts/install.sh

uninstall:
	bash scripts/uninstall.sh -y

test:
	python3 -m pytest tests/ -v

lint:
	ruff check touchflow touchflow_settings 2>/dev/null || true

release:
	bash scripts/build-release.sh

flatpak:
	bash scripts/build-flatpak.sh

snap:
	bash scripts/build-snap.sh

deb:
	bash scripts/build-deb.sh

appimage:
	bash scripts/build-appimage.sh

appimage-cpp:
	bash scripts/build-appimage-cpp.sh

appimage-uninstall:
	bash scripts/build-appimage-uninstall.sh

appimage-all: appimage appimage-cpp appimage-uninstall

clean:
	rm -rf dist build *.egg-info .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

.PHONY: help
help:
	@echo "TouchFlow Keyboard $(VERSION)"
	@echo "  make install   - Install for current user"
	@echo "  make appimage-cpp - Build C++ experimental AppImage installer"
	@echo "  make test      - Run tests"
	@echo "  make lint      - Run linter"
