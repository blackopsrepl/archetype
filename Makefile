SHELL := /bin/bash
.PHONY: help config run alpha beta minor release

help:
	@echo "Makefile Commands:"
	@echo "  config               - Set up the virtual environment."
	@echo "  run                  - Launch un 'archetype' locally."
	@echo "  alpha                - Generate changelog and create an alpha tag."
	@echo "  beta                - Generate changelog and create an alpha tag."
	@echo "  minor                - Generate changelog and create an beta tag."
	@echo "  release              - Generate changelog and create a release tag."

all: clean config install

config:
	@echo "Creating environment..."
	@if [ -d .venv ]; then \
		echo "A virtual environment already exists in .venv. Please double-check."; \
	else \
		echo "Setting up the virtual environment..."; \
		python3.11 -m venv .venv; \
		echo "Activating the virtual environment..."; \
		source .venv/bin/activate; \
		echo "Installing required packages..."; \
		pip3 install -r src/requirements.txt --require-virtualenv --no-input; \
	fi
	@echo ""

run:


alpha:
	@echo "Generating changelog and tag..."
	@commit-and-tag-version --prerelease alpha

beta:
	@echo "Generating changelog and tag..."
	@commit-and-tag-version --prerelease beta

minor:
	@echo "Generating changelog and tag..."
	@commit-and-tag-version --release-as minor

release:
	@echo "Generating changelog and tag..."
	@commit-and-tag-version
