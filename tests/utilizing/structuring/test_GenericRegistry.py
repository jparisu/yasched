"""Tests for GenericRegistry."""

import pytest

from yasched.utilizing.structuring.GenericRegistry import GenericRegistry


# ---------------------------------------------------------------------------
# Concrete subclass for testing (str values)
# ---------------------------------------------------------------------------


class _StrRegistry(GenericRegistry[str]):
    pass


@pytest.fixture
def reg() -> _StrRegistry:
    return _StrRegistry()


# ---------------------------------------------------------------------------
# register — sweet path
# ---------------------------------------------------------------------------


def test_register_stores_value(reg):
    reg.register("key", "value")
    assert reg.get("key") == "value"


def test_register_multiple_keys(reg):
    reg.register("a", "alpha")
    reg.register("b", "beta")
    assert reg.get("a") == "alpha"
    assert reg.get("b") == "beta"


def test_register_integer_typed_registry():
    int_reg: GenericRegistry[int] = GenericRegistry()
    int_reg.register("x", 42)
    assert int_reg.get("x") == 42


# ---------------------------------------------------------------------------
# register — on_duplicate
# ---------------------------------------------------------------------------


def test_register_duplicate_raises_by_default(reg):
    reg.register("key", "first")
    with pytest.raises(KeyError):
        reg.register("key", "second")


def test_register_duplicate_replace(reg):
    reg.register("key", "first")
    reg.register("key", "second", on_duplicate="replace")
    assert reg.get("key") == "second"


def test_register_duplicate_ignore_keeps_original(reg):
    reg.register("key", "first")
    reg.register("key", "second", on_duplicate="ignore")
    assert reg.get("key") == "first"


def test_register_invalid_on_duplicate_raises(reg):
    with pytest.raises(ValueError):
        reg.register("key", "value", on_duplicate="overwrite")


# ---------------------------------------------------------------------------
# register_alias — sweet path
# ---------------------------------------------------------------------------


def test_register_alias_allows_get_by_alias(reg):
    reg.register("canonical", "value")
    reg.register_alias("canonical", "alias")
    assert reg.get("alias") == "value"


def test_register_alias_same_value_as_canonical(reg):
    reg.register("canonical", "value")
    reg.register_alias("canonical", "alias")
    assert reg.get("alias") == reg.get("canonical")


def test_multiple_aliases_for_one_canonical(reg):
    reg.register("key", "value")
    reg.register_alias("key", "alias1")
    reg.register_alias("key", "alias2")
    assert reg.get("alias1") == "value"
    assert reg.get("alias2") == "value"


# ---------------------------------------------------------------------------
# register_alias — failure cases
# ---------------------------------------------------------------------------


def test_register_alias_nonexistent_canonical_raises(reg):
    with pytest.raises(KeyError):
        reg.register_alias("missing", "alias")


def test_register_alias_when_alias_is_canonical_key_raises(reg):
    reg.register("key1", "val1")
    reg.register("key2", "val2")
    with pytest.raises(ValueError):
        reg.register_alias("key1", "key2")


def test_register_alias_duplicate_raises_by_default(reg):
    reg.register("key", "value")
    reg.register_alias("key", "alias")
    with pytest.raises(KeyError):
        reg.register_alias("key", "alias")


def test_register_alias_duplicate_replace(reg):
    reg.register("key1", "val1")
    reg.register("key2", "val2")
    reg.register_alias("key1", "alias")
    reg.register_alias("key2", "alias", on_duplicate="replace")
    assert reg.get("alias") == "val2"


def test_register_alias_duplicate_ignore(reg):
    reg.register("key1", "val1")
    reg.register("key2", "val2")
    reg.register_alias("key1", "alias")
    reg.register_alias("key2", "alias", on_duplicate="ignore")
    assert reg.get("alias") == "val1"


def test_register_alias_invalid_on_duplicate_raises(reg):
    reg.register("key", "value")
    with pytest.raises(ValueError):
        reg.register_alias("key", "alias", on_duplicate="bad")


# ---------------------------------------------------------------------------
# get
# ---------------------------------------------------------------------------


def test_get_by_canonical_key(reg):
    reg.register("k", "v")
    assert reg.get("k") == "v"


def test_get_by_alias(reg):
    reg.register("k", "v")
    reg.register_alias("k", "a")
    assert reg.get("a") == "v"


def test_get_missing_key_raises_key_error(reg):
    with pytest.raises(KeyError):
        reg.get("missing")


def test_get_with_default_returns_default(reg):
    assert reg.get("missing", "fallback") == "fallback"


def test_get_with_none_as_default(reg):
    assert reg.get("missing", None) is None


def test_get_with_false_as_default(reg):
    bool_reg: GenericRegistry[bool] = GenericRegistry()
    assert bool_reg.get("missing", False) is False


# ---------------------------------------------------------------------------
# contains / __contains__
# ---------------------------------------------------------------------------


def test_contains_canonical_key(reg):
    reg.register("k", "v")
    assert reg.contains("k") is True


def test_contains_alias(reg):
    reg.register("k", "v")
    reg.register_alias("k", "a")
    assert reg.contains("a") is True


def test_contains_missing_key(reg):
    assert reg.contains("nope") is False


def test_dunder_contains_canonical(reg):
    reg.register("k", "v")
    assert "k" in reg


def test_dunder_contains_alias(reg):
    reg.register("k", "v")
    reg.register_alias("k", "a")
    assert "a" in reg


def test_dunder_contains_missing(reg):
    assert "nope" not in reg


# ---------------------------------------------------------------------------
# remove
# ---------------------------------------------------------------------------


def test_remove_canonical_key(reg):
    reg.register("k", "v")
    reg.remove("k")
    assert not reg.contains("k")


def test_remove_canonical_also_removes_aliases(reg):
    reg.register("k", "v")
    reg.register_alias("k", "a1")
    reg.register_alias("k", "a2")
    reg.remove("k")
    assert not reg.contains("a1")
    assert not reg.contains("a2")


def test_remove_canonical_reduces_len(reg):
    reg.register("k", "v")
    reg.remove("k")
    assert len(reg) == 0


def test_remove_alias_raises_value_error(reg):
    reg.register("k", "v")
    reg.register_alias("k", "a")
    with pytest.raises(ValueError):
        reg.remove("a")


def test_remove_nonexistent_key_raises_key_error(reg):
    with pytest.raises(KeyError):
        reg.remove("missing")


# ---------------------------------------------------------------------------
# remove_alias
# ---------------------------------------------------------------------------


def test_remove_alias_removes_alias_only(reg):
    reg.register("k", "v")
    reg.register_alias("k", "a")
    reg.remove_alias("a")
    assert not reg.contains("a")
    assert reg.contains("k")
    assert reg.get("k") == "v"


def test_remove_alias_nonexistent_raises(reg):
    with pytest.raises(KeyError):
        reg.remove_alias("nope")


def test_remove_one_alias_leaves_other_intact(reg):
    reg.register("k", "v")
    reg.register_alias("k", "a1")
    reg.register_alias("k", "a2")
    reg.remove_alias("a1")
    assert reg.contains("a2")


# ---------------------------------------------------------------------------
# canonical_keys / all_keys / aliases_of
# ---------------------------------------------------------------------------


def test_canonical_keys_returns_only_canonicals(reg):
    reg.register("a", "1")
    reg.register("b", "2")
    reg.register_alias("a", "alias_a")
    assert sorted(reg.canonical_keys()) == ["a", "b"]


def test_all_keys_includes_aliases(reg):
    reg.register("a", "1")
    reg.register_alias("a", "alias_a")
    assert sorted(reg.all_keys()) == ["a", "alias_a"]


def test_aliases_of_returns_aliases(reg):
    reg.register("k", "v")
    reg.register_alias("k", "a1")
    reg.register_alias("k", "a2")
    assert sorted(reg.aliases_of("k")) == ["a1", "a2"]


def test_aliases_of_no_aliases_returns_empty(reg):
    reg.register("k", "v")
    assert reg.aliases_of("k") == []


# ---------------------------------------------------------------------------
# values / items
# ---------------------------------------------------------------------------


def test_values_returns_canonical_values_only(reg):
    reg.register("a", "alpha")
    reg.register("b", "beta")
    reg.register_alias("a", "alias_a")
    assert sorted(reg.values()) == ["alpha", "beta"]


def test_items_returns_canonical_pairs_only(reg):
    reg.register("a", "alpha")
    reg.register("b", "beta")
    reg.register_alias("a", "alias_a")
    assert sorted(reg.items()) == [("a", "alpha"), ("b", "beta")]


# ---------------------------------------------------------------------------
# __len__
# ---------------------------------------------------------------------------


def test_len_empty_registry(reg):
    assert len(reg) == 0


def test_len_counts_only_canonicals(reg):
    reg.register("a", "1")
    reg.register("b", "2")
    reg.register_alias("a", "alias_a")
    assert len(reg) == 2


def test_len_after_remove(reg):
    reg.register("a", "1")
    reg.register("b", "2")
    reg.remove("a")
    assert len(reg) == 1
