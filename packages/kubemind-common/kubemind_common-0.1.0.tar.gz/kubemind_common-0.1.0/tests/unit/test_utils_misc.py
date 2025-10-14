from datetime import datetime
from uuid import UUID

import pytest

from kubemind_common.utils.ids import new_id
from kubemind_common.utils.time import utc_now_iso
from kubemind_common.utils.jinja import create_jinja_env


def test_new_id_is_uuid4():
    value = new_id()
    # Should be parseable as UUID
    u = UUID(value, version=4)
    assert str(u) == value


def test_utc_now_iso_timezone():
    s = utc_now_iso()
    # parseable
    dt = datetime.fromisoformat(s)
    # timezone-aware, UTC
    assert dt.tzinfo is not None
    assert s.endswith("+00:00")


def test_create_jinja_env_strict_undefined():
    env = create_jinja_env()
    tmpl = env.from_string("Hello {{ name }}")
    with pytest.raises(Exception):
        tmpl.render({})

