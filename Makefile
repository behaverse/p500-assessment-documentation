.PHONY: help build serve dist clean

help:
	@echo "Targets:"
	@echo "  build  - regenerate engines.json and timeline pages from source data"
	@echo "  serve  - run a local dev server at http://localhost:8000 (uses webapp/content symlink)"
	@echo "  dist   - produce a deployable directory at ./dist with content copied (no symlink)"
	@echo "  clean  - remove the dist/ directory"

build:
	python3 scripts/build/excel_extractor.py
	python3 scripts/generation/generate_timelines.py

serve:
	cd webapp && python3 -m http.server 8000

dist:
	rm -rf dist
	cp -r webapp dist
	rm dist/content
	mkdir -p dist/content
	cp -r content/engines.json content/en.yaml content/timeline_configs content/images content/OrderedClicks dist/content/

clean:
	rm -rf dist
