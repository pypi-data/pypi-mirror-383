SHELL := bash -eu -o pipefail
MAKEFLAGS += --warn-undefined-variable
VERSION := $(shell uv version --short)

.PHONY: build clean

requirements.txt: uv.lock
	uv export --no-default-groups --no-emit-local --locked -o $@

dist/stax-$(VERSION)-py3-none-any.whl: requirements.txt
	uv build --wheel

build: requirements.txt dist/stax-$(VERSION)-py3-none-any.whl
	docker build --build-arg VERSION=$(VERSION) -t stax .

clean:
	rm -rf requirements.txt dist
