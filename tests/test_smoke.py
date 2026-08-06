from yasched import __version__


def test_version_exposed() -> None:
    assert __version__ == "4.0.0"
