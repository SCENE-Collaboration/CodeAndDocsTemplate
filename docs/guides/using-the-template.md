# Using this template

`scene-repo-template` creates a new project with packaging, tests, CI and a documentation site already set up.

It works with uv, pip or conda; it needs Python 3.10 or later and [git](https://git-scm.com/downloads).

## 1. Create the project

::::{tab-set}

:::{tab-item} uv

```bash
uvx --from git+https://github.com/SCENE-Collaboration/CodeAndDocsTemplate scene-repo-template new my-project
```

`uvx` runs the generator without installing it. See [installing uv](https://docs.astral.sh/uv/getting-started/installation/).
:::

:::{tab-item} pip
In any Python environment:

```bash
pip install git+https://github.com/SCENE-Collaboration/CodeAndDocsTemplate
scene-repo-template new my-project
```

:::

:::{tab-item} conda
The generator is installed with pip, into a conda environment of its own:

```bash
conda create -n scene-tools python pip
conda activate scene-tools
pip install git+https://github.com/SCENE-Collaboration/CodeAndDocsTemplate
scene-repo-template new my-project
```

:::

::::

You will need to enter:
- The distribution name (for `pip install`)
- The import name
- The project title
- A one-line description
- The author
- The GitHub URL

This will show a summary, and wait for confirmation.

```{note}
Use `--dry-run` for a preview.
```


The project then contains:

- `pyproject.toml`, the package folder and a first test example in `tests/`;
- `.pre-commit-config.yaml` and three GitHub Actions workflows: lint, tests and docs;
- `docs/`, a Jupyter Book with SCENE's logo, colours and footer;
- `LICENSE` (Apache-2.0) and a short `README.md`.

## 2. Set up your environment

In the new project, with your preferred package manager:

::::{tab-set}

:::{tab-item} uv

```bash
cd my-project
git init
uv sync --extra dev
uv run pre-commit install
uv run pytest
```

:::

:::{tab-item} pip

```bash
cd my-project
git init
python3 -m venv .venv          # Windows: py -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pre-commit install
pytest
```

On Ubuntu and Debian, `python3 -m venv` needs the `python3-venv` package (`sudo apt install python3-venv`).

:::

:::{tab-item} conda

```bash
cd my-project
git init
conda create -n my-project python pip
conda activate my-project
pip install -e ".[dev]"
pre-commit install
pytest
```

Install packages that only exist on conda (or that you prefer from conda-forge) with `conda install`, before `pip install -e`.
:::

::::

`pip install -e` installs the package in editable mode: changes to its code take effect without reinstalling.
See *Code Formatting & Linting* in the [Project standards](guidelines.md) for an explanation of the hooks.

## 3. Choose a license

Projects start with Apache-2.0.
To change it, replace `LICENSE` and update every place that names the license:

- the `license` field in `pyproject.toml`;
- the *License* section of `README.md`;
- `license` in `docs/myst.yml`.

## 4. Add your dependencies

List them under `dependencies` in `pyproject.toml`, then reinstall (`uv sync --extra dev`, or `pip install -e ".[dev]"`).

The `uv-lock` pre-commit hook writes `uv.lock` on every commit that changes `pyproject.toml`, also for pip and conda users.
Commit `uv.lock` with the change.

```{note}
`uv.lock` covers only `pyproject.toml`: record conda-only packages in a separate lockfile, see *Lockfiles* in the [Project standards](guidelines.md).
```

## 5. Turn on CI and the docs site

- Create the repository on GitHub at the URL you decided, then commit and push.
- CI runs as soon as you push, if the repository is public and Actions is enabled (**Settings → Actions**): see *Continuous Integration* in the [Project standards](guidelines.md).
- To publish the docs, enable GitHub Pages once: see [Documentation with Jupyter Book](jupyter-book.md#publish).

```{important}
No docs needed? Delete `docs/` and `.github/workflows/docs.yml`.
```
