"""Create a SCENE code project from the skeleton: ``scene-repo-template new``."""

from __future__ import annotations

import argparse
import functools
import keyword
import re
import subprocess
import sys
import unicodedata
import urllib.parse
from collections.abc import Callable
from pathlib import Path
from string import Template

SKELETON = Path(__file__).parent / "skeleton"

BACKENDS = {
    "jupyter-book": {
        "label": "Jupyter Book: guides and notebooks",
        "docs_dependencies": '"jupyter-book>=2"',
        "docs_readme": (
            "Built from `docs/` with [Jupyter Book](https://jupyterbook.org): "
            'after `pip install -e ".[docs]"` (or `uv sync --extra docs`), `jupyter book start` in `docs/` serves it '
            "locally. "
            "`.github/workflows/docs.yml` publishes it to GitHub Pages once Pages is enabled with GitHub Actions as its source."
        ),
    },
}

TEMPLATE_SUFFIX = ".tmpl"
DOT_PREFIX = "dot-"  # dot-github -> .github: hidden files would be skipped by package-data globs
PACKAGE_DIR = "__package__"  # renamed to the import name

# Used with fullmatch: `$` would accept a trailing newline
DIST_NAME = re.compile(r"[A-Za-z0-9]([A-Za-z0-9._-]*[A-Za-z0-9])?")
PACKAGE = re.compile(r"[a-z_][a-z0-9_]*")
# Folders every project ships with
# Otherwise a package of the same name would merge into them.
RESERVED_PACKAGES = {"docs", "tests"}
UNQUOTABLE = re.compile(r'["\\\x00-\x08\x0a-\x1f\x7f]')

Check = Callable[[str], "str | None"]


class ProjectError(ValueError):
    """Invalid or missing answer."""


@functools.cache
def gitignored_names() -> frozenset[str]:
    """Import names the generated .gitignore excludes as folders (build/, lib/, env/, ...)."""
    lines = (SKELETON / "common" / f"{DOT_PREFIX}gitignore").read_text(encoding="utf-8").splitlines()
    return frozenset(name for line in lines if PACKAGE.fullmatch(name := line.strip().strip("/")))


def canonical_name(dist_name: str) -> str:
    """PEP 503 form, so `Pre_Commit` and `pre-commit` compare equal."""
    return re.sub(r"[-_.]+", "-", dist_name).lower()


def requirement_names(requirements: str) -> set[str]:
    """Canonical distribution names in a list of quoted requirements: `"pytest>=8", "mkdocstrings[python]"`."""
    return {canonical_name(name) for name in re.findall(r'"([A-Za-z0-9._-]+)', requirements)}


@functools.cache
def dev_distributions() -> frozenset[str]:
    """The generated project's dev extra (pre-commit, pytest, ...), read from its pyproject."""
    text = (SKELETON / "common" / f"pyproject.toml{TEMPLATE_SUFFIX}").read_text(encoding="utf-8")
    return frozenset(
        requirement_names(re.search(r"^optional-dependencies\.dev = \[(.*)\]$", text, re.MULTILINE).group(1))
    )


@functools.cache
def dev_tool_names() -> frozenset[str]:
    """Import names of the dev extra (pytest, pre_commit, ...)."""
    return frozenset(name.replace("-", "_") for name in dev_distributions())


@functools.cache
def toolchain_distributions() -> frozenset[str]:
    """Every distribution the generated extras depend on: dev, and docs for each backend."""
    docs = set().union(*(requirement_names(backend["docs_dependencies"]) for backend in BACKENDS.values()))
    return dev_distributions() | docs


def check_dist_name(value: str) -> str | None:
    if not DIST_NAME.fullmatch(value):
        return "use letters, digits, '-', '_' or '.', starting and ending with a letter or digit"
    if canonical_name(value) in toolchain_distributions():
        return f"{value} is one of the project's own dependencies; the project would depend on itself"
    return None


def check_package(value: str) -> str | None:
    if not PACKAGE.fullmatch(value) or keyword.iskeyword(value):
        return "use a lowercase Python identifier, e.g. my_project"
    if value in sys.stdlib_module_names:
        return f"{value} is a standard-library module; importing it would not reach your package"
    if value in RESERVED_PACKAGES:
        return f"{value}/ is already a folder of the project"
    if value in gitignored_names():
        return f"{value}/ is in the project's .gitignore, so the code would not be committed"
    if value in dev_tool_names():
        return f"{value} is one of the project's dev tools; a package of that name would shadow it"
    return None


def check_text(value: str) -> str | None:
    if not value.strip():
        return "must not be empty"
    if UNQUOTABLE.search(value):
        return 'must be one line, without " or \\ or control characters'
    return None


def check_url(value: str) -> str | None:
    if not value.startswith(("https://", "http://")) or " " in value or UNQUOTABLE.search(value):
        return "must be an http(s) URL"
    if not urllib.parse.urlsplit(value).hostname:
        return "must be an http(s) URL with a host, e.g. https://github.com/lab/project"
    return None


def check_dest(value: str) -> str | None:
    if not value:
        return "required"
    path = Path(value)
    if path.exists() and (not path.is_dir() or any(path.iterdir())):
        return f"{path} exists and is not an empty folder"
    return None


def default_dist_name(folder: str) -> str:
    """`My Projét` -> `My-Projet`: accents dropped, other invalid characters replaced with `-`."""
    ascii_name = unicodedata.normalize("NFKD", folder).encode("ascii", "ignore").decode()
    name = re.sub(r"[^A-Za-z0-9._-]+", "-", ascii_name).strip("-._")
    return name if check_dist_name(name) is None else "project"


def default_package(dist_name: str) -> str:
    package = re.sub(r"[^a-z0-9_]", "_", dist_name.lower()).lstrip("0123456789_")
    return package if check_package(package) is None else "project"


def git_user_name() -> str:
    try:
        result = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True, check=False)
    except OSError:
        return ""
    return result.stdout.strip()


def output_name(part: str, package: str) -> str:
    if part == PACKAGE_DIR:
        return package
    if part.startswith(DOT_PREFIX):
        return "." + part[len(DOT_PREFIX) :]
    return part


def text_or_none(data: bytes) -> str | None:
    if b"\0" in data:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def generate(dest: Path, values: dict[str, str], backend: str, dry_run: bool = False) -> list[Path]:
    """Copy `common/`, then the backend's folder, into `dest`; render `.tmpl` files with `values`.

    Text files are written with LF line endings, whatever checkout the skeleton was installed from; binary files are
    copied byte for byte. With `dry_run`, templates are still rendered, so missing values fail the same way, but
    nothing is written.
    """
    variables = {**values, **{key: value for key, value in BACKENDS[backend].items() if key != "label"}}
    written = []
    for layer in ("common", backend):
        root = SKELETON / layer
        for source in sorted(root.rglob("*")):
            relative = source.relative_to(root)
            if not source.is_file() or "__pycache__" in relative.parts:
                continue
            target = dest.joinpath(*(output_name(part, values["package"]) for part in relative.parts))
            content = source.read_bytes()
            text = text_or_none(content)
            if target.suffix == TEMPLATE_SUFFIX:
                target = target.with_suffix("")
                text = Template(text).substitute(variables)
            if text is not None:
                content = text.replace("\r\n", "\n").encode("utf-8")
            written.append(target)
            if dry_run:
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
    return written


def resolve(question: str, given: str | None, default: str | None, check: Check, interactive: bool) -> str:
    """Return the option given on the command line, else ask, else (with --yes) the default."""
    if given is None and interactive:
        import questionary

        answer = questionary.text(question, default=default or "", validate=lambda v: check(v) or True).ask()
        if answer is None:
            raise KeyboardInterrupt
        return answer
    value = given if given is not None else default
    if value is None:
        raise ProjectError(f"{question}: required with --yes")
    error = check(value)
    if error:
        raise ProjectError(f"{question}: {error}")
    return value


def resolve_backend(given: str | None, interactive: bool) -> str:
    if given is not None or not interactive or len(BACKENDS) == 1:
        return given or next(iter(BACKENDS))
    import questionary

    choices = [questionary.Choice(backend["label"], value=key) for key, backend in BACKENDS.items()]
    answer = questionary.select("Documentation", choices=choices).ask()
    if answer is None:
        raise KeyboardInterrupt
    return answer


def new_project(args: argparse.Namespace) -> int:
    interactive = not args.yes
    dest = Path(resolve("Folder to create", args.dest, None, check_dest, interactive))
    name = resolve(
        "Distribution name (pip install ...)",
        args.name,
        default_dist_name(dest.resolve().name),
        check_dist_name,
        interactive,
    )
    values = {"dist_name": name}
    values["package"] = resolve("Import name", args.package, default_package(name), check_package, interactive)
    values["title"] = resolve("Title", args.title, name, check_text, interactive)
    values["description"] = resolve(
        "One-line description", args.description, "A SCENE code project.", check_text, interactive
    )
    values["author"] = resolve("Author", args.author, git_user_name() or "SCENE Collaboration", check_text, interactive)
    values["github_url"] = resolve(
        "GitHub repository URL",
        args.github,
        f"https://github.com/SCENE-Collaboration/{name}",
        check_url,
        interactive,
    )
    values["github_url"] = values["github_url"].rstrip("/").removesuffix(".git")
    backend = resolve_backend(args.docs, interactive)

    print(f"\nProject in {dest}:")
    for key, value in {**values, "docs": backend}.items():
        print(f"  {key:<12} {value}")
    if interactive:
        import questionary

        if not questionary.confirm("Create it?", default=True).ask():
            print("Nothing written.")
            return 1

    written = generate(dest, values, backend, dry_run=args.dry_run)
    if args.dry_run:
        print(f"\nDry run: would create {len(written)} files; nothing written.")
        for path in written:
            print(f"  {path.relative_to(dest).as_posix()}")
        return 0
    print(f"\nCreated {len(written)} files. Next, in {dest}:")
    print("  git init")
    print("  with uv:              uv sync --extra dev, then uv run pre-commit install and uv run pytest")
    print(
        '  with pip or conda:    pip install -e ".[dev]" in an activated environment, then pre-commit install and pytest'
    )
    print("  see Using this template in the SCENE guidelines for each step")
    print(f"then create {values['github_url']} on GitHub, commit and push.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="scene-repo-template", description="Create SCENE code projects.")
    commands = parser.add_subparsers(dest="command", required=True)
    new = commands.add_parser(
        "new",
        help="create a project",
        description="Create a project. Options not given are asked for; with --yes, their defaults are used.",
    )
    new.add_argument("dest", nargs="?", help="folder to create; must not exist, or be empty")
    new.add_argument("--name", help="distribution name, the one people pip install (default: the folder name)")
    new.add_argument("--package", help="import name (default: derived from --name)")
    new.add_argument("--title", help="project title (default: --name)")
    new.add_argument("--description", help="one-line description")
    new.add_argument("--author", help="author (default: git config user.name)")
    new.add_argument("--github", help="repository URL (default: https://github.com/SCENE-Collaboration/<name>)")
    new.add_argument("--docs", choices=list(BACKENDS), help="documentation backend")
    new.add_argument("-y", "--yes", action="store_true", help="use defaults for options not given; do not confirm")
    new.add_argument("-n", "--dry-run", action="store_true", help="ask everything, list the files, write nothing")
    args = parser.parse_args(argv)
    try:
        return new_project(args)
    except ProjectError as error:
        parser.exit(2, f"scene-repo-template: error: {error}\n")
    except OSError as error:
        parser.exit(1, f"scene-repo-template: error: {error}\nFiles written before the error are left in place.\n")
    except KeyboardInterrupt:
        print("\nCancelled; nothing written.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
