"""Tests for GenericSingleton mixin."""

import threading

import pytest

from yasched.utilizing.structuring.GenericSingleton import GenericSingleton


# ---------------------------------------------------------------------------
# Minimal concrete subclasses used across tests
# ---------------------------------------------------------------------------


class _Alpha(GenericSingleton):
    pass


class _Beta(GenericSingleton):
    pass


class _Counter(GenericSingleton):
    """Subclass that tracks how many times __new__ truly constructs an object."""

    constructions: int = 0

    def __new__(cls):
        instance = super().__new__(cls)
        cls.constructions += 1
        return instance


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset all test subclasses before every test."""
    _Alpha._reset_instance()
    _Beta._reset_instance()
    _Counter._reset_instance()
    _Counter.constructions = 0
    yield
    _Alpha._reset_instance()
    _Beta._reset_instance()
    _Counter._reset_instance()


# ---------------------------------------------------------------------------
# get_instance — sweet path
# ---------------------------------------------------------------------------


def test_get_instance_returns_instance():
    instance = _Alpha.get_instance()
    assert isinstance(instance, _Alpha)


def test_get_instance_returns_same_object_on_repeated_calls():
    a = _Alpha.get_instance()
    b = _Alpha.get_instance()
    assert a is b


def test_get_instance_constructs_only_once():
    _Counter.get_instance()
    _Counter.get_instance()
    _Counter.get_instance()
    assert _Counter.constructions == 1


# ---------------------------------------------------------------------------
# Independent singletons per subclass
# ---------------------------------------------------------------------------


def test_different_subclasses_have_independent_singletons():
    alpha = _Alpha.get_instance()
    beta = _Beta.get_instance()
    assert alpha is not beta
    assert type(alpha) is _Alpha
    assert type(beta) is _Beta


def test_subclass_singleton_does_not_bleed_into_parent():
    alpha = _Alpha.get_instance()
    assert not isinstance(alpha, _Beta)


# ---------------------------------------------------------------------------
# _reset_instance
# ---------------------------------------------------------------------------


def test_reset_clears_singleton():
    first = _Alpha.get_instance()
    _Alpha._reset_instance()
    second = _Alpha.get_instance()
    assert first is not second


def test_reset_of_one_subclass_does_not_affect_other():
    _Alpha.get_instance()
    beta_before = _Beta.get_instance()
    _Alpha._reset_instance()
    beta_after = _Beta.get_instance()
    assert beta_before is beta_after


def test_reset_allows_new_construction():
    _Counter.get_instance()
    assert _Counter.constructions == 1
    _Counter._reset_instance()
    _Counter.constructions = 0
    _Counter.get_instance()
    assert _Counter.constructions == 1


# ---------------------------------------------------------------------------
# Thread safety
# ---------------------------------------------------------------------------


def test_get_instance_is_thread_safe():
    results: list[_Alpha] = []

    def worker():
        results.append(_Alpha.get_instance())

    threads = [threading.Thread(target=worker) for _ in range(50)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(results) == 50
    assert all(r is results[0] for r in results)


def test_constructions_happen_exactly_once_under_concurrency():
    results: list[_Counter] = []

    def worker():
        results.append(_Counter.get_instance())

    threads = [threading.Thread(target=worker) for _ in range(50)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert _Counter.constructions == 1
    assert all(r is results[0] for r in results)


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_get_instance_after_multiple_resets_still_works():
    for _ in range(5):
        _Alpha._reset_instance()
    instance = _Alpha.get_instance()
    assert isinstance(instance, _Alpha)


def test_instance_is_exactly_the_declared_subtype():
    instance = _Alpha.get_instance()
    assert type(instance) is _Alpha
    assert not isinstance(instance, _Beta)
