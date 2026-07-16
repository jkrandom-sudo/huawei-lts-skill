from scripts.generate_tools import validate_catalog


def test_checked_in_catalog_matches_installed_sdk():
    errors = validate_catalog()

    assert errors == []
