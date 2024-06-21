.PHONY: app install dump dist

all: install dump dist

app:
ifdef name
	find . -type f -exec sed -i 's/a/$(name)/g' {} +
	$(MAKE) all
else
    @echo "Usage: make app name=<a>"
	@exit 1
endif


install:
	npm install

dump:
	npm run dump app

dist:
	npm run dist
