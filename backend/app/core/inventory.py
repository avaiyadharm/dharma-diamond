from enum import Enum
from typing import Iterable, Set


class InventoryState(str, Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    SOLD = "SOLD"
    RETURNED_PENDING_INSPECTION = "RETURNED_PENDING_INSPECTION"
    AVAILABLE_AFTER_INSPECTION = "AVAILABLE_AFTER_INSPECTION"
    DAMAGED = "DAMAGED"
    LOST = "LOST"
    UNDER_REPAIR = "UNDER_REPAIR"
    ARCHIVED = "ARCHIVED"


_ALLOWED_TRANSITIONS: dict[InventoryState, set[InventoryState]] = {
    InventoryState.AVAILABLE: {
        InventoryState.RESERVED,
        InventoryState.SOLD,
        InventoryState.DAMAGED,
        InventoryState.LOST,
        InventoryState.UNDER_REPAIR,
        InventoryState.ARCHIVED,
    },
    InventoryState.RESERVED: {
        InventoryState.AVAILABLE,
        InventoryState.SOLD,
        InventoryState.DAMAGED,
        InventoryState.LOST,
        InventoryState.UNDER_REPAIR,
        InventoryState.ARCHIVED,
    },
    InventoryState.SOLD: {
        InventoryState.RETURNED_PENDING_INSPECTION,
    },
    InventoryState.RETURNED_PENDING_INSPECTION: {
        InventoryState.AVAILABLE_AFTER_INSPECTION,
        InventoryState.DAMAGED,
        InventoryState.LOST,
        InventoryState.ARCHIVED,
    },
    InventoryState.AVAILABLE_AFTER_INSPECTION: {
        InventoryState.AVAILABLE,
        InventoryState.RESERVED,
        InventoryState.SOLD,
        InventoryState.DAMAGED,
    },
    InventoryState.DAMAGED: {
        InventoryState.UNDER_REPAIR,
        InventoryState.ARCHIVED,
    },
    InventoryState.LOST: {
        InventoryState.ARCHIVED,
    },
    InventoryState.UNDER_REPAIR: {
        InventoryState.AVAILABLE,
        InventoryState.DAMAGED,
        InventoryState.ARCHIVED,
    },
    InventoryState.ARCHIVED: set(),
}


def _coerce_state(state: str | InventoryState) -> InventoryState:
    if isinstance(state, InventoryState):
        return state
    return InventoryState(state.upper())


def validate_inventory_transition(
    from_state: str | InventoryState,
    to_state: str | InventoryState,
) -> bool:
    current = _coerce_state(from_state)
    target = _coerce_state(to_state)
    allowed = _ALLOWED_TRANSITIONS.get(current, set())
    return target in allowed


def get_valid_next_states(state: str | InventoryState) -> set[InventoryState]:
    return _ALLOWED_TRANSITIONS.get(_coerce_state(state), set())


__all__ = [
    "InventoryState",
    "validate_inventory_transition",
    "get_valid_next_states",
]
