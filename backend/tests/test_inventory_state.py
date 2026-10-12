from app.core.inventory import InventoryState, validate_inventory_transition


def test_inventory_statuses_are_explicit_and_valid():
    assert InventoryState.AVAILABLE.value == "AVAILABLE"
    assert InventoryState.RESERVED.value == "RESERVED"
    assert InventoryState.SOLD.value == "SOLD"
    assert InventoryState.DAMAGED.value == "DAMAGED"


def test_allowed_inventory_transitions():
    assert validate_inventory_transition(InventoryState.AVAILABLE, InventoryState.RESERVED) is True
    assert validate_inventory_transition("AVAILABLE", "RESERVED") is True
    assert validate_inventory_transition("RESERVED", "SOLD") is True
    assert validate_inventory_transition("AVAILABLE", "DAMAGED") is True


def test_disallowed_inventory_transitions_are_rejected():
    assert validate_inventory_transition("SOLD", "AVAILABLE") is False
    assert validate_inventory_transition("DAMAGED", "RESERVED") is False
    assert validate_inventory_transition("ARCHIVED", "SOLD") is False
