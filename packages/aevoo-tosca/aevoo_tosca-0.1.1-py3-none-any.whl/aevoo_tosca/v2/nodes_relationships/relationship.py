from __future__ import annotations

from pydantic import Field

from .interfaces.interface import InterfaceAssignment, InterfaceDefinition
from ..common import CommonType
from ..common.default_base_model import DefaultBaseModel
from ..properties_attributes_parameters.attribute import (
    AttributeAssignment,
    AttributeDefinition,
)
from ..properties_attributes_parameters.property import (
    PropertyAssignment,
    PropertyDefinition,
)


class RelationshipTemplate(DefaultBaseModel):
    type: str
    description: str | None = None
    metadata: dict[str, str] | None = None
    attributes: dict[str, AttributeAssignment] = Field(default_factory=dict)
    properties: dict[str, PropertyAssignment] = Field(default_factory=dict)
    interfaces: dict[str, dict[str, str | InterfaceAssignment]] | None = None
    copy_: str | None = Field(None, alias="copy")


class RelationshipType(CommonType):
    properties: dict[str, PropertyDefinition] | None
    atttributes: dict[str, AttributeDefinition] | None
    interfaces: dict[str, InterfaceDefinition] | None
    valid_target_types: list[str] | None
