from kubemind_common.api.pagination import parse_pagination, paginate
from kubemind_common.contracts.common import Page


def test_parse_pagination_bounds():
    assert parse_pagination(None, None) == (1, 50)
    assert parse_pagination(0, -1) == (1, 1)
    assert parse_pagination(10, 9999) == (10, 500)


def test_paginate_model():
    page = paginate([1, 2], total=10, page=2, size=2)
    assert isinstance(page, Page)
    assert page.items == [1, 2]
    assert page.page == 2
    assert page.size == 2

