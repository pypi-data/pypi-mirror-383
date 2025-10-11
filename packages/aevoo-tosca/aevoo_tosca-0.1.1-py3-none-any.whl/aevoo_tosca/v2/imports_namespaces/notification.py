from typing import Optional, Dict

from pydantic import BaseModel, Extra

from .operation import OperationNotificationImplementationDefinition
from ..common.default_base_model import DefaultBaseModel
from ..properties_attributes_parameters.parameter import (
    ParameterDefinition,
    ParameterMappingAssignment,
)


class NotificationAssignment(DefaultBaseModel):
    implementation: Optional[OperationNotificationImplementationDefinition] = None
    outputs: Optional[Dict[str, ParameterMappingAssignment]] = None


class NotificationDefinition(DefaultBaseModel):
    description: Optional[str] = None
    implementation: Optional[OperationNotificationImplementationDefinition] = None
    outputs: Optional[Dict[str, ParameterDefinition]] = None
