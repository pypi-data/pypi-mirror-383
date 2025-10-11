install:
	uv sync

lint:
	uv run ruff check back_channel_client/

format:
	uv run ruff format back_channel_client/

check-format:
	uv run ruff format --check back_channel_client/

.PHONY: build
build:
	uv build

publish:
	uv publish