"""SQLAlchemy query helpers and filter builders."""
from __future__ import annotations

from typing import Any, Dict, List, Sequence

from sqlalchemy import Select, asc, desc, or_
from sqlalchemy.orm import Query


def apply_filters(
    query: Select | Query,
    model: type,
    filters: Dict[str, Any]
) -> Select | Query:
    """Apply filters to SQLAlchemy query.

    Args:
        query: SQLAlchemy query or select statement
        model: SQLAlchemy model class
        filters: Dictionary of column_name -> value

    Returns:
        Filtered query

    Example:
        from sqlalchemy import select
        from kubemind_common.db.query import apply_filters

        query = select(User)
        filters = {"is_active": True, "role": "admin"}
        query = apply_filters(query, User, filters)
        results = await session.execute(query)
    """
    for column_name, value in filters.items():
        if not hasattr(model, column_name):
            continue

        column = getattr(model, column_name)

        if value is None:
            query = query.where(column.is_(None))
        elif isinstance(value, (list, tuple)):
            # IN filter
            query = query.where(column.in_(value))
        else:
            query = query.where(column == value)

    return query


def apply_sorting(
    query: Select | Query,
    model: type,
    sort_by: str | None = None,
    sort_order: str = "asc"
) -> Select | Query:
    """Apply sorting to SQLAlchemy query.

    Args:
        query: SQLAlchemy query or select statement
        model: SQLAlchemy model class
        sort_by: Column name to sort by
        sort_order: "asc" or "desc" (default: "asc")

    Returns:
        Sorted query

    Example:
        query = select(User)
        query = apply_sorting(query, User, sort_by="created_at", sort_order="desc")
    """
    if not sort_by or not hasattr(model, sort_by):
        return query

    column = getattr(model, sort_by)

    if sort_order.lower() == "desc":
        query = query.order_by(desc(column))
    else:
        query = query.order_by(asc(column))

    return query


def apply_pagination(
    query: Select | Query,
    page: int = 1,
    page_size: int = 50
) -> Select | Query:
    """Apply pagination to SQLAlchemy query.

    Args:
        query: SQLAlchemy query or select statement
        page: Page number (1-indexed)
        page_size: Number of items per page

    Returns:
        Paginated query

    Example:
        query = select(User)
        query = apply_pagination(query, page=2, page_size=20)
        results = await session.execute(query)
    """
    offset = (page - 1) * page_size
    return query.limit(page_size).offset(offset)


def build_search_filter(
    model: type,
    search_columns: Sequence[str],
    search_term: str
) -> Any:
    """Build OR filter for full-text search across multiple columns.

    Args:
        model: SQLAlchemy model class
        search_columns: List of column names to search
        search_term: Search term

    Returns:
        SQLAlchemy OR filter expression

    Example:
        from sqlalchemy import select
        from kubemind_common.db.query import build_search_filter

        search_filter = build_search_filter(
            User,
            ["name", "email", "username"],
            "john"
        )
        query = select(User).where(search_filter)
    """
    if not search_term:
        return None

    search_pattern = f"%{search_term}%"
    conditions = []

    for column_name in search_columns:
        if hasattr(model, column_name):
            column = getattr(model, column_name)
            conditions.append(column.ilike(search_pattern))

    if not conditions:
        return None

    return or_(*conditions)


def build_query(
    model: type,
    filters: Dict[str, Any] | None = None,
    search_columns: Sequence[str] | None = None,
    search_term: str | None = None,
    sort_by: str | None = None,
    sort_order: str = "asc",
    page: int | None = None,
    page_size: int = 50
) -> Select:
    """Build complete SQLAlchemy query with filters, search, sorting, and pagination.

    Args:
        model: SQLAlchemy model class
        filters: Dictionary of column_name -> value
        search_columns: List of columns for full-text search
        search_term: Search term
        sort_by: Column name to sort by
        sort_order: "asc" or "desc"
        page: Page number (1-indexed)
        page_size: Items per page

    Returns:
        Complete SQLAlchemy select statement

    Example:
        from kubemind_common.db.query import build_query

        query = build_query(
            User,
            filters={"is_active": True},
            search_columns=["name", "email"],
            search_term="john",
            sort_by="created_at",
            sort_order="desc",
            page=1,
            page_size=20
        )
        results = await session.execute(query)
    """
    from sqlalchemy import select

    query = select(model)

    # Apply filters
    if filters:
        query = apply_filters(query, model, filters)

    # Apply search
    if search_columns and search_term:
        search_filter = build_search_filter(model, search_columns, search_term)
        if search_filter is not None:
            query = query.where(search_filter)

    # Apply sorting
    query = apply_sorting(query, model, sort_by, sort_order)

    # Apply pagination
    if page is not None:
        query = apply_pagination(query, page, page_size)

    return query


class QueryBuilder:
    """Fluent query builder for SQLAlchemy.

    Usage:
        from kubemind_common.db.query import QueryBuilder

        builder = QueryBuilder(User)
        query = (builder
            .filter(is_active=True, role="admin")
            .search(["name", "email"], "john")
            .sort("created_at", "desc")
            .paginate(page=1, size=20)
            .build())

        results = await session.execute(query)
    """

    def __init__(self, model: type):
        """Initialize query builder.

        Args:
            model: SQLAlchemy model class
        """
        from sqlalchemy import select

        self.model = model
        self._query = select(model)
        self._filters: Dict[str, Any] = {}
        self._search_columns: List[str] = []
        self._search_term: str | None = None
        self._sort_by: str | None = None
        self._sort_order: str = "asc"
        self._page: int | None = None
        self._page_size: int = 50

    def filter(self, **kwargs: Any) -> QueryBuilder:
        """Add filters.

        Args:
            **kwargs: Column filters

        Returns:
            Self for chaining
        """
        self._filters.update(kwargs)
        return self

    def search(self, columns: Sequence[str], term: str) -> QueryBuilder:
        """Add search filter.

        Args:
            columns: Columns to search
            term: Search term

        Returns:
            Self for chaining
        """
        self._search_columns = list(columns)
        self._search_term = term
        return self

    def sort(self, column: str, order: str = "asc") -> QueryBuilder:
        """Add sorting.

        Args:
            column: Column name
            order: "asc" or "desc"

        Returns:
            Self for chaining
        """
        self._sort_by = column
        self._sort_order = order
        return self

    def paginate(self, page: int, size: int = 50) -> QueryBuilder:
        """Add pagination.

        Args:
            page: Page number (1-indexed)
            size: Page size

        Returns:
            Self for chaining
        """
        self._page = page
        self._page_size = size
        return self

    def build(self) -> Select:
        """Build final query.

        Returns:
            SQLAlchemy select statement
        """
        return build_query(
            self.model,
            filters=self._filters or None,
            search_columns=self._search_columns or None,
            search_term=self._search_term,
            sort_by=self._sort_by,
            sort_order=self._sort_order,
            page=self._page,
            page_size=self._page_size
        )

    def reset(self) -> QueryBuilder:
        """Reset all filters and options.

        Returns:
            Self for chaining
        """
        from sqlalchemy import select

        self._query = select(self.model)
        self._filters = {}
        self._search_columns = []
        self._search_term = None
        self._sort_by = None
        self._sort_order = "asc"
        self._page = None
        self._page_size = 50
        return self
