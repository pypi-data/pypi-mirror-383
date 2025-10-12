# mdxlate

Translate Markdown docs into multiple languages using LLMs.  
Batteries included: prompt template, CLI, OpenAI/OpenRouter provider switch, and a simple change-detection cache.

## 📚 Documentation

**[Read the full documentation →](docs/)**

- **[Getting Started](docs/index.md)** – Installation and quick start
- **[CLI Reference](docs/cli.md)** – Complete command-line guide
- **[Programmatic Usage](docs/programmatic.md)** – Python API and examples
- **[Caching System](docs/caching.md)** – How the cache works
- **[Custom Prompt](docs/custom-prompt.md)** – Customize translations
- **[Error Handling](docs/error-handling.md)** – Failure recovery
- **[Development Guide](docs/development.md)** – Contributing
- **[FAQ](docs/faq.md)** – Troubleshooting

## Install
```bash
pip install -e .
````

## Quick start

1. Initialize the editable prompt (creates `~/.mdxlate/translation_instruction.txt`):

```bash
mdx init
```

2. Run translations:

```bash
export OPENAI_API_KEY=sk-...   # or use OPEN_ROUTER_API_KEY when provider=openrouter
mdx run docs_src out --languages de fr --model gpt-4o-mini
```

Result: translated files under `out/<lang>/...`, preserving the original folder structure.
A cache file `.mdxlate.hashes.json` is written in `docs_src`.

## CLI

```bash
mdx run [OPTIONS] DOCS_SRC OUT_DIR
```

**Options**

* `--base-language TEXT` – Base language (default: `en`)
* `--languages TEXT...` – Target languages, space-separated (default: `de`)
* `--model TEXT` – Model name (default: `gpt-4o-mini`)
* `--provider [openai|openrouter]` – Backend provider (default: `openai`)
* `--api-key TEXT` – API key (overrides env)
* `--api-env-key TEXT` – Env var to read (default: `OPENAI_API_KEY`)
* `--base-url TEXT` – Custom base URL (e.g., OpenRouter)
* `--prompt-path PATH` – Use a custom prompt file instead of the default
* `--force` – Force re-translation, bypassing cache
* `--cache-dir PATH` – Directory for cache file (defaults to source directory)

## Examples

OpenAI (env var):

```bash
export OPENAI_API_KEY=sk-...
mdx run docs_src out --languages de fr --model gpt-4o-mini
```

OpenRouter:

```bash
export OPEN_ROUTER_API_KEY=or-...
mdx run docs_src out --languages de --provider openrouter --model google/gemini-2.5-pro
```

Custom prompt:

```bash
mdx run docs_src out --languages de --prompt-path ./my_prompt.txt
```

Custom cache directory (for read-only CI/CD):

```bash
mdx run docs_src out --languages de --cache-dir /tmp
```

## Error Handling

If any file fails to translate (e.g., due to API errors, rate limits, or network issues), mdxlate will:

1. **Continue processing** other files instead of crashing
2. **Save the cache** for successful translations
3. **Generate a failure report** at `.mdxlate.failures.json` with details about what failed

Example failure report:
```json
{
  "failures": [
    {
      "file": "docs/advanced.md",
      "error": "Rate limit exceeded",
      "error_type": "RateLimitError"
    }
  ]
}
```

After fixing the issue (e.g., waiting for rate limits to reset), re-run the translation. Only failed files will be retried thanks to the cache.

## Behavior

* **Prompt:** default lives at `~/.mdxlate/translation_instruction.txt` (created by `mdx init`). You can edit it freely or pass `--prompt-path`.
* **Cache:** re-translation is skipped if *file bytes + prompt content + model + language* are unchanged. By default, cache is written to source directory as `.mdxlate.hashes.json`. Use `--cache-dir` for read-only environments.
* **Structure:** each language gets its own mirror tree under `OUT_DIR/<lang>/`.

## Programmatic use

```python
from pathlib import Path
from mdxlate.start_translation import start_translation

start_translation(
    docs_src=Path("docs_src"),
    out_dir=Path("out"),
    base_language="en",
    languages=["de", "fr"],
    model="gpt-4o-mini",
    provider="openai",  # or "openrouter"
    api_key=None,       # pass explicitly or rely on env
    base_url=None,
    prompt_path=None,
    cache_dir=None,     # optional: specify custom cache directory
)
```

## Integrations

* **[Jekyll](docs/integrations/jekyll.md)** – Complete guide for translating Jekyll sites with frontmatter preservation

## Files of interest

* `mdxlate/cli.py` – Typer CLI (`mdx init`, `mdx run`)
* `mdxlate/client.py` – `make_client()` factory (OpenAI/OpenRouter)
* `mdxlate/translator.py` – translation, hashing, and I/O
* `mdxlate/translation_instruction.txt` – default prompt template

## Development

### Setup

```bash
pip install -e .
pip install ruff mypy pytest
```

### Code Quality

This project uses **Ruff** for linting and formatting, and **Mypy** for type checking:

```bash
# Lint code
ruff check src tests

# Auto-fix linting issues
ruff check --fix src tests

# Format code
ruff format src tests

# Type check
mypy src --ignore-missing-imports

# Run tests
pytest tests/
```

### CI/CD

The `.github/workflows/quality.yml` workflow runs automatically on every push and PR:
- ✅ Ruff linting
- ✅ Ruff formatting check
- ✅ Mypy type checking

## License

MIT

## Layout

```
repo/
  pyproject.toml
  README.md
  src/
    mdxlate/
      __init__.py
      cli.py
      client.py
      translator.py
      start_translation.py
      translation_instruction.txt
  tests/            # optional
  main.py           # optional local test runner
```

````

---

# pyproject.toml
```toml
[build-system]
requires = ["setuptools>=69", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "mdxlate"
version = "0.1.0"
description = "Translate Markdown docs into multiple languages using LLMs."
readme = "README.md"
requires-python = ">=3.10"
license = { text = "MIT" }
authors = [{ name = "Tobias Bück" }]
dependencies = [
  "typer>=0.12",
  "openai>=1.40",
  "tenacity>=8.2",
]

[project.scripts]
mdx = "mdxlate.cli:app"

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]
include = ["mdxlate*"]

[tool.setuptools.package-data]
mdxlate = ["translation_instruction.txt"]

[tool.pytest.ini_options]
addopts = "-q"
testpaths = ["tests"]
