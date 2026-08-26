"""Customer/model collection access control (ACL)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class Scope:
    """A restricted view: only chunks matching the allowed customers/models.

    An empty ``customers`` set matches nothing, so a customer with no assigned
    collections sees no documents. ``None`` (not a Scope) means unrestricted.
    """

    customers: frozenset[str] = field(default_factory=frozenset)
    models: frozenset[str] = field(default_factory=frozenset)

    def allows(self, metadata: dict) -> bool:
        customer = str(metadata.get("customer", ""))
        model = str(metadata.get("model", ""))
        if not customer or customer not in self.customers:
            return False
        if self.models and model not in self.models:
            return False
        return True


def build_scope(role: str, customers: list[str], models: list[str]) -> Scope | None:
    """Return None (unrestricted) for internal roles, else a restricted Scope."""
    if role in ("admin", "support"):
        return None
    return Scope(customers=frozenset(customers), models=frozenset(models))
