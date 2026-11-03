# TODO

Open work and open decisions for this template.

## Work

- **Project generator** (`scripts/new_project.py`, stdlib only):
  - copies an explicit allowlist of template files, never the contributed examples;
  - renames `placeholder` everywhere `docs/guides/using-the-template.md` lists;
  - asks which docs backend to keep: Jupyter Book (`docs/myst.yml`) or MkDocs (`api-docs/`, branch `cy/scene-docs-mkdocs`);
  - has tests in `tests/`, run by `tests.yml` on Linux and Windows;
  - then: rewrite `docs/guides/using-the-template.md` around it, and restore the README's directory tree, generated from its allowlist.
- **CI on the template itself:** run the workflows on the template repository whatever its visibility, with `if: ${{ github.event.repository.is_template || !github.event.repository.private }}`, so repositories created from it keep the public-only rule. Check in a real run that `is_template` is set in the event payload.
- **Review and test pass:** `pytest` on Windows and Linux, `pre-commit run --all-files --hook-stage manual`, a strict book build with link checking, `actionlint` and `zizmor`, the generator end to end (generate, lock, install, test, build the docs), and every page checked in light and dark mode.

## Decisions

- **Host the MkDocs API site next to the Jupyter Book?** One Pages site per repository, so both builds would go into one artifact (book at `/`, MkDocs under `/api/`): one more step in `.github/workflows/docs.yml`, a second toolchain in `uv.lock`, two themes to keep alike. Decide once the generator offers the MkDocs option, so its output can be shown.
- **New repository:** this work moves to a new SCENE repository; its name and visibility are open. After the move, update the repository links in `pyproject.toml` (`urls`) and `docs/myst.yml` (`github`), and in `api-docs/mkdocs.yml` if kept.
- **Footer funder line:** "Simons Foundation" now; SCENE's own wording is "supported by a Simons Foundation International grant administered by the Simons Foundation".
- **MLAI example headers:** authors are given as initials (C. Benquet, T. Sainsbury); the permission line has no date.
