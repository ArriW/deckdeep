.PHONY: test
test:
	act -P ubuntu-latest=catthehacker/ubuntu:act-latest -W .github/workflows/python-tests.yml --env PIP_ROOT_USER_ACTION=ignore

.PHONY: run
run:
	python -m deckdeep.main

.PHONY: run-fresh
run-fresh:
	rm -f save_game.json
	python -m deckdeep.main

.PHONY: format
format:
	black ./tests ./deckdeep ./scripts

.PHONY: lint
lint:
	flake8 ./tests ./deckdeep ./scripts

.PHONY: mypy
mypy:
	mypy --no-error-summary ./tests ./deckdeep ./scripts

.PHONY: test-all
test-all: test format lint mypy

.PHONY: update-docs
update-docs:
	python scripts/generate_keybind_docs.py
	@echo "Updating README.md with new keybind documentation..."
	@sed -i.bak '/^## Controls/,/^## Project Structure/d' README.md
	@cat keybind_docs.md >> README.md
	@rm keybind_docs.md README.md.bak
	@echo "Documentation updated successfully."