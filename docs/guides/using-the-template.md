# Using this template

Steps to start a new project from this repository, in order.

## 1. Create your repository

On GitHub, click **Use this template** → **Create a new repository**. See GitHub's [guide to creating a repository from a template](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template).

## 2. Rename the package

The template's package is called `placeholder`. Rename it everywhere:

- the `placeholder/` folder;
- `pyproject.toml`: `name` (the name people `pip install`), `packages`, and the `version` line under `[tool.setuptools.dynamic]`;
- `placeholder/__init__.py` and `tests/test_version.py`, which import it.

Then update the links to this repository: `urls` in `pyproject.toml`, and `github` and `title` in `docs/myst.yml`.

## 3. Choose a license

`LICENSE` and the `license` field in `pyproject.toml` must name the same license. The template uses Apache-2.0; if you change it, change both.

## 4. Set up your environment

```bash
uv sync --extra dev        # or: pip install -e ".[dev]"
pre-commit install
pre-commit run --all-files
```

*Code Formatting & Linting* in the [Guidelines](guidelines.md) explains what the hooks do.

## 5. Add your dependencies

List them under `dependencies` in `pyproject.toml`, then run `uv lock` and commit `uv.lock` with the change. The `uv-lock` hook does this for you on commit.

## 6. Turn on CI and the docs site

- CI runs as soon as you push, but only if the repository is public: see *Continuous Integration* in the [Guidelines](guidelines.md).
- To publish this book, enable GitHub Pages once: see [Documentation with Jupyter Book](jupyter-book.md#publish).

## 7. Remove what you do not need

Delete `docs/contributed-examples/` or the docs workflow (`.github/workflows/docs.yml`) if your project has no use for them, and replace the README with your own.
