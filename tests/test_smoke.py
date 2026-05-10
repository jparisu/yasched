from yasched import __version__


def test_version_exposed() -> None:
    assert __version__ == "2.0.0"
