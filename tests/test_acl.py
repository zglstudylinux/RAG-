"""Tests for customer/model ACL scoping."""

from __future__ import annotations

from ragkb.core.acl import Scope, build_scope


def test_internal_roles_are_unrestricted() -> None:
    assert build_scope("admin", [], []) is None
    assert build_scope("support", [], []) is None


def test_customer_scope() -> None:
    scope = build_scope("customer", ["acme"], ["x1"])
    assert scope is not None
    assert scope.customers == frozenset(["acme"])
    assert scope.models == frozenset(["x1"])


def test_scope_allows_matching_customer() -> None:
    scope = Scope(customers=frozenset(["acme"]))
    assert scope.allows({"customer": "acme", "model": "x1"})
    assert not scope.allows({"customer": "globex"})
    assert not scope.allows({})  # untagged docs are hidden from restricted scopes


def test_scope_model_filter() -> None:
    scope = Scope(customers=frozenset(["acme"]), models=frozenset(["x1"]))
    assert scope.allows({"customer": "acme", "model": "x1"})
    assert not scope.allows({"customer": "acme", "model": "x2"})
