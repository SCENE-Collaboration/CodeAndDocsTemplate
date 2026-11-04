import datetime
import importlib
import importlib.metadata
import json
import os
import shutil
import subprocess
import sys
import types
from pathlib import Path
from string import Template

import pytest

from scene_repo_template import cli

REPOSITORY = Path(__file__).parents[1]
ANSWERS = {"dist_name", "package", "title", "description", "author", "github_url", "license", "year"}

# Installing and building a generated project needs uv, Node.js and the network; CI sets this variable.
E2E = pytest.mark.skipif(
    not os.environ.get("SCENE_TEMPLATE_E2E"), reason="set SCENE_TEMPLATE_E2E=1 to install and build a generated project"
)


def generate(tmp_path, *options, folder="my-project"):
    dest = tmp_path / folder
    assert cli.main(["new", str(dest), "--yes", *options]) == 0
    return dest


def files_of(root):
    return {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}


def refused(tmp_path, *options, folder="my-project"):
    with pytest.raises(SystemExit) as exit_info:
        cli.main(["new", str(tmp_path / folder), "--yes", *options])
    return exit_info.value.code == 2


COMMON_FILES = {
    ".github/workflows/docs.yml",
    ".github/workflows/lint.yml",
    ".github/workflows/tests.yml",
    ".gitignore",
    ".pre-commit-config.yaml",
    "LICENSE",
    "README.md",
    "docs/images/favicon.png",
    "docs/images/scene-logo.png",
    "docs/index.md",
    "my_project/__init__.py",
    "my_project/version.py",
    "pyproject.toml",
    "tests/test_version.py",
}
BACKEND_FILES = {
    "jupyter-book": {"docs/myst.yml", "docs/_static/footer.md", "docs/_static/scene.css"},
    "mkdocs": {"mkdocs.yml", "docs/stylesheets/scene.css"},
}


def test_every_backend_is_tested():
    assert set(BACKEND_FILES) == set(cli.BACKENDS)


@pytest.mark.parametrize("backend", BACKEND_FILES)
def test_a_project_gets_the_common_files_and_only_its_own_docs_backend(tmp_path, backend):
    project = files_of(generate(tmp_path, f"--docs={backend}"))
    assert COMMON_FILES | BACKEND_FILES[backend] <= project
    other_backends = set().union(*(files for name, files in BACKEND_FILES.items() if name != backend))
    assert project & other_backends == set()


def test_the_backends_ship_the_same_logo_and_favicon():
    for image in ("scene-logo.png", "favicon.png"):
        copies = {(cli.SKELETON / backend / "docs" / "images" / image).read_bytes() for backend in cli.BACKENDS}
        assert len(copies) == 1, image


def test_every_license_has_its_text():
    assert {path.name for path in (cli.SKELETON / "licenses").iterdir()} == set(cli.LICENSES)


@pytest.mark.parametrize("license", cli.LICENSES)
def test_the_license_reaches_every_file_that_names_it(tmp_path, license):
    dest = generate(tmp_path, f"--license={license}", "--author=A. Person")
    assert f'license = "{license}"' in (dest / "pyproject.toml").read_text(encoding="utf-8")
    assert f"{license}: see `LICENSE`." in (dest / "README.md").read_text(encoding="utf-8")
    assert f"license: {license}\n" in (dest / "docs" / "myst.yml").read_text(encoding="utf-8")
    text = (dest / "LICENSE").read_text(encoding="utf-8")
    # Apache-2.0 has no copyright line to fill; the others start with one.
    if license != "Apache-2.0":
        assert f"{datetime.date.today().year}" in text.splitlines()[2]
        assert "A. Person" in text.splitlines()[2]


def test_the_default_license_is_apache(tmp_path):
    assert "Apache License" in (generate(tmp_path) / "LICENSE").read_text(encoding="utf-8")


def test_an_unknown_license_is_refused(tmp_path):
    assert refused(tmp_path, "--license=GPL-3.0")


def test_the_docs_extra_follows_the_backend(tmp_path):
    pyproject = (generate(tmp_path, "--docs=mkdocs") / "pyproject.toml").read_text(encoding="utf-8")
    assert '"mkdocstrings[python]>=0.27"' in pyproject
    assert '"mkdocs-jupyter>=0.25"' in pyproject
    assert "jupyter-book" not in pyproject


def test_no_skeleton_naming_is_left_in_a_project(tmp_path):
    skeleton = files_of(cli.SKELETON)
    for marker in (cli.TEMPLATE_SUFFIX, cli.DOT_PREFIX, cli.PACKAGE_DIR):
        assert any(marker in name for name in skeleton)
    project = files_of(generate(tmp_path))
    assert [
        name for name in project if any(m in name for m in (cli.TEMPLATE_SUFFIX, cli.DOT_PREFIX, cli.PACKAGE_DIR))
    ] == []


def test_none_of_the_guidelines_site_is_copied(tmp_path):
    assert (REPOSITORY / "docs" / "guides").is_dir()
    assert (REPOSITORY / "docs" / "contributed-examples").is_dir()
    project = files_of(generate(tmp_path))
    assert [name for name in project if "guides/" in name or "contributed-examples" in name] == []


def test_answers_reach_the_rendered_files(tmp_path):
    dest = generate(
        tmp_path,
        "--name=scene-gaze",
        "--package=gaze",
        "--title=Gaze: tracking",
        "--description=Eye tracking in freely moving animals.",
        "--author=A. Person",
        "--github=https://github.com/lab/scene-gaze/",
    )
    pyproject = (dest / "pyproject.toml").read_text(encoding="utf-8")
    assert 'name = "scene-gaze"' in pyproject
    assert 'authors = [ { name = "A. Person" } ]' in pyproject
    assert 'packages = [ "gaze" ]' in pyproject
    assert 'version = { attr = "gaze.version.__version__" }' in pyproject
    assert 'urls.Source = "https://github.com/lab/scene-gaze"' in pyproject
    assert 'optional-dependencies.docs = [ "jupyter-book>=2" ]' in pyproject
    myst = (dest / "docs" / "myst.yml").read_text(encoding="utf-8")
    assert 'title: "Gaze: tracking"' in myst
    assert "github: https://github.com/lab/scene-gaze\n" in myst
    assert 'importlib.import_module("gaze")' in (dest / "tests" / "test_version.py").read_text(encoding="utf-8")
    assert (dest / "gaze" / "__init__.py").is_file()


def test_the_rendered_pyproject_is_valid_toml(tmp_path):
    tomllib = pytest.importorskip("tomllib")
    pyproject = tomllib.loads((generate(tmp_path) / "pyproject.toml").read_text(encoding="utf-8"))
    assert pyproject["project"]["name"] == "my-project"


def test_github_actions_expressions_are_copied_verbatim(tmp_path):
    docs = (generate(tmp_path) / ".github" / "workflows" / "docs.yml").read_text(encoding="utf-8")
    assert "BASE_URL: /${{ github.event.repository.name }}" in docs


def test_templates_use_only_the_values_the_generator_provides():
    provided = ANSWERS | {key for backend in cli.BACKENDS.values() for key in backend if key != "label"}
    used = set()
    for path in cli.SKELETON.rglob(f"*{cli.TEMPLATE_SUFFIX}"):
        template = Template(path.read_text(encoding="utf-8"))
        for match in template.pattern.finditer(template.template):
            assert match.group("invalid") is None, path
            used.add(match.group("named") or match.group("braced"))
    used.discard(None)
    assert used
    assert used <= provided


def test_the_default_import_name_comes_from_the_folder_name(tmp_path):
    dest = generate(tmp_path, folder="2-My.Project")
    assert (dest / "my_project" / "__init__.py").is_file()


def test_a_folder_name_with_spaces_and_accents_gives_a_valid_default_name(tmp_path):
    dest = generate(tmp_path, folder="My Projét")
    assert 'name = "My-Projet"' in (dest / "pyproject.toml").read_text(encoding="utf-8")
    assert (dest / "my_projet" / "__init__.py").is_file()


def test_a_github_url_ending_in_git_is_stored_without_it(tmp_path):
    dest = generate(tmp_path, "--github=https://github.com/lab/proj.git/")
    pyproject = (dest / "pyproject.toml").read_text(encoding="utf-8")
    assert 'urls.Source = "https://github.com/lab/proj"' in pyproject
    assert 'urls."Bug Tracker" = "https://github.com/lab/proj/issues"' in pyproject


def test_text_files_are_written_with_lf_and_binary_files_byte_for_byte(tmp_path, monkeypatch):
    skeleton = tmp_path / "skeleton"
    (skeleton / "common").mkdir(parents=True)
    (skeleton / "jupyter-book").mkdir()
    (skeleton / "licenses" / "MIT").mkdir(parents=True)
    (skeleton / "common" / "plain.txt").write_bytes(b"one\r\ntwo\r\n")
    (skeleton / "common" / "rendered.txt.tmpl").write_bytes(b"$package\r\n")
    png = b"\x89PNG\r\n\x1a\n\x00\x00\r\n"
    (skeleton / "common" / "logo.png").write_bytes(png)
    monkeypatch.setattr(cli, "SKELETON", skeleton)
    dest = tmp_path / "out"
    cli.generate(dest, {"package": "pkg", "license": "MIT"}, "jupyter-book")
    assert (dest / "plain.txt").read_bytes() == b"one\ntwo\n"
    assert (dest / "rendered.txt").read_bytes() == b"pkg\n"
    assert (dest / "logo.png").read_bytes() == png


def test_no_generated_text_file_has_crlf(tmp_path):
    dest = generate(tmp_path)
    texts = {path: cli.text_or_none(path.read_bytes()) for path in dest.rglob("*") if path.is_file()}
    assert any(text is None for text in texts.values())  # the logo and favicon are binary
    assert [path for path, text in texts.items() if text is not None and "\r" in text] == []


def test_an_unwritable_destination_is_reported_without_a_traceback(tmp_path, capsys):
    (tmp_path / "a-file").write_text("", encoding="utf-8")
    with pytest.raises(SystemExit) as exit_info:
        cli.main(["new", str(tmp_path / "a-file" / "proj"), "--yes", "--name=proj"])
    assert exit_info.value.code == 1
    assert "Traceback" not in capsys.readouterr().err


def test_a_dry_run_lists_the_files_of_a_real_run_and_writes_nothing(tmp_path, capsys):
    assert cli.main(["new", str(tmp_path / "dry"), "--yes", "--dry-run"]) == 0
    assert not (tmp_path / "dry").exists()
    listing = capsys.readouterr().out.split("Dry run:")[1]
    listed = {line.strip() for line in listing.splitlines() if line.startswith("  ")}
    assert listed == files_of(generate(tmp_path, folder="dry"))


class Prompts:
    """Stands in for questionary: every question is answered with its default, as if by pressing Enter."""

    def __init__(self):
        self.asked = []

    def text(self, question, default="", validate=None):
        self.asked.append((question, default))
        return types.SimpleNamespace(ask=lambda: default)

    def confirm(self, question, default=True):
        self.asked.append((question, default))
        return types.SimpleNamespace(ask=lambda: default)

    def select(self, question, choices):
        self.asked.append((question, choices[0].value))
        return types.SimpleNamespace(ask=lambda: choices[0].value)

    def Choice(self, title, value):
        return types.SimpleNamespace(title=title, value=value)


@pytest.fixture
def prompts(monkeypatch):
    fake = Prompts()
    monkeypatch.setitem(sys.modules, "questionary", fake)
    return fake


def test_an_interactive_dry_run_does_not_ask_to_create(tmp_path, prompts):
    assert cli.main(["new", str(tmp_path / "dry"), "--dry-run"]) == 0
    assert "Create it?" not in [question for question, _ in prompts.asked]
    assert not (tmp_path / "dry").exists()


def test_an_invalid_option_is_asked_again_interactively(tmp_path, prompts, capsys):
    cli.main(["new", str(tmp_path / "proj"), "--package=json", "--dry-run"])
    assert ("Import name", "json") in prompts.asked
    assert "Import name: json is a standard-library module" in capsys.readouterr().err


def test_a_non_empty_folder_is_refused(tmp_path):
    dest = tmp_path / "taken"
    dest.mkdir()
    (dest / "keep.txt").write_text("kept", encoding="utf-8")
    assert refused(tmp_path, folder="taken")
    assert files_of(dest) == {"keep.txt"}


@pytest.mark.parametrize(
    "package",
    [
        *["1project", "my-project", "MyProject", "class", "json", "tests", "docs", "lib", "build", "env"],
        *["my_project\n", "pytest", "pre_commit"],
    ],
)
def test_an_invalid_import_name_is_refused(tmp_path, package):
    assert refused(tmp_path, f"--package={package}")
    assert not (tmp_path / "my-project").exists()


@pytest.mark.parametrize("package", ["version", "set", "distribution"])
def test_the_generated_version_test_passes_whatever_the_import_name(tmp_path, monkeypatch, package):
    dest = generate(tmp_path, f"--package={package}")
    monkeypatch.syspath_prepend(str(dest))
    # Stand-ins for the installed metadata: what is at stake is the names the generated test binds.
    monkeypatch.setattr(importlib.metadata, "packages_distributions", lambda: {package: ["my-project"]})
    monkeypatch.setattr(importlib.metadata, "version", lambda _: importlib.import_module(package).__version__)
    namespace = {}
    try:
        exec((dest / "tests" / "test_version.py").read_text(encoding="utf-8"), namespace)
        namespace["test_installed_version_matches_package_version"]()
    finally:
        sys.modules.pop(package, None)


def test_a_distribution_name_with_a_trailing_newline_is_refused(tmp_path):
    # Title and URL given, else their defaults (built from the name) would be what refuses the newline.
    assert refused(tmp_path, "--name=my-project\n", "--title=My project", "--github=https://github.com/x/my-project")


@pytest.mark.parametrize("name", ["pytest", "Pre_Commit", "pytest.cov", "jupyter-book"])
def test_a_distribution_name_of_a_toolchain_dependency_is_refused(tmp_path, name):
    # An explicit import name, else the default (derived from the name) would be what is refused.
    assert refused(tmp_path, f"--name={name}", "--package=my_project")


def test_a_folder_named_like_an_ignored_folder_gets_a_committable_default_import_name(tmp_path):
    dest = generate(tmp_path, folder="build")
    assert (dest / "project" / "__init__.py").is_file()


@pytest.mark.parametrize("title", ['A "quoted" title', "back\\slash", "", "bell\x07", "two\nlines"])
def test_a_title_that_cannot_be_quoted_is_refused(tmp_path, title):
    assert refused(tmp_path, f"--title={title}")


@pytest.mark.parametrize("url", ["SCENE-Collaboration/my-project", "https://", "https:///my-project"])
def test_a_github_url_must_be_a_url_with_a_host(tmp_path, url):
    assert refused(tmp_path, f"--github={url}")


def run(dest, *command):
    # Run in the generated project's own environment, not this repository's.
    env = {key: value for key, value in os.environ.items() if key not in ("VIRTUAL_ENV", "UV_PROJECT_ENVIRONMENT")}
    subprocess.run(command, cwd=dest, env=env, check=True)


@E2E
def test_a_generated_project_installs_lints_and_passes_its_tests(tmp_path):
    dest = generate(tmp_path)
    run(dest, "uv", "lock")
    run(dest, "uv", "sync", "--extra", "dev")
    run(dest, "uv", "run", "pytest")
    run(dest, "git", "init", "--quiet")
    run(dest, "git", "add", "--all")
    run(dest, "uv", "run", "pre-commit", "run", "--all-files", "--hook-stage", "manual")


@E2E
@pytest.mark.skipif(shutil.which("node") is None, reason="Jupyter Book needs Node.js")
def test_a_generated_jupyter_book_builds(tmp_path):
    dest = generate(tmp_path, "--docs=jupyter-book")
    run(dest, "uv", "sync", "--extra", "docs")
    run(dest / "docs", "uv", "run", "jupyter", "book", "build", "--html", "--strict")


@E2E
def test_a_generated_mkdocs_site_builds_with_an_api_page_per_module_and_a_notebook(tmp_path):
    dest = generate(tmp_path, "--docs=mkdocs")
    notebook = {"cells": [{"cell_type": "markdown", "metadata": {}, "source": ["# Analysis"]}], "metadata": {}}
    notebook |= {"nbformat": 4, "nbformat_minor": 5}
    (dest / "docs" / "analysis.ipynb").write_text(json.dumps(notebook), encoding="utf-8")
    mkdocs_yml = dest / "mkdocs.yml"
    mkdocs_yml.write_text(mkdocs_yml.read_text(encoding="utf-8") + "  - analysis.ipynb\n", encoding="utf-8")
    run(dest, "uv", "sync", "--extra", "docs")
    run(dest, "uv", "run", "mkdocs", "build", "--strict")
    assert (dest / "site" / "reference" / "my_project" / "version" / "index.html").is_file()
    assert (dest / "site" / "analysis" / "index.html").is_file()
