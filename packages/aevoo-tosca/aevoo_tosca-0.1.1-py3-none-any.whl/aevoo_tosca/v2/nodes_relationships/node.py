from __future__ import annotations

from pydantic import Field, model_validator

from .artifacts.artifact import ArtifactDefinition
from .capabilities_requirements.capability import (
    CapabilityAssignment,
    CapabilityDefinition,
)
from .capabilities_requirements.node_filter import NodeFilter
from .capabilities_requirements.requirement import RequirementAssignment
from .interfaces.interface import InterfaceAssignment, InterfaceDefinition
from ..common import CommonType
from ..common.default_base_model import DefaultBaseModel
from ..properties_attributes_parameters.attribute import (
    AttributeDefinition,
    AttributeAssignment,
)
from ..properties_attributes_parameters.attribute_property import (
    AttributePropertyAssignment,
    property_model,
    AssignmentFunction,
)
from ..properties_attributes_parameters.property import (
    PropertyAssignment,
    PropertyDefinition,
)

try:
    from aevoo_lib.exceptions import NotImplementedExc
except ModuleNotFoundError as e:
    pass


class MapProperties(DefaultBaseModel):
    properties: dict[str, PropertyAssignment]


class NodeInstanceTemplate(DefaultBaseModel):
    dn: PropertyAssignment
    namespace: str | None = None
    properties: dict[str, PropertyAssignment]
    type: str
    version: str | None = None

    def items(self):
        for k in self.model_dump().keys():
            yield k, getattr(self, k)

    def keys(self):
        return self.model_dump().keys()

    @model_validator(mode="after")
    # !!! never name this method "validate" !!!
    def check(self):
        self.properties = property_model(self.properties)
        return self


class NodeTemplate(DefaultBaseModel):
    attributes: None | dict[str, AttributeAssignment] = None
    count: int | AttributePropertyAssignment = 1
    description: str | None = None
    directives: list[str] | None = Field(None, min_length=1, max_length=1)
    metadata: dict[str, str] | None = None
    # TODO : entry_schema (example: list)
    properties: (
        None
        | dict[str, PropertyAssignment]
        | NodeInstanceTemplate
        | dict[str, PropertyAssignment | dict[str, PropertyAssignment]]
    ) = None
    type: str
    version: str | None = None

    capabilities: dict[str, CapabilityAssignment] | None = None
    requirements: list[dict[str, str | RequirementAssignment]] | None = None
    interfaces: dict[str, dict[str, str | InterfaceAssignment]] | None = None
    artifacts: str | ArtifactDefinition | None = None
    node_filter: NodeFilter | None = None
    copy_: str | None = Field(None, alias="copy")

    @model_validator(mode="after")
    # !!! never name this method "validate" !!!
    def check(self):
        attributes = self.attributes
        capabilities = self.capabilities
        count = self.count
        directives = self.directives
        node_filter = self.node_filter
        properties = self.properties

        if (
            isinstance(count, AssignmentFunction)
            or (isinstance(count, int) and count > 1)
        ) and (directives is None or "substitute" not in directives):
            raise ValueError("Multiple occurrences is only supported for substitution")
        if directives is not None and "select" in directives:
            if not (attributes is None and properties is None):
                raise ValueError(
                    '"select" directive => prohibited : attributes/properties'
                )
            if node_filter is None:
                raise ValueError('"select" directive => mandatory : node_filter')
            if capabilities is not None:
                raise NotImplementedExc("Node capabilities filter not implemented")
        else:
            if node_filter is not None:
                raise ValueError('node_filter :reserved for "select" directive')

        self.properties = property_model(properties)

        return self


class NodeType(CommonType):
    properties: dict[str, PropertyDefinition] | None
    attributes: dict[str, AttributeDefinition] | None
    capabilities: dict[str, CapabilityDefinition] | None
    requirements: list[PropertyDefinition] | None  # TODO List of map ?
    interfaces: dict[str, InterfaceDefinition] | None
    artifacts: dict[str, ArtifactDefinition] | None
