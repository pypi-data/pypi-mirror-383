from __future__ import annotations

from typing import Any

from .attribute_property import AttributePropertyAssignment
from .constraint_clause import ConstraintClause
from .schema import SchemaDefinition
from ..common.default_base_model import DefaultBaseModel

AttributeAssignment = int | bool | str | list | AttributePropertyAssignment


class AttributeDefinition(DefaultBaseModel):
    type: str
    description: None | str = None
    default: Any = None
    status: str
    constraints: None | list[ConstraintClause] = None
    key_schema: None | SchemaDefinition = None
    entry_schema: None | SchemaDefinition = None
    metadata: None | dict[str, str] = None

    def __init__(self, **data):
        status = data.get("status")
        status_allowed = ("supported", "unsupported", "experimental", "deprecated")
        if status is not None and status not in status_allowed:
            raise Exception(
                f"Unsupported status ({status}). Allowed : {status_allowed}"
            )
        super().__init__(**data)
