
from __future__ import annotations
from typing import Optional
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .event_expression import EventExpression, EventExpressionGuard
from .event_simple_expression import EventSimpleExpression
from .event_grouping_expression import EventGroupingExpression


@JsonMap({})
class EventQueryConfigQueryFilter(BaseModel):
    """EventQueryConfigQueryFilter

    :param expression: expression
    :type expression: EventExpression
    """

    def __init__(self, expression: EventExpression, **kwargs):
        """EventQueryConfigQueryFilter

        :param expression: expression
        :type expression: EventExpression
        """
        self.expression = EventExpressionGuard.return_one_of(expression)
        self._kwargs = kwargs


@JsonMap({"query_filter": "QueryFilter"})
class EventQueryConfig(BaseModel):
    """EventQueryConfig

    :param query_filter: query_filter (optional)
    :type query_filter: Optional[EventQueryConfigQueryFilter]
    """

    def __init__(self, query_filter: Optional[EventQueryConfigQueryFilter] = None, **kwargs):
        """EventQueryConfig

        :param query_filter: query_filter (optional)
        :type query_filter: Optional[EventQueryConfigQueryFilter]
        """
        self.query_filter = self._define_object(
            query_filter, EventQueryConfigQueryFilter
        ) if query_filter is not None else None
        self._kwargs = kwargs
