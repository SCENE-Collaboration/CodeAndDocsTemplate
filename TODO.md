# TODO

Open work and open decisions for this repository.

## Work

- **CI on this repository:** its workflows skip private repositories, like those of generated projects. If the new repository is private, delete the `if:` lines in `.github/workflows/` here; the skeleton's keep them.
- **Review and test pass:** `pytest` on Windows and Linux with `SCENE_TEMPLATE_E2E=1`, `pre-commit run --all-files --hook-stage manual`, a strict book build with link checking, `actionlint` and `zizmor` on `.github/` and the skeleton's `dot-github/`, the interactive prompts by hand, and every page checked in light and dark mode.
- **Landing page typo:** "for more other repositories" in `docs/index.md`.

## Decisions

- **New repository:** this work moves to a new SCENE repository; its name and visibility are open. After the move, update the repository links in `pyproject.toml` (`urls`), `docs/myst.yml` (`github`) and the `uvx --from` command in `docs/guides/using-the-template.md`. `uvx --from git+https://…` works without credentials only on a public repository. Do not mark it as a GitHub template repository: projects come from the generator.
- **Footer funder line:** "Simons Foundation" now; SCENE's own wording is "supported by a Simons Foundation International grant administered by the Simons Foundation".
- **MLAI example headers:** authors are given as initials (C. Benquet, T. Sainsbury); the permission line has no date.
