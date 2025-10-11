from pydantic import Field

from ...common import CommonType
from ...common.default_base_model import DefaultBaseModel
from ...properties_attributes_parameters.attribute import (
    AttributeAssignment,
    AttributeDefinition,
)
from ...properties_attributes_parameters.property import (
    PropertyAssignment,
    PropertyDefinition,
)


class CapabilityAssignment(DefaultBaseModel):
    attributes: dict[str, AttributeAssignment] | None = None
    properties: dict[str, PropertyAssignment] | None = None
    count: int = Field(default=1)


class CapabilityDefinition(DefaultBaseModel):
    type: str
    description: str | None = None
    attributes: dict[
        str, AttributeAssignment
    ] | None = None  # TODO AttributeRefinement ?
    properties: dict[str, PropertyAssignment] | None = None  # TODO PropertyRefinement ?
    valid_source_types: list[str] | None = None
    count_range: list[int | str] = Field(
        default=[1, "UNBOUNDED"], min_length=2, max_length=2
    )


class CapabilityType(CommonType):
    attributes: dict[str, AttributeDefinition] | None
    properties: dict[str, PropertyDefinition] | None
    valid_source_types: list[str] | None
