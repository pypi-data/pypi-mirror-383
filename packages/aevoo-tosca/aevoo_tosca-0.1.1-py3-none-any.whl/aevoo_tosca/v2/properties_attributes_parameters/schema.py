from __future__ import annotations

from typing import Optional

from .constraint_clause import ConstraintClause
from ..common.default_base_model import DefaultBaseModel


class SchemaDefinition(DefaultBaseModel):
    type: str
    description: Optional[str] = None
    constraints: Optional[list[ConstraintClause]] = None
    key_schema: Optional[SchemaDefinition] = None
    entry_schema: Optional[SchemaDefinition] = None


SchemaDefinition.model_rebuild()
