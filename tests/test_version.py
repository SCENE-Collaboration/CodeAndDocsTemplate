from importlib.metadata import packages_distributions, version

import scene_repo_template


def test_installed_version_matches_package_version():
    (distribution,) = set(packages_distributions()["scene_repo_template"])
    assert version(distribution) == scene_repo_template.__version__
