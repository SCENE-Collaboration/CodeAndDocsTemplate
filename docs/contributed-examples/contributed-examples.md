# Contributed examples

Pages contributed by SCENE labs, taken from their own documentation or analyses. Each one shows real research code and figures in this book's format.

:::{toc}
:context: children
:::

## Required header

Please start every contributed example with the header below.

- **Frontmatter**, at the very top of the file, or of the first Markdown cell for a notebook. The book shows the authors, venue, DOI and license in the page's title block.
- **A `Contributed example` box**, right under the frontmatter, naming the source and the publication in full.

Copy this into the new page and fill in every field:

````markdown
---
title: <Page title>
authors:
  - name: <Author name>
    affiliations:
      - <Lab, institution>
venue: <Journal or preprint server>
doi: <DOI of the publication>
license: <SPDX identifier of the original material's license, e.g. MIT; leave the line out if it has none>
github: <Repository the material comes from>
source_url: <Exact page or file it was adapted from>
---

:::{admonition} Contributed example
:class: note

- **Lab:** <Lab, institution>
- **Source:** [<repository / page>](<link to the original page or file>)
- **Publication:** <Authors> (<year>). <Title>. *<Venue>*. [doi:<DOI>](https://doi.org/<DOI>)
- **Permission:** <Who agreed to its reuse here, and when>
- **Changes:** <What was changed from the original, or "none">
:::
````

## Adding an example

1. Get the lab's agreement to reuse the material, and check its license. If the source repository has no license file, its content may not be reused without explicit permission.
2. Create the page in the lab's folder, `docs/contributed-examples/<lab>/` (e.g. `docs/contributed-examples/MLAI/`), starting with the header above.
3. Put its images in `docs/contributed-examples/<lab>/images/`. Keep notebooks small: every embedded plot adds to the repository's size, so keep only the cells the example needs.
4. List the page under this one in `docs/myst.yml`.
