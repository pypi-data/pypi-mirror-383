from pydantic import Field

from .node_filter import NodeFilter
from ..interfaces.interface import InterfaceAssignment
from ...common.default_base_model import DefaultBaseModel
from ...properties_attributes_parameters.property import PropertyAssignment


class RequirementAssignment(DefaultBaseModel):
    capability: str | None = None
    node: str | None = None
    relationship: str | None = None
    node_filter: NodeFilter | None = None
    count: int = Field(default=1)

    type: str | None = None
    properties: None | str | dict[str, PropertyAssignment] = None
    interfaces: dict[str, dict[str, str | InterfaceAssignment]] | None = None

    # def __post_init__(self):
    #     if len(self.occurrences) == 0:
    #         self.occurrences = [1, 1]


class RequirementDefinition(DefaultBaseModel):
    capability: str
    node: str | None = None  # Conditional
    relationship: str | None = None
    node_filter: NodeFilter | None = None
    count_range: list[int | str] = Field(default=[1, 1], min_length=2, max_length=2)
    #
    type: str | None = None
    interfaces: None | dict[str, InterfaceAssignment] = None
