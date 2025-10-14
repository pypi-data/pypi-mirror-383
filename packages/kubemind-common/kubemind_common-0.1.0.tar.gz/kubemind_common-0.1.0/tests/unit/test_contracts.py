from kubemind_common.testing.contracts import assert_valid_event


def test_event_contract_validation_minimal():
    evt = {
        "id": "abc",
        "source": "kubernetes",
        "type": "resource_change",
        "timestamp": "2025-01-01T00:00:00Z",
    }
    model = assert_valid_event(evt)
    assert model.id == "abc"
    assert model.source == "kubernetes"

