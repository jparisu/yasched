"""Tests for coring.Schedule shared base class."""

from yasched.coring.Schedule import Schedule

# ---------------------------------------------------------------------------
# Base class behavior
# ---------------------------------------------------------------------------


def test_schedule_can_be_instantiated_directly_without_abstract_methods():
    s = Schedule()
    assert isinstance(s, Schedule)


def test_schedule_is_a_plain_base_class():
    assert Schedule.__bases__ == (object,)


# ---------------------------------------------------------------------------
# Subclass contract
# ---------------------------------------------------------------------------


def test_concrete_subclass_without_abstract_methods_is_instantiable():
    class ConcreteSchedule(Schedule):
        pass

    s = ConcreteSchedule()
    assert isinstance(s, Schedule)


def test_isinstance_check_on_subclass():
    class ConcreteSchedule(Schedule):
        pass

    s = ConcreteSchedule()
    assert isinstance(s, Schedule)
