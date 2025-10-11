from ...common import CommonType
from ...common.default_base_model import DefaultBaseModel
from ...properties_attributes_parameters.property import (
    PropertyAssignment,
    PropertyDefinition,
)


class ArtifactDefinition(DefaultBaseModel):
    type: str
    file: str
    repository: str | None = None
    description: str | None = None
    deploy_path: str | None = None
    artifact_version: str | None = None
    checksum: str | None = None
    checksum_algorithm: str | None = None
    properties: dict[str, PropertyAssignment] | None = None


class ArtifactType(CommonType):
    mime_type: str | None
    file_ext: list[str] | None
    properties: dict[str, PropertyDefinition] | None
