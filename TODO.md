# TODO

Open work and open decisions for this repository.

## Work

- **MkDocs backend for the generator:** `src/scene_repo_template/skeleton/mkdocs/`, from the prototype on `cy/scene-docs-mkdocs` (worktree `../CodeAndDocsTemplate-mkdocs`, `api-docs/` uncommitted). It writes `docs/`, with its own docs extra (`docs_dependencies`), docs workflow and SCENE stylesheet from `scene-palette.json`; add it to `BACKENDS` in `cli.py` and to the end-to-end docs test. The logo and favicon are in `skeleton/jupyter-book/docs/images/` because `footer.md` links them relatively; move them to `common/` only if both backends can reach them there.
- **CI on this repository:** its workflows skip private repositories, like those of generated projects. If the new repository is private, delete the `if:` lines in `.github/workflows/` here; the skeleton's keep them.
- **Review and test pass:** `pytest` on Windows and Linux with `SCENE_TEMPLATE_E2E=1`, `pre-commit run --all-files --hook-stage manual`, a strict book build with link checking, `actionlint` and `zizmor` on `.github/` and the skeleton's `dot-github/`, the interactive prompts by hand, and every page checked in light and dark mode.

## Decisions

- **New repository:** this work moves to a new SCENE repository; its name and visibility are open. After the move, update the repository links in `pyproject.toml` (`urls`), `docs/myst.yml` (`github`) and the `uvx --from` command in `docs/guides/using-the-template.md`. `uvx --from git+https://…` works without credentials only on a public repository. Do not mark it as a GitHub template repository: projects come from the generator.
- **Footer funder line:** "Simons Foundation" now; SCENE's own wording is "supported by a Simons Foundation International grant administered by the Simons Foundation".
- **MLAI example headers:** authors are given as initials (C. Benquet, T. Sainsbury); the permission line has no date.
