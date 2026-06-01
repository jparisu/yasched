"""Tests for XymlLoader."""

import pytest

from yasched.utilizing.xyml.XymlKeyRegistry import XymlKeyRegistry
from yasched.utilizing.xyml.XymlLoader import (
    XymlCircularIncludeError,
    XymlDirectiveError,
    XymlFileNotFoundError,
    XymlLoader,
)


@pytest.fixture(autouse=True)
def reset_registry():
    XymlKeyRegistry._reset_instance()
    yield
    XymlKeyRegistry._reset_instance()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write(tmp_path, name: str, content: str):
    p = tmp_path / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# load — basic YAML (no directives)
# ---------------------------------------------------------------------------


def test_load_simple_scalar(tmp_path):
    p = _write(tmp_path, "a.yaml", "hello")
    assert XymlLoader.load(p) == "hello"


def test_load_simple_mapping(tmp_path):
    p = _write(tmp_path, "a.yaml", "key: value\nnum: 42")
    assert XymlLoader.load(p) == {"key": "value", "num": 42}


def test_load_simple_list(tmp_path):
    p = _write(tmp_path, "a.yaml", "- 1\n- 2\n- 3")
    assert XymlLoader.load(p) == [1, 2, 3]


def test_load_nested_structure(tmp_path):
    p = _write(tmp_path, "a.yaml", "outer:\n  inner: value\n  list:\n    - 1\n    - 2")
    assert XymlLoader.load(p) == {"outer": {"inner": "value", "list": [1, 2]}}


def test_load_file_not_found_raises():
    with pytest.raises(XymlFileNotFoundError):
        XymlLoader.load("/no/such/file.yaml")


# ---------------------------------------------------------------------------
# loads — basic
# ---------------------------------------------------------------------------


def test_loads_simple_mapping(tmp_path):
    result = XymlLoader.loads("x: 1\ny: 2", base_path=tmp_path)
    assert result == {"x": 1, "y": 2}


def test_loads_none_base_path_does_not_raise():
    result = XymlLoader.loads("value: 99")
    assert result == {"value": 99}


def test_loads_null_yaml_returns_none():
    assert XymlLoader.loads("null") is None


# ---------------------------------------------------------------------------
# __file__ — REPLACE
# ---------------------------------------------------------------------------


def test_file_directive_replaces_node(tmp_path):
    _write(tmp_path, "inner.yaml", "key: from_inner")
    p = _write(tmp_path, "main.yaml", "data:\n  __file__: inner.yaml")
    result = XymlLoader.load(p)
    assert result == {"data": {"key": "from_inner"}}


def test_file_directive_replaces_with_list(tmp_path):
    _write(tmp_path, "list.yaml", "- a\n- b\n- c")
    p = _write(tmp_path, "main.yaml", "items:\n  __file__: list.yaml")
    result = XymlLoader.load(p)
    assert result == {"items": ["a", "b", "c"]}


def test_file_directive_replaces_with_scalar(tmp_path):
    _write(tmp_path, "scalar.yaml", "42")
    p = _write(tmp_path, "main.yaml", "count:\n  __file__: scalar.yaml")
    result = XymlLoader.load(p)
    assert result == {"count": 42}


def test_file_directive_at_top_level(tmp_path):
    _write(tmp_path, "content.yaml", "a: 1\nb: 2")
    p = _write(tmp_path, "main.yaml", "__file__: content.yaml")
    result = XymlLoader.load(p)
    assert result == {"a": 1, "b": 2}


def test_file_directive_with_sibling_keys_raises(tmp_path):
    _write(tmp_path, "inner.yaml", "x: 1")
    p = _write(tmp_path, "main.yaml", "__file__: inner.yaml\nextra: bad")
    with pytest.raises(XymlDirectiveError):
        XymlLoader.load(p)


def test_file_directive_not_found_raises(tmp_path):
    p = _write(tmp_path, "main.yaml", "__file__: missing.yaml")
    with pytest.raises(XymlFileNotFoundError):
        XymlLoader.load(p)


def test_file_directive_relative_path_resolved_from_including_file(tmp_path):
    sub = tmp_path / "sub"
    sub.mkdir()
    _write(sub, "inner.yaml", "val: 10")
    p = _write(tmp_path, "main.yaml", "data:\n  __file__: sub/inner.yaml")
    result = XymlLoader.load(p)
    assert result == {"data": {"val": 10}}


# ---------------------------------------------------------------------------
# __ext__ — EXTEND
# ---------------------------------------------------------------------------


def test_ext_directive_merges_file_as_base(tmp_path):
    _write(tmp_path, "base.yaml", "a: 1\nb: 2")
    p = _write(tmp_path, "main.yaml", "__ext__: base.yaml\nb: overridden\nc: 3")
    result = XymlLoader.load(p)
    assert result == {"a": 1, "b": "overridden", "c": 3}


def test_ext_directive_file_key_excluded_from_result(tmp_path):
    _write(tmp_path, "base.yaml", "x: 10")
    p = _write(tmp_path, "main.yaml", "__ext__: base.yaml\ny: 20")
    result = XymlLoader.load(p)
    assert "__ext__" not in result


def test_ext_directive_current_keys_override_file_keys(tmp_path):
    _write(tmp_path, "base.yaml", "color: red\nsize: large")
    p = _write(tmp_path, "main.yaml", "__ext__: base.yaml\ncolor: blue")
    result = XymlLoader.load(p)
    assert result["color"] == "blue"
    assert result["size"] == "large"


def test_ext_directive_file_is_base_only(tmp_path):
    _write(tmp_path, "base.yaml", "from_base: yes")
    p = _write(tmp_path, "main.yaml", "__ext__: base.yaml\nfrom_local: yes")
    result = XymlLoader.load(p)
    assert result == {"from_base": True, "from_local": True}


def test_ext_directive_file_not_mapping_raises(tmp_path):
    _write(tmp_path, "list.yaml", "- 1\n- 2")
    p = _write(tmp_path, "main.yaml", "__ext__: list.yaml\na: 1")
    with pytest.raises(XymlDirectiveError):
        XymlLoader.load(p)


def test_ext_directive_not_found_raises(tmp_path):
    p = _write(tmp_path, "main.yaml", "__ext__: missing.yaml\na: 1")
    with pytest.raises(XymlFileNotFoundError):
        XymlLoader.load(p)


# ---------------------------------------------------------------------------
# Nested directives
# ---------------------------------------------------------------------------


def test_nested_file_directives(tmp_path):
    _write(tmp_path, "leaf.yaml", "value: leaf")
    _write(tmp_path, "mid.yaml", "child:\n  __file__: leaf.yaml")
    p = _write(tmp_path, "main.yaml", "root:\n  __file__: mid.yaml")
    result = XymlLoader.load(p)
    assert result == {"root": {"child": {"value": "leaf"}}}


def test_list_of_file_directives(tmp_path):
    _write(tmp_path, "a.yaml", "name: alpha")
    _write(tmp_path, "b.yaml", "name: beta")
    p = _write(tmp_path, "main.yaml", "items:\n  - __file__: a.yaml\n  - __file__: b.yaml")
    result = XymlLoader.load(p)
    assert result == {"items": [{"name": "alpha"}, {"name": "beta"}]}


def test_ext_inside_file_include(tmp_path):
    _write(tmp_path, "base.yaml", "x: 1")
    _write(tmp_path, "child.yaml", "__ext__: base.yaml\ny: 2")
    p = _write(tmp_path, "main.yaml", "data:\n  __file__: child.yaml")
    result = XymlLoader.load(p)
    assert result == {"data": {"x": 1, "y": 2}}


# ---------------------------------------------------------------------------
# Circular include detection
# ---------------------------------------------------------------------------


def test_direct_circular_include_raises(tmp_path):
    p = _write(tmp_path, "a.yaml", "__file__: a.yaml")
    with pytest.raises(XymlCircularIncludeError):
        XymlLoader.load(p)


def test_transitive_circular_include_raises(tmp_path):
    _write(tmp_path, "b.yaml", "__file__: a.yaml")
    _write(tmp_path, "a.yaml", "__file__: b.yaml")
    p = tmp_path / "a.yaml"
    with pytest.raises(XymlCircularIncludeError):
        XymlLoader.load(p)


def test_same_file_twice_in_different_branches_is_allowed(tmp_path):
    _write(tmp_path, "shared.yaml", "val: shared")
    p = _write(
        tmp_path,
        "main.yaml",
        "a:\n  __file__: shared.yaml\nb:\n  __file__: shared.yaml",
    )
    result = XymlLoader.load(p)
    assert result == {"a": {"val": "shared"}, "b": {"val": "shared"}}


# ---------------------------------------------------------------------------
# Multiple directives in same mapping
# ---------------------------------------------------------------------------


def test_two_directive_keys_in_same_mapping_raises(tmp_path):
    _write(tmp_path, "a.yaml", "x: 1")
    _write(tmp_path, "b.yaml", "y: 2")
    p = _write(tmp_path, "main.yaml", "__file__: a.yaml\n__ext__: b.yaml")
    with pytest.raises(XymlDirectiveError):
        XymlLoader.load(p)


# ---------------------------------------------------------------------------
# loads with base_path for relative resolution
# ---------------------------------------------------------------------------


def test_loads_resolves_relative_to_base_path(tmp_path):
    _write(tmp_path, "inner.yaml", "loaded: yes")
    result = XymlLoader.loads("__file__: inner.yaml", base_path=tmp_path)
    assert result == {"loaded": True}


def test_loads_file_not_found_relative_to_base_path_raises(tmp_path):
    with pytest.raises(XymlFileNotFoundError):
        XymlLoader.loads("__file__: nonexistent.yaml", base_path=tmp_path)
