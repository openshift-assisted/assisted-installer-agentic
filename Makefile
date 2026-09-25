.PHONY: validate test

validate:
	@printf '=== Python validation ===\n'
	python3 scripts/validate.py
	@printf '\n=== Markdown lint ===\n'
	markdownlint-cli2 '**/*.md' '.agents/skills/**/*.md'
	@printf '\n=== Link checks ===\n'
	lychee --config .lychee.toml '**/*.md' '.agents/skills/**/*.md'

test:
	python3 -m unittest discover -s scripts -p 'test_*.py' -v
