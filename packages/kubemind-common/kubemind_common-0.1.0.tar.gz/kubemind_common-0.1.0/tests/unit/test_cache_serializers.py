import pytest

from kubemind_common.cache.serializers import JSONSerializer, PickleSerializer, StringSerializer


def test_json_serializer_roundtrip():
    ser = JSONSerializer()
    data = {"a": 1, "b": [2, 3], "c": {"x": "y"}}
    encoded = ser.serialize(data)
    assert isinstance(encoded, (bytes, bytearray))
    decoded = ser.deserialize(encoded)
    assert decoded == data


def test_pickle_serializer_roundtrip():
    ser = PickleSerializer()
    # Use a type not JSON-serializable to emphasize pickle utility
    o = {"a", "b"}
    encoded = ser.serialize(o)
    o2 = ser.deserialize(encoded)
    assert o2 == o


def test_string_serializer_only_strings():
    ser = StringSerializer()
    s = "hello"
    encoded = ser.serialize(s)
    assert ser.deserialize(encoded) == s
    with pytest.raises(ValueError):
        ser.serialize(123)  # type: ignore[arg-type]
