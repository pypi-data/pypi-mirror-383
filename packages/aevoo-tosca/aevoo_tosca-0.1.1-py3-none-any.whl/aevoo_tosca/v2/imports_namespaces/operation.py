from ..common.default_base_model import DefaultBaseModel
from ..nodes_relationships.artifacts.artifact import ArtifactDefinition
from ..properties_attributes_parameters.parameter import (
    ParameterDefinition,
    ParameterMappingAssignment,
    ParameterValueAssignment,
)


class OperationNotificationImplementationDefinition(DefaultBaseModel):
    primary: ArtifactDefinition | None = None
    dependencies: list[ArtifactDefinition] | None = None
    timeout: int | None = None


class OperationAssignment(DefaultBaseModel):
    implementation: OperationNotificationImplementationDefinition | None = None
    inputs: dict[str, ParameterValueAssignment] | None = None
    outputs: dict[str, ParameterMappingAssignment] | None = None


class OperationDefinition(DefaultBaseModel):
    description: str | None = None
    implementation: OperationNotificationImplementationDefinition | None = None
    inputs: dict[str, ParameterDefinition] | None = None
    outputs: dict[str, ParameterDefinition] | None = None
