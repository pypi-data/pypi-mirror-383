from __future__ import annotations

from typing import Any

from .common.default_base_model import DefaultBaseModel
from .imports_namespaces.import_definition import ImportDefinition
from .imports_namespaces.repository import RepositoryDefinition
from .nodes_relationships.artifacts.artifact import ArtifactType
from .nodes_relationships.capabilities_requirements.capability import CapabilityType
from .nodes_relationships.interfaces.interface import InterfaceType
from .nodes_relationships.node import NodeType
from .nodes_relationships.relationship import RelationshipType
from .price import ServicePrice
from .properties_attributes_parameters.data_type import DataType
from .topology_template import TopologyTemplate


class MetadataTemplate(DefaultBaseModel):
    ephemeral: bool = False
    prices: ServicePrice | None = None
    template_author: str | None = None
    template_name: str | None = None
    template_version: str | None = None


class ServiceTemplate(DefaultBaseModel):
    tosca_definitions_version: str = "tosca_2_0"
    profile: str | None = None
    # metadata: dict[str, any] | None = None
    metadata: MetadataTemplate | None = None
    description: str | None = None
    dsl_definitions: Any | None = None
    repositories: dict[str, RepositoryDefinition] | None = None
    imports: list[ImportDefinition] | None = None

    artifact_types: dict[str, ArtifactType] | None = None
    data_types: dict[str, DataType] | None = None
    capability_types: dict[str, CapabilityType] | None = None
    interface_types: dict[str, InterfaceType] | None = None
    relationship_type: dict[str, RelationshipType] | None = None
    node_types: dict[str, NodeType] | None = None
    # group_types: dict[str, GroupType] | None
    # policy_types: dict[str, PolicyType] | None

    topology_template: TopologyTemplate

    template_name: str | None = None
    template_author: str | None = None
    template_version: str | None = None

    # @model_validator(mode="after")
    # def check(cls, v: ServiceTemplate):
    #     if v.metadata is not None:
    #         for k, v in v.metadata.items():
    #             if not isinstance(v, str):
    #                 yaml.load


# ServiceTemplate.model_rebuild()
