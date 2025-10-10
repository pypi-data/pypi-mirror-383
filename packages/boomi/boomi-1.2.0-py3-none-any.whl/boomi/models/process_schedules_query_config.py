
from __future__ import annotations
from typing import Optional
from .utils.json_map import JsonMap
from .utils.base_model import BaseModel
from .process_schedules_expression import (
    ProcessSchedulesExpression,
    ProcessSchedulesExpressionGuard,
)
from .process_schedules_simple_expression import ProcessSchedulesSimpleExpression
from .process_schedules_grouping_expression import ProcessSchedulesGroupingExpression


@JsonMap({})
class ProcessSchedulesQueryConfigQueryFilter(BaseModel):
    """ProcessSchedulesQueryConfigQueryFilter

    :param expression: expression
    :type expression: ProcessSchedulesExpression
    """

    def __init__(self, expression: ProcessSchedulesExpression, **kwargs):
        """ProcessSchedulesQueryConfigQueryFilter

        :param expression: expression
        :type expression: ProcessSchedulesExpression
        """
        self.expression = ProcessSchedulesExpressionGuard.return_one_of(expression)
        self._kwargs = kwargs


@JsonMap({"query_filter": "QueryFilter"})
class ProcessSchedulesQueryConfig(BaseModel):
    """ProcessSchedulesQueryConfig

    :param query_filter: query_filter (optional)
    :type query_filter: Optional[ProcessSchedulesQueryConfigQueryFilter]
    """

    def __init__(self, query_filter: Optional[ProcessSchedulesQueryConfigQueryFilter] = None, **kwargs):
        """ProcessSchedulesQueryConfig

        :param query_filter: query_filter (optional)
        :type query_filter: Optional[ProcessSchedulesQueryConfigQueryFilter]
        """
        self.query_filter = self._define_object(
            query_filter, ProcessSchedulesQueryConfigQueryFilter
        ) if query_filter is not None else None
        self._kwargs = kwargs
