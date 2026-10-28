# Development guide

Each project sets its own rules, such as who reviews what and how decisions are made.
The guidelines below are a suggested common starting point.

## When writing code

(git-workflow)=
### Git workflow

- Use a branch per change, named `name/issue-number-description`, e.g. `john/123-add-login-feature`.
- Keep branches up to date with `main`, and delete them after merging.
- Write commits that each do one thing, with a clear message; reference the issue number.

### Recommended code style

Formatting and linting are enforced by Ruff, configured under `[tool.ruff]` in `pyproject.toml`: see *Code Formatting & Linting* in the [Project standards](guidelines.md). Ruff does not check names, so follow Python's conventions ([PEP 8](https://peps.python.org/pep-0008/#naming-conventions)):

- variables, functions, modules and files: `lower_snake_case`;
- classes: `PascalCase`;
- constants: `UPPER_SNAKE_CASE`;
- private members: `_single_leading_underscore`.

For docstrings, follow the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings).

## When sharing code

Use the following GitHub-provided features to share and discuss code effectively:

### Issues

A good issue has:

- A clear, descriptive title
- For a bug: steps to reproduce, expected and actual behaviour, and environment details (OS, Python and package versions)
- For a feature: the use case it serves, alternate approaches considered
- Screenshots or videos when relevant

Keep the discussion in the issue thread, so decisions stay findable.

### Pull requests

Before opening one:

- Work on a branch named `name/issue-number-description` (see [](#git-workflow))
- Self-review your changes
- Run the tests locally (`uv run pytest` or `pytest`)
- Make sure the pre-commit hooks pass; once installed, they run on every commit
- Update the documentation
- Keep the change focused: open the smallest pull request that is useful on its own, one you would want to review yourself

The description gives a clear title, what changed and why, links to related issues, how to test it, and any useful data: benchmark plots, UI changes, or other relevant information.

### Code review

Focus on the code: give clear, actionable feedback, and explain the reason behind each suggestion.

Check that:

- The pre-commit checks and CI pass (formatting and linting are Ruff's job, not the reviewer's)
- Tests are included for the change
- Error handling is appropriate
- Performance is considered where it matters
- The documentation is updated
