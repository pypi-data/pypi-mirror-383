# Frets on Fire helper targets

PLATFORM := $(shell uname)

.PHONY: build python-package linux-packages windows-packages mac-packages dist clean release

ifeq ($(findstring Windows_NT,$(OS)),Windows_NT)
# Windows hosts
build: windows-packages

windows-packages:
	briefcase build windows --target exe --update
	briefcase package windows --target exe --update
else ifneq (,$(findstring Linux,$(PLATFORM)))
# Linux hosts
build: python-package linux-packages

python-package:
	python -m build

linux-packages:
	briefcase build linux --target debian --update
	briefcase package linux --target debian --update
	briefcase package linux --target fedora --update
        briefcase build linux flatpak
        briefcase package linux flatpak
else ifeq ($(PLATFORM),Darwin)
# macOS hosts
build: mac-packages

mac-packages:
	briefcase build macOS --target dmg --update
	briefcase package macOS --target dmg --update
else
build:
	@echo "Unsupported platform: $(PLATFORM)"
endif

dist: build

clean:
	rm -rf build dist

release:
	python -m pip install --upgrade pip build twine
	python -m build
	twine upload dist/*.whl dist/*.tar.gz
