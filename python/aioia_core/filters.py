"""
Filter type definitions for AIoIA projects.

Provides TypedDict definitions for CRUD filter operations,
compatible with Refine's filter structure.
"""

from __future__ import annotations

from typing import Any, Literal, TypedDict

FilterOperator = Literal[
    "eq",
    "ne",
    "gt",
    "gte",
    "lt",
    "lte",
    "in",
    "contains",
    "startswith",
    "endswith",
    "null",
    "nnull",
]

ConditionalOperator = Literal["or", "and"]


class LogicalFilter(TypedDict, total=False):
    """
    Single field filter condition.

    Example:
        {"field": "status", "operator": "eq", "value": "active"}
    """

    field: str
    operator: FilterOperator
    value: Any


class ConditionalFilter(TypedDict, total=False):
    """
    OR/AND combination filter.

    Example:
        {"operator": "or", "value": [
            {"field": "status", "operator": "eq", "value": "active"},
            {"field": "status", "operator": "eq", "value": "pending"}
        ]}
    """

    operator: ConditionalOperator
    value: list[CrudFilter]


CrudFilter = LogicalFilter | ConditionalFilter
