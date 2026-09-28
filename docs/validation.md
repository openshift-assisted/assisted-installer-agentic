# Validation

Validation checks the repository's package contracts, Markdown, links, and
static instruction quality. The [Makefile](../Makefile) defines two entry points:

```bash
skipper make validate
skipper make test
```

[Skipper](https://github.com/stratoscale/skipper) runs commands in the validation
container selected by [skipper.yaml](../skipper.yaml). The
[validation Dockerfile](../Dockerfile.assisted-installer-agentic-validation)
defines the tool versions used by that container. These development dependencies
are not needed to install or use the plugins.

## What each tool checks

`make validate` runs these checks in order and stops on failure:

| Tool | Purpose in this repository | Configuration or implementation |
| --- | --- | --- |
| Repository Python validator | Checks required skill frontmatter, names, matching manifests, marketplace coverage, local dependency registration, plugin link boundaries, and development-skill aliases. | [scripts/validate.py](../scripts/validate.py) |
| [markdownlint-cli2](https://github.com/DavidAnson/markdownlint-cli2) | Applies Markdown formatting rules, such as consistent headings, lists, and code fences. | [.markdownlint-cli2.yaml](../.markdownlint-cli2.yaml) |
| [Lychee](https://lychee.cli.rs/) | Checks local link targets and external URL availability. External checks require network access. | [.lychee.toml](../.lychee.toml) |
| [Skillsaw](https://github.com/stbenjam/skillsaw) | Adds static checks for skill and plugin structure, instruction quality, references, and suspicious content. | [.skillsaw.yaml](../.skillsaw.yaml) |

Markdownlint and Lychee cover repository Markdown, including `docs/`, and
explicitly include the development skills under `.agents/skills/`.
Markdownlint's configuration allows long lines, inline HTML, and files without
an initial top-level heading.

`make test` uses Python's [unittest](https://docs.python.org/3/library/unittest.html)
to exercise the repository validator, including regression cases and validation
of the current checkout. The [isolation tests](../scripts/test_isolation.py) also
copy each plugin to a temporary directory and check its package independently
of the checkout. Required dependencies remain separate plugins.

## Skillsaw policy

The configuration pins the rule version and extends content analysis to Markdown
under plugin skill directories, including operational references. Recognized
instruction files and applicable built-in rules are discovered automatically.

- Warnings and errors fail validation; informational findings remain advisory.
  Run `skillsaw lint --config .skillsaw.yaml --no-custom-rules --no-plugins --verbose .`
  in the validation environment to see informational details.
- MCP tool-name checks flag installation-specific identifiers in prose;
  repetitive tool-call examples are checked at informational severity.
- A directory mention alone does not count as referencing every bundled file.
- Plugin-level README files are not required by this repository's package contract.
- Custom Python rules and installed Skillsaw rule extensions are disabled by
  the Makefile flags. Validation of this repository's plugins remains enabled.

## CI and coverage limits

The [validation workflow](../.github/workflows/validate.yaml) builds the same
validation image and runs `make validate`. The
[test workflow](../.github/workflows/test.yaml) runs `make test` with Python 3.10.
Both run for pushes and pull requests targeting `main`.

Passing these checks establishes static consistency, not successful execution in
every host or correct task outcomes. Reviewers still need to assess skill
semantics, capability assumptions, and behavior on representative tasks. A
reachable external link also does not establish that its content is correct.
