from ...common import CommonType
from ...common.default_base_model import DefaultBaseModel
from ...imports_namespaces.notification import (
    NotificationAssignment,
    NotificationDefinition,
)
from ...imports_namespaces.operation import OperationAssignment, OperationDefinition
from ...properties_attributes_parameters.parameter import (
    ParameterDefinition,
    ParameterValueAssignment,
)


class InterfaceAssignment(DefaultBaseModel):
    inputs: dict[str, ParameterValueAssignment] | None = None
    operations: dict[str, OperationAssignment] | None = None
    notifications: dict[str, NotificationAssignment] | None = None


class InterfaceDefinition(DefaultBaseModel):
    type: str
    description: str | None = None
    inputs: dict[str, ParameterDefinition] | None = None
    operations: dict[str, OperationDefinition] | None = None
    notifications: dict[str, NotificationDefinition] | None = None


class InterfaceType(CommonType):
    inputs: dict[str, ParameterDefinition] | None
    operations: dict[str, OperationDefinition] | None
    notifications: dict[str, NotificationDefinition] | None
    valid_source_types: list[str] | None
