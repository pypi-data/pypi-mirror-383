from __future__ import annotations

from pydantic import model_validator, Field
from typing_extensions import Annotated

# if TYPE_CHECKING:
from .attribute_mapping import AttributeMapping
from .capability_mapping import CapabilityMapping
from .interface_mapping import InterfaceMapping
from .property_mapping import PropertyMapping
from .requirement_mapping import RequirementMapping
from ..common.default_base_model import DefaultBaseModel
from ..nodes_relationships.capabilities_requirements.node_filter import NodeFilter


class SubstitutionMapping(DefaultBaseModel):
    node_type: str
    substitution_filter: NodeFilter | None = None
    attributes: dict[str, AttributeMapping] | None = None
    properties: dict[str, PropertyMapping] | None = None
    # TODO max_length = ? TopologyVersion._loading_capabilities
    capabilities: dict[
        str, Annotated[list[str], Field(min_length=2, max_length=2)] | CapabilityMapping
    ] | None = None
    requirements: dict[
        str,
        Annotated[list[str], Field(min_length=2, max_length=2)] | RequirementMapping,
    ] | None = None
    interfaces: dict[str, InterfaceMapping] | None = None

    @model_validator(mode="before")
    @classmethod
    def check(cls, values):
        sf = values.get("substitution_filter")
        if not (sf is None or sf.get("capabilities") is None):
            raise ValueError("capabilities in substitution_filter is not implemented")
        return values
