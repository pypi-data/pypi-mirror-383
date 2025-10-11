from __future__ import annotations

import re
from pydantic import Field
from typing import Optional, TYPE_CHECKING, Set, Any

from ..common.default_base_model import DefaultBaseModel

try:
    from aevoo_lib.exceptions import NotImplementedExc
    from aevoo_lib.tosca.function.expression_eval import expression_eval
except ModuleNotFoundError as e:
    pass

if TYPE_CHECKING:
    from aevoo_lib.workspace.mapping.ws.instance import Instance
    from aevoo_lib.workspace.topology.version.topology_version import Relations


# TODO: scalar units eval


class ConstraintClause(DefaultBaseModel):
    equal: Optional[Any] = None
    greater_than: Optional[Any] = None
    greater_or_equal: Optional[Any] = None
    in_range: Optional[Any] = None
    length: str | list | dict | None = None
    less_than: Optional[Any] = None
    less_or_equal: Optional[Any] = None
    min_length: str | list | dict | None = None
    max_length: str | list | dict | None = None
    pattern: Optional[Any] | None = None
    schema_: str | None = Field(None, alias="schema")
    valid_values: list[Any] | None = None

    def eval(
        self, value, from_instance: Instance = None, relations__: Relations = None
    ):
        _fields = self.model_dump(exclude_unset=True)
        for key, target in _fields.items():
            if target is not None:
                target = expression_eval(
                    target, instance=from_instance, key=key, relations__=relations__
                )
                _eval_method = constraint_functions.get(key)
                if _eval_method(value, target) is False:
                    return False
        return True

    def find_rs_and_inputs(self, find_rs_and_inputs) -> Set:
        _fields = self.model_dump(exclude_unset=True)
        _rs = set()
        for key, target in _fields.items():
            if target is not None:
                _eval_method = constraint_functions.get(key)
                _rs.update(find_rs_and_inputs(target))
        return _rs


def _eval_equal(value, target):
    return value == target


def _eval_greater_than(value, target):
    return value > target


def _eval_greater_or_equal(value, target):
    return value >= target


def _eval_less_than(value, target):
    return value < target


def _eval_less_or_equal(value, target):
    return value <= target


def _eval_in_range(value, target):
    _low, _up = target
    # return value >= _low and value <= _up
    return _low <= value <= _up


def _eval_valid_values(value, target):
    return value in target


def _eval_length(value, target):
    if isinstance(target, str):
        return len(value) == int(target)
    else:
        return len(value) == len(target)


def _eval_min_length(value, target):
    if isinstance(target, str):
        return len(value) >= int(target)
    else:
        return len(value) >= len(target)


def _eval_max_length(value, target):
    if isinstance(target, str):
        return len(value) <= int(target)
    else:
        return len(value) <= len(target)


def _eval_pattern(value, target):
    return re.fullmatch(target, value) is not None


def _eval_schema(value, target):
    raise NotImplementedExc("schema constraint clause not implemented")


constraint_functions = {
    "equal": _eval_equal,
    "greater_than": _eval_greater_than,
    "greater_or_equal": _eval_greater_or_equal,
    "less_than": _eval_less_than,
    "less_or_equal": _eval_less_or_equal,
    "in_range": _eval_in_range,
    "valid_values": _eval_valid_values,
    "length": _eval_length,
    "min_length": _eval_min_length,
    "max_length": _eval_max_length,
    "pattern": _eval_pattern,
    "schema_": _eval_schema,
}
