# Documentation with Jupyter Book

[Jupyter Book](https://jupyterbook.org) builds a website from Markdown ([MyST](https://mystmd.org/guide)) files and Jupyter notebooks.

This template uses Jupyter Book 2. The configuration is `docs/myst.yml`.

## Write

- Pages are Markdown files and notebooks in `docs/`; the landing page is `docs/index.md`.
- Add a page by creating the file in `docs/`: every page there is built and listed in the sidebar, in alphabetical order, with folders as sections. To choose the order, add a [`toc:`](https://mystmd.org/guide/table-of-contents) to `myst.yml`; pages not listed there are then not built.
- Images go in `docs/images/`.
- Notebooks (`.ipynb`) are pages like any other. They are shown with the outputs saved in them, not re-executed: [Figure 5 kinematics](../contributed-examples/MLAI/figure-5-kinematics.ipynb) is an example.

## Preview locally

```bash
uv sync --extra docs           # or: pip install -e ".[docs]"
cd docs && jupyter book start  # serves the book at http://localhost:3000 and reloads on save
```

Jupyter Book needs [Node.js](https://nodejs.org) 18 or later. If it is not installed, the first run offers to install a private copy.

## Publish

`.github/workflows/docs.yml` builds the book on every pull request, so a broken page fails the check. On every push to `main`, it also publishes the book to GitHub Pages, at `https://<organisation>.github.io/<repository>/`.

Before the first publication, enable Pages once: in the repository's **Settings → Pages**, set **Source** to **GitHub Actions**. See GitHub's [Pages documentation](https://docs.github.com/en/pages) and Jupyter Book's [deployment guide](https://mystmd.org/guide/deployment-github-pages).

Like the other workflows, it only runs on public repositories.

## Learn more

- [Jupyter Book documentation](https://jupyterbook.org): installing, building and publishing a book.
- [MyST guide](https://mystmd.org/guide): the Markdown flavour used by every page. Most useful sections:
  - [MyST Markdown quickstart](https://mystmd.org/guide/quickstart-myst-markdown)
  - [Typography](https://mystmd.org/guide/typography), [directives](https://mystmd.org/guide/directives) and [admonitions](https://mystmd.org/guide/admonitions)
  - [Cross-references](https://mystmd.org/guide/cross-references)
  - [Table of contents](https://mystmd.org/guide/table-of-contents), which is the `toc:` in `myst.yml`
  - [Notebooks](https://mystmd.org/guide/notebooks-with-markdown)
  - [Page frontmatter](https://mystmd.org/guide/frontmatter): title, authors, DOI and license shown at the top of a page
  - [Website themes](https://mystmd.org/guide/website-templates): the options used in `myst.yml` under `site:`
