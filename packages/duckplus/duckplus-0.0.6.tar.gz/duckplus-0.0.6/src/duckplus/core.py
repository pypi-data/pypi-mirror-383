"""Public relational surface for Duck+."""

from __future__ import annotations

from ._core_specs import (
    AsofOrder,
    AsofSpec,
    ExpressionPredicate,
    JoinPredicate,
    JoinProjection,
    JoinSpec,
    PartitionSpec,
)
from .aggregates import AggregateArgument, AggregateExpression, AggregateOrder
from .filters import (
    FilterExpression,
    col,
    column,
    equals,
    greater_than,
    greater_than_or_equal,
    less_than,
    less_than_or_equal,
    not_equals,
)
from .duckrel import DuckRel

__all__ = [
    "AsofOrder",
    "AsofSpec",
    "ColumnPredicate",
    "AggregateArgument",
    "AggregateExpression",
    "AggregateOrder",
    "FilterExpression",
    "DuckRel",
    "ExpressionPredicate",
    "JoinPredicate",
    "JoinProjection",
    "JoinSpec",
    "PartitionSpec",
    "col",
    "column",
    "equals",
    "greater_than",
    "greater_than_or_equal",
    "less_than",
    "less_than_or_equal",
    "not_equals",
]

