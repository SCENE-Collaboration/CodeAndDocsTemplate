# TODO

Open work and open decisions for this repository.

## Work

- **CI on this repository:** its workflows skip private repositories, like those of generated projects. If the new repository is private, delete the `if:` lines in `.github/workflows/` here; the skeleton's keep them.
- **Review and test pass, what is left:** the interactive prompts by hand (the `questionary` path has no tests), and every page of the book and of a generated MkDocs site checked in light and dark mode. Done on 2026-10-28: `pytest` with `SCENE_TEMPLATE_E2E=1` on Windows and the Linux break cases in WSL, `pre-commit run --hook-stage manual`, a strict book build, `actionlint` and `zizmor` (no findings) on `.github/` and the skeleton's `dot-github/`.

## Decisions

- **New repository:** this work moves to a new SCENE repository; its name and visibility are open. After the move, update the repository links in `pyproject.toml` (`urls`), `docs/myst.yml` (`github`) and `docs/guides/using-the-template.md` (uv, pip and conda tabs). Installing from `git+https://…` works without credentials only on a public repository. Do not mark it as a GitHub template repository: projects come from the generator.
- **Broken links** (`jupyter book build --strict --check-links` fails on them):
  - `guides/guidelines.md`: the DataCamp docstrings tutorial returns 403 to the link checker; `SCENE-Collaboration/SCENE-pipelines` returns 404 (private, or not created yet).
  - `contributed-examples/MLAI/datajoint-architecture.md`: `https://docs.datajoint.org/` does not resolve and `github.com/datajoint/datajoint` returns 404. The page is kept as published, so a fix belongs in its "Changes" field.
- **Footer funder line:** "Simons Foundation" now, in the skeleton's `jupyter-book/docs/_static/footer.md` and in the `copyright` of `mkdocs/mkdocs.yml.tmpl`; SCENE's own wording is "supported by a Simons Foundation International grant administered by the Simons Foundation".
- **MLAI example headers:** authors are given as initials (C. Benquet, T. Sainsbury); the permission line has no date.
