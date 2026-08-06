"""Tests for XymlKeyBehavior."""

from yasched.utilizing.xyml.XymlKeyBehavior import XymlKeyBehavior


def test_replace_member_exists():
    assert XymlKeyBehavior.REPLACE is not None


def test_extend_member_exists():
    assert XymlKeyBehavior.EXTEND is not None


def test_replace_and_extend_are_distinct():
    assert XymlKeyBehavior.REPLACE != XymlKeyBehavior.EXTEND


def test_members_are_enum_instances():
    assert isinstance(XymlKeyBehavior.REPLACE, XymlKeyBehavior)
    assert isinstance(XymlKeyBehavior.EXTEND, XymlKeyBehavior)
