from __future__ import annotations

from .attribute import AttributeAssignment
from .property import PropertyDefinition
from ..common.default_base_model import DefaultBaseModel
from ..price import Prices


class ParameterDefinition(PropertyDefinition):
    pass
    # mapping: Optional[AttributeSelectionFormat]


class ParameterValueAssignment(DefaultBaseModel):
    pass


class ParameterMappingAssignment(DefaultBaseModel):
    pass


class MetadataInput(DefaultBaseModel):
    prices: Prices | None = None


class InputDefinition(ParameterDefinition):
    cid: str | None = None
    metadata: MetadataInput | None = None
    required: bool = None


class OutputDefinition(ParameterDefinition):
    value: AttributeAssignment
