# Project standards

Shared practices for SCENE code projects. The [template](using-the-template.md) sets up the core components.

## Core components

1. **Code Organization**

   * We recommend a clear folder structure for modules, tests and configuration, kept the same across projects where possible.

2. **Documentation**

   * [Jupyter Book](https://jupyterbook.org) setup for comprehensive, interactive project documentation, published to GitHub Pages: see [Documentation with Jupyter Book](jupyter-book.md).
   * Docstrings matter as much as the documentation pages: see these [guidelines for readable, maintainable docstrings](https://www.datacamp.com/tutorial/docstrings-python).

4. **Lockfiles**

```{attention}
**Please use and update an environment lockfile**: it records the exact version of every dependency, so others can rebuild your environment. The provided CI template fails if none of the files below is present; **keeping it up to date is up to you**.
```

   * Python: `uv.lock` (this template's default; `uv lock`, kept current by the `uv-lock` pre-commit hook), or `poetry.lock`, `pdm.lock`.
   * Conda environments, or mixed Python and other languages: `pixi.lock` ([pixi](https://pixi.sh)) or `conda-lock.yml` ([conda-lock](https://github.com/conda/conda-lock)).
   * R: `renv.lock` ([renv](https://rstudio.github.io/renv/)).
   * Julia: `Manifest.toml`.
   * JavaScript: `package-lock.json`. Rust: `Cargo.lock`.
   * Using another language? Add its lockfile to the check in `.github/workflows/lint.yml`.

5. **Code Formatting & Linting**

   * Consistently formatted code is easier to read and review. [Ruff](https://docs.astral.sh/ruff/) formats the code and checks it for likely bugs; its settings are under `[tool.ruff]` in `pyproject.toml`.
   * [Pre-commit](https://pre-commit.com/) runs Ruff and a few other checks (spelling, whitespace, YAML/TOML validity, an up-to-date `uv.lock`), configured in `.pre-commit-config.yaml`. CI runs the same hooks without fixing anything, so a commit that passes locally passes in CI.
     * Many pre-made hooks exist for other purposes; they save time by automating repetitive tasks and catching failures early.
     * Keep in mind they are code running on all files you commit, so make sure to install only trusted hooks and review their configuration.
   * **Set up**, once per clone:

     ```bash
     pip install -e ".[dev]"   # or: uv sync --extra dev
     pre-commit install
     ```

   * **When you commit**, the hooks run on the files in that commit and automatically fix what they can. If a hook changes a file, the commit is blocked: review the change and stage/commit again.
   * **First run on existing code**, or after changing `.pre-commit-config.yaml`: commits only check the files they touch, so run `pre-commit run --all-files` once to bring every file in line. Expect a large diff the first time; commit it on its own.

6. **Continuous Integration**

   * SCENE projects use GitHub Actions for automated tests and code-quality checks.
   * The workflows only run on public repositories: on a private one, runs draw on SCENE-Collaboration's Actions quota, which can be billed. To run them on a private repository anyway, delete the `if: ${{ !github.event.repository.private }}` line in each workflow, **after checking with the owners**.
   * This template runs two workflows on every pull request and every push to `main`, with no other setup:
     * **Lint** (`.github/workflows/lint.yml`): the pre-commit hooks above, check-only, and a check that a lockfile is committed.
     * **Tests** (`.github/workflows/tests.yml`): `pytest` on Linux (Python 3.10 and 3.13) and Windows (Python 3.13).
   * Results appear as checks at the bottom of each pull request, and under the repository's **Actions** tab. A red check links to the log of the failing step: see [using workflow run logs](https://docs.github.com/en/actions/how-tos/monitor-workflows/use-workflow-run-logs).
   * To make your own, see: GitHub's [quickstart](https://docs.github.com/en/actions/get-started/quickstart), the [Python tutorial](https://docs.github.com/en/actions/tutorials/build-and-test-code/python) and the [workflow syntax reference](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax).



## Advanced topics

1. **Containerization**

   * [Docker](https://docs.docker.com/get-started/) gives everyone the same environment to develop, run and share code in. We recommend setting it up from the start of a project, not at the end.

2. **Data Workflow Integration**

   * [DataJoint](https://www.datajoint.com/) manages and queries scientific data pipelines. Use it at least to store data and metadata, and to automate routine steps such as preprocessing or running DeepLabCut.
   * SCENE projects will be required to use the collaboration's shared DataJoint schemas, [SCENE-pipelines](https://github.com/SCENE-Collaboration/SCENE-pipelines): the tables for labs, subjects, sessions and their provenance, used across all labs.
   * [DataJoint Elements](https://docs.datajoint.com/elements/) provides templates for common workflows and schema management.
     * Note: the DeepLabCut workflow there is currently out of date; the team is updating it.
