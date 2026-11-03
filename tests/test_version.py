from importlib.metadata import packages_distributions, version

import placeholder


def test_installed_version_matches_package_version():
    (distribution,) = set(packages_distributions()["placeholder"])
    assert version(distribution) == placeholder.__version__
