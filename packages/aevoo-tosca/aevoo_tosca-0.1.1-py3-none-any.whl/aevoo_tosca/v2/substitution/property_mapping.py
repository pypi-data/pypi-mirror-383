from pydantic import Field

from ..common.default_base_model import DefaultBaseModel
from ..properties_attributes_parameters.attribute import AttributeAssignment
from ..properties_attributes_parameters.property import PropertyAssignment


class PropertyMapping(DefaultBaseModel):
    mapping: list[str] | None = Field(min_length=2, max_length=2)
    attributes: dict[str, AttributeAssignment] | None = None
    properties: dict[str, PropertyAssignment] | None = None
    # value: Optional # Deprecated
